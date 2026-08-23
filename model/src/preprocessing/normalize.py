"""
Audio normalization module supporting peak, RMS, and fold-local reference statistics.
Strictly adheres to Constraint RC-08 (Fold-Local Preprocessing and Fitting).
"""

from typing import Dict, Any, List, Optional
import numpy as np


def compute_fold_normalization_stats(
    train_audios: List[np.ndarray],
    fold_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fits normalization statistics exclusively on the training split/fold.
    Computes mean RMS level, mean peak amplitude, and global reference scale.
    """
    if not train_audios:
        return {"fold_id": fold_id, "ref_rms": 0.10, "ref_peak": 0.95}
        
    rms_values = []
    peak_values = []
    
    for audio in train_audios:
        if len(audio) == 0:
            continue
        rms = np.sqrt(np.mean(audio ** 2) + 1e-12)
        peak = np.max(np.abs(audio)) + 1e-12
        rms_values.append(rms)
        peak_values.append(peak)
        
    mean_rms = float(np.mean(rms_values)) if rms_values else 0.10
    mean_peak = float(np.mean(peak_values)) if peak_values else 0.95
    
    return {
        "fold_id": fold_id,
        "ref_rms": mean_rms,
        "ref_peak": mean_peak,
        "fitted_sample_count": len(train_audios)
    }


def normalize_loudness(
    audio: np.ndarray,
    method: str = "peak",
    target_peak: float = 0.95,
    target_rms: float = 0.10,
    fold_stats: Optional[Dict[str, Any]] = None
) -> np.ndarray:
    """
    Normalizes audio loudness according to the specified method.
    
    Args:
        audio: 1D mono float32 array.
        method: "peak" | "rms" | "fold_stat".
        target_peak: Target peak amplitude (e.g. 0.95 = -0.45 dBFS).
        target_rms: Target RMS level for RMS normalization.
        fold_stats: Optional fold-fitted statistics dictionary (RC-08).
        
    Returns:
        Normalized float32 numpy array.
    """
    if len(audio) == 0:
        return audio.astype(np.float32)
        
    audio = audio.astype(np.float32)
    peak = np.max(np.abs(audio))
    
    if peak <= 1e-8:
        # Silent audio
        return audio
        
    if method == "peak":
        scale = target_peak / peak
        normalized = audio * scale
        return np.clip(normalized, -1.0, 1.0).astype(np.float32)
        
    elif method == "rms":
        current_rms = np.sqrt(np.mean(audio ** 2) + 1e-12)
        scale = target_rms / current_rms
        normalized = audio * scale
        # Peak limit to prevent hard clipping distortion
        peak_after = np.max(np.abs(normalized))
        if peak_after > 0.99:
            normalized = normalized * (0.95 / peak_after)
        return np.clip(normalized, -1.0, 1.0).astype(np.float32)
        
    elif method == "fold_stat" and fold_stats is not None:
        # Scale relative to training fold reference RMS
        ref_rms = fold_stats.get("ref_rms", 0.10)
        current_rms = np.sqrt(np.mean(audio ** 2) + 1e-12)
        scale = ref_rms / max(current_rms, 1e-6)
        normalized = audio * scale
        peak_after = np.max(np.abs(normalized))
        if peak_after > 0.99:
            normalized = normalized * (0.95 / peak_after)
        return np.clip(normalized, -1.0, 1.0).astype(np.float32)
        
    else:
        # Fallback to standard peak normalization
        scale = target_peak / peak
        normalized = audio * scale
        return np.clip(normalized, -1.0, 1.0).astype(np.float32)
