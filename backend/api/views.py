from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from ml.feature_extractor import AudioFeatureExtractor
from storage.pinecone_client import PineconeClient
from utils.audio_processing import AudioProcessor
import os
import uuid
import datetime

class SongViewSet(viewsets.ViewSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feature_extractor = AudioFeatureExtractor()
        self.pinecone_client = PineconeClient(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENV,
            index_name=settings.PINECONE_INDEX
        )
        self.audio_processor = AudioProcessor()

    @action(detail=False, methods=['POST'])
    def upload(self, request):
        """Upload and process a song"""
        try:
            audio_file = request.FILES.get('audio')
            if not audio_file:
                return Response({'error': 'No audio file provided'}, status=status.HTTP_400_BAD_REQUEST)

            temp_path = f"/tmp/audio_files/{uuid.uuid4()}{os.path.splitext(audio_file.name)[1]}"
            with open(temp_path, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            # Process audio
            is_valid, error = self.audio_processor.validate_audio(temp_path)
            if not is_valid:
                return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

            normalized_path = self.audio_processor.normalize_audio(temp_path)
            features = self.feature_extractor.extract_audio_features(normalized_path)

            # Store in Pinecone
            vector_id = str(uuid.uuid4())
            metadata = {
                'id': vector_id,
                'title': request.data.get('title', ''),
                'artist': request.data.get('artist', ''),
                'created_at': datetime.datetime.now().isoformat()
            }

            self.pinecone_client.upsert_vectors(
                vectors=[features['embedding']],
                metadata=[metadata]
            )

            return Response(metadata, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @action(detail=False, methods=['POST'])
    def find_similar(self, request):
        """Find similar songs"""
        try:
            song_id = request.data.get('song_id')
            if not song_id:
                return Response({'error': 'No song ID provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            vector = self.pinecone_client.fetch_vector(song_id)
            if not vector:
                return Response({'error': 'Song not found'}, status=status.HTTP_404_NOT_FOUND)
            
            similar_songs = self.pinecone_client.search_similar(
                query_vector=vector,
                top_k=int(request.query_params.get('limit', 10))
            )
            
            return Response(similar_songs, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 