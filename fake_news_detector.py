import streamlit as st
from transformers import pipeline
import torch
import warnings

# Suppress warnings from transformers regarding max_length
warnings.filterwarnings("ignore")

# Using a robust open-source fake news detection model from huggingface
MODEL_NAME = "mrm8488/bert-tiny-finetuned-fake-news-detection"

@st.cache_resource(show_spinner="Loading Fake News Detection Model...")
def load_detector():
    """
    Loads and caches the fake news detection model to avoid reloading on every run.
    The task is 'text-classification'.
    """
    try:
        # device=0 loads the model on GPU if available, else -1 for CPU
        device = 0 if torch.cuda.is_available() else -1
        detector = pipeline("text-classification", model=MODEL_NAME, device=device)
        return detector
    except Exception as e:
        print(f"Failed to load model: {e}")
        return None

def analyze_article(detector, text: str) -> dict:
    """
    Analyzes text (like a news title or summary) and returns the probability
    of it being fake news or real news.
    """
    if not detector or not text:
        return {"label": "UNKNOWN", "score": 0.0}
        
    try:
        # Pre-process text to limit length as tiny BERT models have a 512 token limit
        # Taking a truncated version if it's too long
        input_text = text[:512] 
        result = detector(input_text)[0] # pipeline returns a list of dicts
        
        # The model usually returns labels like 'LABEL_0' (Real) and 'LABEL_1' (Fake)
        # Check specific model documentation for label mappings.
        # For 'mrm8488/bert-tiny-finetuned-fake-news-detection': 
        # Label 0 -> Real, Label 1 -> Fake 
        # (Note: Always verify label mappings for the specific model used)
        
        raw_label = result.get('label', '')
        score = result.get('score', 0.0)
        
        # Map labels to human-readable format
        if '0' in raw_label or raw_label.lower() == 'true' or raw_label.lower() == 'real':
             return {"prediction": "REAL", "confidence": score, "reason": "The content appears to align with credible reporting standards."}
        elif '1' in raw_label or raw_label.lower() == 'false' or raw_label.lower() == 'fake':
             return {"prediction": "FAKE", "confidence": score, "reason": "The model detected sensationalist language, inconsistencies, or linguistic patterns commonly associated with misinformation."}
        else:
             # Fallback if label format is different
             return {"prediction": raw_label.upper(), "confidence": score, "reason": "Analysis inconclusive."}
            
    except Exception as e:
        print(f"Error analyzing text: {e}")
        return {"prediction": "ERROR", "confidence": 0.0, "reason": "An error occurred during analysis."}

if __name__ == "__main__":
    # Test the function locally
    det = load_detector()
    res = analyze_article(det, "Scientists discover new cure for cancer in deep sea sponges.")
    print(res)
