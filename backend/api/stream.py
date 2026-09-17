from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import tempfile
import os
import wave
import uuid
import pandas as pd
from typing import List

from backend.inference.predictor_service import predict
from backend.core.config import settings

# In order to properly test/aggregate, we import the model's logic
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from model.src.evaluation.speaker_aggregation import aggregate_windows_to_session

router = APIRouter()

# 16kHz, 16-bit mono PCM -> 32000 bytes per second
# Contract min_duration = 2.0s -> 64000 bytes
SAMPLE_RATE = 16000
BYTES_PER_SAMPLE = 2
MIN_DURATION_SEC = 2.0
WINDOW_BYTES = int(SAMPLE_RATE * BYTES_PER_SAMPLE * MIN_DURATION_SEC)
MAX_WINDOWS = 50  # Cap rolling window to prevent unbounded memory

def save_pcm_to_wav(pcm_data: bytes, filepath: str):
    """Utility to wrap raw PCM chunks into a readable WAV file for the predictor."""
    with wave.open(filepath, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(BYTES_PER_SAMPLE)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm_data)

@router.websocket("")
async def stream_audio(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    
    buffer = bytearray()
    window_records = []
    
    try:
        while True:
            data = await websocket.receive_bytes()
            buffer.extend(data)
            
            # Process in windows of MIN_DURATION_SEC
            while len(buffer) >= WINDOW_BYTES:
                # Extract one window
                window_data = buffer[:WINDOW_BYTES]
                # Keep overlap or disjoint? The prompt doesn't specify overlap, so disjoint is fine, 
                # or just advance buffer. Let's advance by WINDOW_BYTES (disjoint).
                buffer = buffer[WINDOW_BYTES:]
                
                temp_wav_path = tempfile.mktemp(suffix=".wav")
                try:
                    save_pcm_to_wav(window_data, temp_wav_path)
                    
                    # Run inference on the window
                    pred_res = predict(temp_wav_path, return_explanations=False)
                    
                    # Store window results
                    window_records.append({
                        "session_id": session_id,
                        "prob": pred_res.prediction.pd_probability_calibrated,
                        "quality": pred_res.prediction.audio_quality_score,
                        "uncertainty": 1.0 - pred_res.prediction.confidence_score
                    })
                    
                    # Cap memory (discard oldest low-quality data first)
                    if len(window_records) > MAX_WINDOWS:
                        # Find the lowest quality record among the oldest half of the buffer
                        oldest_half = window_records[:len(window_records)//2]
                        lowest_quality_idx = min(range(len(oldest_half)), key=lambda i: oldest_half[i]['quality'])
                        window_records.pop(lowest_quality_idx)
                        
                    # Aggregate
                    df = pd.DataFrame(window_records)
                    
                    # Config for aggregation
                    agg_config = {
                        "aggregation": {
                            "window_to_session": "quality_weighted_mean",
                            "quality_temperature": 1.0
                        }
                    }
                    
                    agg_df = aggregate_windows_to_session(df, agg_config)
                    aggregated_prob = float(agg_df.iloc[0]['prob'])
                    
                    # Emit running prediction
                    await websocket.send_json({
                        "session_id": session_id,
                        "windows_processed": len(window_records),
                        "running_prediction": aggregated_prob,
                        "last_window_quality": pred_res.prediction.audio_quality_score,
                        "status": "accumulating"
                    })
                    
                finally:
                    if os.path.exists(temp_wav_path):
                        os.remove(temp_wav_path)
                        
    except WebSocketDisconnect:
        # Cleanup automatically handled by connection drop, buffer goes out of scope
        pass
    except Exception as e:
        # Log and close on internal error
        await websocket.close(code=1011, reason=str(e))
