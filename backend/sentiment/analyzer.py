"""
Sentiment Analysis Engine using Distilled FinancialBERT (ONNX Int8)
"""
from pathlib import Path
from typing import Dict, Union, List, Optional
import numpy as np
import logging
import os
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer
from models import SentimentLabel
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

# Noise filter - fluff keywords to exclude
NOISE_KEYWORDS = [
    'opinion', 'podcast', 'guide', 'how to', 'explained', 'personal finance',
    'tips', 'editorial', 'review', 'newsletter', 'subscribe', 'watch live',
    'live updates', 'commentary', 'column', 'q&a', 'interview'
]

BULL_THRESHOLD = 0.6  # High confidence for bull
BEAR_THRESHOLD = 0.6  # High confidence for bear

@dataclass
class PolarityCounts:
    """Counts of bull, bear, and neutral headlines"""
    bull_count: int = 0
    bear_count: int = 0
    neutral_count: int = 0
    filtered_count: int = 0

class SentimentAnalyzer:
    """Analyzes sentiment of financial news using ONNX quantizied model"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SentimentAnalyzer, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if self.initialized:
            return
            
        self.noise_pattern = re.compile(
            r'\b(' + '|'.join(NOISE_KEYWORDS) + r')\b', 
            re.IGNORECASE
        )
        
        # Model paths
        self.model_dir = Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), "model_quantized"))
        self.tokenizer_id = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
        
        try:
            self._load_model()
        except Exception as e:
            logger.critical(f"FATAL: Failed to load ONNX model: {e}")
            raise RuntimeError("Could not load financial sentiment model. Check model_quantized directory.") from e

        self.initialized = True

    def _load_model(self):
        """Load the quantized ONNX model"""
        if not (self.model_dir / "model_quantized.onnx").exists():
            logger.info("Quantized model not found. Please run build_model.py first.")
            self.model = None
            return

        logger.info(f"Loading ONNX model from {self.model_dir}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_id)
        self.model = ORTModelForSequenceClassification.from_pretrained(
            self.model_dir,
            file_name="model_quantized.onnx"
        )
        self.id2label = {0: "negative", 1: "neutral", 2: "positive"}
        logger.info("ONNX Model loaded successfully")

    def is_noise(self, text: str) -> bool:
        if not text: return True
        return bool(self.noise_pattern.search(text))

    def analyze(self, text: str) -> tuple[float, SentimentLabel]:
        """
        Analyze sentiment. Returns (score -1 to 1, label).
        """
        if not text or not text.strip():
            return 0.0, SentimentLabel.NEUTRAL

        if self.model is None:
             # Fallback if model not loaded
            return 0.0, SentimentLabel.NEUTRAL

        try:
            # Tokenize
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=64)
            
            # Inference
            outputs = self.model(**inputs)
            logits = outputs.logits.detach().numpy()
            
            # Softmax
            exp_logits = np.exp(logits - np.max(logits))
            probabilities = exp_logits / exp_logits.sum(axis=1, keepdims=True)
            
            # Result
            pred_id = np.argmax(probabilities[0])
            confidence = float(probabilities[0][pred_id])
            label_str = self.id2label[pred_id]
            
            # Map to system types
            if label_str == "positive":
                return confidence, SentimentLabel.POSITIVE
            elif label_str == "negative":
                return -confidence, SentimentLabel.NEGATIVE
            else:
                return 0.0, SentimentLabel.NEUTRAL
                
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return 0.0, SentimentLabel.NEUTRAL

    def calculate_polarity_score(self, bull_count: int, bear_count: int) -> float:
        total = bull_count + bear_count
        if total == 0: return 50.0
        return round((bull_count / total) * 100, 1)

    def aggregate_sentiment(self, scores: list[float]) -> tuple[float, SentimentLabel, PolarityCounts]:
        counts = PolarityCounts()
        if not scores:
            return 0.0, SentimentLabel.NEUTRAL, counts
            
        for score in scores:
            if score > 0.1:  # Positive confidence
                counts.bull_count += 1
            elif score < -0.1: # Negative confidence
                counts.bear_count += 1
            else:
                counts.neutral_count += 1
                
        polarity_score = self.calculate_polarity_score(counts.bull_count, counts.bear_count)
        
        if polarity_score > 55:
            label = SentimentLabel.POSITIVE
        elif polarity_score < 45:
            label = SentimentLabel.NEGATIVE
        else:
            label = SentimentLabel.NEUTRAL
            
        # Normalize 0-100 to -1 to 1
        normalized = (polarity_score - 50) / 50
        
        return normalized, label, counts

# Singleton
analyzer = SentimentAnalyzer()
