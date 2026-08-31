"""
Reference Video Analyzer.
Extracts shot boundaries, color palettes, and motion beats from a reference clip
to generate a baseline schema/target for the AI Editor.
"""

from typing import Dict, Any, List
import os
import cv2
import numpy as np
import subprocess
from typing import Dict, Any, List

class ReferenceAnalyzer:
    
    @classmethod
    def analyze_audio_loudness(cls, path: str, threshold: float = 0.04, chunk_duration: float = 1/30.0) -> Dict[str, Any]:
        """
        Inspired by Auto-Editor: extracts audio, measures peak loudness per chunk (frame),
        and identifies 'loud' vs 'silent' regions for automated cutting.
        """
        import tempfile
        if not os.path.exists(path):
            return {"error": f"Media not found: {path}"}
            
        temp_wav = os.path.join(tempfile.gettempdir(), "temp_audio_analyze.wav")
        
        # 1. Extract audio to 16-bit PCM WAV using FFmpeg
        cmd = [
            "ffmpeg", "-i", path, "-vn", "-acodec", "pcm_s16le", 
            "-ar", "44100", "-ac", "1", "-y", temp_wav
        ]
        
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            import wave
            with wave.open(temp_wav, 'rb') as wf:
                framerate = wf.getframerate()
                nframes = wf.getnframes()
                audio_data = np.frombuffer(wf.readframes(nframes), dtype=np.int16)
        except Exception as e:
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            return {"error": f"Audio extraction failed: {e}"}
            
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
            
        # 2. Measure Loudness per Chunk (Auto-Editor maxAbs algorithm)
        samples_per_chunk = int(framerate * chunk_duration)
        loudness_array = []
        
        for i in range(0, len(audio_data), samples_per_chunk):
            chunk = audio_data[i:i + samples_per_chunk]
            if len(chunk) == 0:
                break
            # Normalize peak to 0.0 - 1.0 (16-bit max is 32767)
            peak = np.max(np.abs(chunk)) / 32767.0
            loudness_array.append(peak)
            
        # 3. Detect cuts based on threshold
        is_loud = np.array(loudness_array) >= threshold
        
        # Group into regions
        regions = []
        in_loud = False
        start_idx = 0
        
        for idx, loud in enumerate(is_loud):
            if loud and not in_loud:
                in_loud = True
                start_idx = idx
            elif not loud and in_loud:
                in_loud = False
                regions.append({
                    "start": start_idx * chunk_duration,
                    "end": idx * chunk_duration,
                    "type": "loud",
                    "duration": (idx - start_idx) * chunk_duration
                })
                
        if in_loud:
             regions.append({
                "start": start_idx * chunk_duration,
                "end": len(is_loud) * chunk_duration,
                "type": "loud",
                "duration": (len(is_loud) - start_idx) * chunk_duration
            })
            
        return {
            "source_path": path,
            "threshold": threshold,
            "loud_regions": regions,
            "total_duration": len(loudness_array) * chunk_duration,
            "loudness_array_preview": [float(x) for x in loudness_array[:10]] # just preview
        }
    
    @classmethod
    def analyze_video(cls, path: str) -> Dict[str, Any]:
        """
        Analyzes a reference video and extracts shot boundaries using OpenCV frame differencing.
        """
        if not os.path.exists(path):
            return {"error": f"Reference video not found: {path}"}
            
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        shots = []
        motion_beats = []
        
        prev_hist = None
        shot_start_time = 0.0
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Convert to HSV and calculate histogram for Hue and Saturation
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
            cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            
            if prev_hist is not None:
                # Compare histograms using correlation
                diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                
                # If correlation is low, a hard cut or significant transition occurred
                if diff < 0.85:
                    current_time = frame_idx / fps
                    # Record the previous shot
                    if current_time - shot_start_time > 0.3:  # minimum shot duration threshold
                        shots.append({
                            "start": shot_start_time,
                            "end": current_time,
                            "duration": current_time - shot_start_time,
                            "type": "shot"
                        })
                        motion_beats.append(current_time)
                        shot_start_time = current_time
                        
            prev_hist = hist
            frame_idx += 1
            
        # Append final shot
        if duration - shot_start_time > 0.1:
            shots.append({
                "start": shot_start_time,
                "end": duration,
                "duration": duration - shot_start_time,
                "type": "shot"
            })
            
        cap.release()
        
        avg_cut_duration = sum(s["duration"] for s in shots) / len(shots) if shots else duration
        
        return {
            "source_path": path,
            "duration": duration,
            "fps": fps,
            "total_frames": total_frames,
            "shots": shots,
            "motion_beats": motion_beats,
            "average_cut_duration": avg_cut_duration
        }
