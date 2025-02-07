from typing import Dict, Any, Optional
import numpy as np
from pathlib import Path
import librosa
from .clmr_model import CLMRModel

class AudioFeatureExtractor:
    def __init__(self, model: Optional[CLMRModel] = None):
        """
        Initialize the feature extractor with a CLMR model instance.
        Args:
            model: Optional CLMRModel instance
        """
        self.model = model if model else CLMRModel()
        
    def extract_audio_features(self, 
                             audio_path: str, 
                             extract_additional: bool = False) -> Dict[str, Any]:
        """
        Extract both CLMR embeddings and additional audio features if requested.
        Args:
            audio_path: Path to the audio file
            extract_additional: Whether to extract additional audio features
        Returns:
            Dictionary containing embeddings and additional features
        """
        features = {
            'embedding': self.model.extract_features(audio_path).flatten()
        }
        
        if extract_additional:
            additional_features = self._extract_additional_features(audio_path)
            features.update(additional_features)
            
        return features
    
    def _extract_additional_features(self, audio_path: str) -> Dict[str, Any]:
        """
        Extract additional audio features using librosa.
        Args:
            audio_path: Path to the audio file
        Returns:
            Dictionary of additional features
        """
        y, sr = librosa.load(audio_path)
        
        # Extract various audio features
        features = {
            'tempo': librosa.beat.tempo(y=y, sr=sr)[0],
            'spectral_centroid': np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)),
            'spectral_bandwidth': np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)),
            'spectral_rolloff': np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)),
            'zero_crossing_rate': np.mean(librosa.feature.zero_crossing_rate(y=y)),
            'rms_energy': np.mean(librosa.feature.rms(y=y))
        }
        
        return features 