import torch
import torchaudio
from transformers import AutoModel, AutoFeatureExtractor
import numpy as np
from typing import Union, List, Optional

class CLMRModel:
    def __init__(self, model_name: str = "m-a-p/CLMR-v2"):
        """
        Initialize the CLMR model for music representation learning.
        Args:
            model_name: The name of the model to load from HuggingFace
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
        self.model.eval()

    @torch.no_grad()
    def extract_features(self, audio_path: str) -> np.ndarray:
        """
        Extract features from an audio file using the CLMR model.
        Args:
            audio_path: Path to the audio file
        Returns:
            numpy array of extracted features
        """
        # Load and resample audio
        waveform, sample_rate = torchaudio.load(audio_path)
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)

        # Convert to mono if stereo
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        # Extract features using the feature extractor
        inputs = self.feature_extractor(
            waveform, 
            sampling_rate=16000, 
            return_tensors="pt"
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Get model outputs
        outputs = self.model(**inputs)
        
        # Use mean pooling to get a single vector representation
        embeddings = outputs.last_hidden_state.mean(dim=1)
        
        return embeddings.cpu().numpy()

    def get_batch_features(self, audio_paths: List[str]) -> np.ndarray:
        """
        Extract features from multiple audio files.
        Args:
            audio_paths: List of paths to audio files
        Returns:
            numpy array of extracted features for all files
        """
        features = []
        for audio_path in audio_paths:
            try:
                feature = self.extract_features(audio_path)
                features.append(feature)
            except Exception as e:
                print(f"Error processing {audio_path}: {str(e)}")
                continue
        return np.vstack(features) 