"""
Visual Evaluator for AI-generated frames against a reference.
Computes layout, color, and perceptual differences to generate natural language diagnoses.
"""

import numpy as np
from typing import Dict, Any

import cv2
import numpy as np
from typing import Dict, Any
from skimage.metrics import structural_similarity as ssim

class FrameEvaluator:
    
    @classmethod
    def evaluate(cls, generated_frame: np.ndarray, reference_frame: np.ndarray) -> Dict[str, Any]:
        """
        Compares two frames using SSIM, Histogram matching, and MSE to output a structured diagnosis.
        """
        # Ensure identical shapes. If not, resize generated to match reference.
        if generated_frame.shape != reference_frame.shape:
            h, w = reference_frame.shape[:2]
            generated_frame = cv2.resize(generated_frame, (w, h), interpolation=cv2.INTER_AREA)

        # Convert to BGR for OpenCV
        gen_bgr = cv2.cvtColor(generated_frame, cv2.COLOR_RGBA2BGR) if generated_frame.shape[2] == 4 else generated_frame
        ref_bgr = cv2.cvtColor(reference_frame, cv2.COLOR_RGBA2BGR) if reference_frame.shape[2] == 4 else reference_frame

        # 1. Structural Similarity (SSIM) on Grayscale
        gen_gray = cv2.cvtColor(gen_bgr, cv2.COLOR_BGR2GRAY)
        ref_gray = cv2.cvtColor(ref_bgr, cv2.COLOR_BGR2GRAY)
        
        # Calculate SSIM (returns score between -1 and 1)
        sim_score, diff_image = ssim(ref_gray, gen_gray, full=True)
        
        # 2. Color Histogram Difference
        hist_diff = 0.0
        for i in range(3): # B, G, R channels
            hist_gen = cv2.calcHist([gen_bgr], [i], None, [256], [0, 256])
            hist_ref = cv2.calcHist([ref_bgr], [i], None, [256], [0, 256])
            cv2.normalize(hist_gen, hist_gen, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            cv2.normalize(hist_ref, hist_ref, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            # Bhattacharyya distance (0 means perfect match, 1 means total mismatch)
            hist_diff += cv2.compareHist(hist_ref, hist_gen, cv2.HISTCMP_BHATTACHARYYA)
        
        avg_hist_diff = hist_diff / 3.0

        # Build Diagnosis
        diagnoses = []
        score = max(0.0, sim_score * 100.0)
        
        if sim_score < 0.7:
            diagnoses.append(f"Major layout or structural divergence (SSIM: {sim_score:.2f}).")
        elif sim_score < 0.9:
            diagnoses.append(f"Minor layout misalignment detected (SSIM: {sim_score:.2f}).")
            
        if avg_hist_diff > 0.3:
            diagnoses.append(f"Significant color palette mismatch (HistDiff: {avg_hist_diff:.2f}).")
            score -= 15
        elif avg_hist_diff > 0.15:
            diagnoses.append(f"Slight color/shading variation (HistDiff: {avg_hist_diff:.2f}).")
            score -= 5

        # Normalize score to 0-100
        final_score = max(0.0, min(100.0, score))

        return {
            "score": float(final_score),
            "ssim": float(sim_score),
            "color_diff": float(avg_hist_diff),
            "diagnosis": diagnoses
        }

