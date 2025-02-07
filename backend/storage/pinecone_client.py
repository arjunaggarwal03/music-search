import pinecone
from typing import List, Dict, Any, Optional
import numpy as np

class PineconeClient:
    def __init__(self, 
                 api_key: str,
                 environment: str,
                 index_name: str,
                 dimension: int = 2048):  # CLMR embedding dimension
        """
        Initialize Pinecone client and index.
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
            index_name: Name of the Pinecone index
            dimension: Dimension of the vectors to be stored
        """
        pinecone.init(api_key=api_key, environment=environment)
        
        # Create index if it doesn't exist
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=dimension,
                metric='cosine'
            )
            
        self.index = pinecone.Index(index_name)
    
    def upsert_vectors(self, 
                      vectors: List[np.ndarray], 
                      metadata: List[Dict[str, Any]]) -> None:
        """
        Upload vectors and their metadata to Pinecone.
        Args:
            vectors: List of feature vectors
            metadata: List of metadata dictionaries for each vector
        """
        vectors_with_ids = [
            (str(i), vector.tolist(), meta)
            for i, (vector, meta) in enumerate(zip(vectors, metadata))
        ]
        
        self.index.upsert(vectors=vectors_with_ids)
    
    def search_similar(self, 
                      query_vector: np.ndarray, 
                      top_k: int = 10,
                      filter: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar vectors in the index.
        Args:
            query_vector: Query vector to find similar items
            top_k: Number of similar items to return
            filter: Optional filter criteria
        Returns:
            List of similar items with their metadata
        """
        results = self.index.query(
            vector=query_vector.tolist(),
            top_k=top_k,
            include_metadata=True,
            filter=filter
        )
        
        return results['matches'] 