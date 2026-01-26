
from pathlib import Path
from typing import Dict, Union, List
import numpy as np
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer, PreTrainedTokenizer

class FinancialSentimentAnalyzer:
    def __init__(self, model_dir: str = "model_quantized", model_filename: str = "model_quantized.onnx"):
        self.model_path = Path(model_dir)
        self.tokenizer = AutoTokenizer.from_pretrained("mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
        
        # Load the QUANTIZED model strictly
        print(f"Loading ONNX model from {self.model_path / model_filename}...")
        self.model = ORTModelForSequenceClassification.from_pretrained(
            self.model_path,
            file_name=model_filename
        )
        
        # Labels map for this specific model
        # 0: negative, 1: neutral, 2: positive
        self.id2label = {0: "negative", 1: "neutral", 2: "positive"}

    def analyze_sentiment(self, text: str) -> Dict[str, Union[str, float]]:
        """
        Analyze sentiment of a financial text.
        Returns label (positive/negative/neutral) and confidence score.
        """
        # Tokenize
        inputs = self.tokenizer(text, return_tensors="pt")
        
        # Inference (ONNX)
        outputs = self.model(**inputs)
        logits = outputs.logits.detach().numpy() # Convert to numpy to avoid torch dependency logic
        
        # Softmax to get probabilities
        exp_logits = np.exp(logits - np.max(logits))
        probabilities = exp_logits / exp_logits.sum(axis=1, keepdims=True)
        
        # Get result
        prediction_id = np.argmax(probabilities[0])
        score = float(probabilities[0][prediction_id])
        label = self.id2label[prediction_id]
        
        return {
            "label": label,
            "score": round(score, 4)
        }

if __name__ == "__main__":
    # Test block
    analyzer = FinancialSentimentAnalyzer()
    
    test_headline = "Inflation rises, markets tumble as uncertainty grows"
    print(f"\nAnalyzing: '{test_headline}'")
    result = analyzer.analyze_sentiment(test_headline)
    print(f"Result: {result}")
    
    test_headline_2 = "Tech stocks rally on strong earnings report"
    print(f"\nAnalyzing: '{test_headline_2}'")
    result_2 = analyzer.analyze_sentiment(test_headline_2)
    print(f"Result: {result_2}")
