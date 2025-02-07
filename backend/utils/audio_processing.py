import os
from typing import Tuple, Optional
import librosa
import soundfile as sf
import numpy as np

class AudioProcessor:
    @staticmethod
    def validate_audio(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if the audio file is in a supported format and not corrupted.
        Args:
            file_path: Path to the audio file
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            y, sr = librosa.load(file_path, duration=1)  # Load just first second
            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def normalize_audio(file_path: str, target_sr: int = 16000) -> str:
        """
        Normalize audio file to consistent format.
        Args:
            file_path: Path to the audio file
            target_sr: Target sample rate
        Returns:
            Path to normalized audio file
        """
        # Load audio
        y, sr = librosa.load(file_path, sr=None)
        
        # Resample if necessary
        if sr != target_sr:
            y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
        
        # Convert to mono if stereo
        if len(y.shape) > 1:
            y = librosa.to_mono(y)
        
        # Normalize amplitude
        y = librosa.util.normalize(y)
        
        # Save normalized audio
        output_path = f"{os.path.splitext(file_path)[0]}_normalized.wav"
        sf.write(output_path, y, target_sr)
        
        return output_path

    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        """
        Get the duration of an audio file in seconds.
        Args:
            file_path: Path to the audio file
        Returns:
            Duration in seconds
        """
        y, sr = librosa.load(file_path)
        return librosa.get_duration(y=y, sr=sr)

    @staticmethod
    def split_audio(
        file_path: str,
        segment_duration: float = 30.0
    ) -> list[str]:
        """
        Split long audio files into smaller segments.
        Args:
            file_path: Path to the audio file
            segment_duration: Duration of each segment in seconds
        Returns:
            List of paths to the segment files
        """
        y, sr = librosa.load(file_path)
        duration = librosa.get_duration(y=y, sr=sr)
        
        if duration <= segment_duration:
            return [file_path]
        
        segment_samples = int(segment_duration * sr)
        segments = []
        
        for i, start in enumerate(range(0, len(y), segment_samples)):
            segment = y[start:start + segment_samples]
            if len(segment) < segment_samples / 2:  # Skip very short segments
                continue
                
            segment_path = f"{os.path.splitext(file_path)[0]}_segment_{i}.wav"
            sf.write(segment_path, segment, sr)
            segments.append(segment_path)
            
        return segments 