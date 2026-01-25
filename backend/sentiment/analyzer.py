"""
Sentiment Analysis Engine with Polarity Counting and Noise Filter
"""
from textblob import TextBlob
from models import SentimentLabel
import re
from dataclasses import dataclass


# Economic keywords that boost positive/negative sentiment
POSITIVE_KEYWORDS = [
    "growth", "surge", "rally", "boom", "gains", "profit", "recovery",
    "expansion", "bullish", "upbeat", "optimism", "record high",
    "investment", "innovation", "breakthrough", "milestone", "success",
    "strong", "robust", "thriving", "flourishing", "soaring"
]

NEGATIVE_KEYWORDS = [
    "recession", "crash", "crisis", "decline", "losses", "deficit",
    "inflation", "unemployment", "bankruptcy", "collapse", "downturn",
    "bearish", "slump", "plunge", "warning", "risk", "fear", "concern",
    "weak", "struggling", "falling", "dropping", "shrinking", "layoffs"
]

# Noise filter - fluff keywords to exclude
NOISE_KEYWORDS = [
    'opinion', 'podcast', 'guide', 'how to', 'explained', 'personal finance',
    'tips', 'editorial', 'review', 'newsletter', 'subscribe', 'watch live',
    'live updates', 'commentary', 'column', 'q&a', 'interview'
]

KEYWORD_BOOST = 0.15  # How much to boost sentiment for each keyword match
BULL_THRESHOLD = 0.2  # Score above this = Bullish
BEAR_THRESHOLD = -0.2  # Score below this = Bearish


@dataclass
class PolarityCounts:
    """Counts of bull, bear, and neutral headlines"""
    bull_count: int = 0
    bear_count: int = 0
    neutral_count: int = 0
    filtered_count: int = 0  # Headlines removed by noise filter


class SentimentAnalyzer:
    """Analyzes sentiment of economic news headlines with polarity counting"""
    
    def __init__(self):
        self.positive_pattern = re.compile(
            r'\b(' + '|'.join(POSITIVE_KEYWORDS) + r')\b', 
            re.IGNORECASE
        )
        self.negative_pattern = re.compile(
            r'\b(' + '|'.join(NEGATIVE_KEYWORDS) + r')\b', 
            re.IGNORECASE
        )
        self.noise_pattern = re.compile(
            r'\b(' + '|'.join(NOISE_KEYWORDS) + r')\b', 
            re.IGNORECASE
        )
    
    def is_noise(self, text: str) -> bool:
        """Check if headline is noise/fluff that should be filtered out"""
        if not text:
            return True
        return bool(self.noise_pattern.search(text))
    
    def analyze(self, text: str) -> tuple[float, SentimentLabel]:
        """
        Analyze sentiment of text.
        Returns: (score from -1 to 1, sentiment label)
        """
        if not text or not text.strip():
            return 0.0, SentimentLabel.NEUTRAL
        
        # Get base sentiment from TextBlob
        blob = TextBlob(text)
        base_score = blob.sentiment.polarity  # -1 to 1
        
        # Apply keyword boosting
        positive_matches = len(self.positive_pattern.findall(text))
        negative_matches = len(self.negative_pattern.findall(text))
        
        keyword_boost = (positive_matches - negative_matches) * KEYWORD_BOOST
        
        # Combine scores with clamping
        final_score = max(-1.0, min(1.0, base_score + keyword_boost))
        
        # Determine label using thresholds for Bull/Bear classification
        if final_score > BULL_THRESHOLD:
            label = SentimentLabel.POSITIVE  # Bullish
        elif final_score < BEAR_THRESHOLD:
            label = SentimentLabel.NEGATIVE  # Bearish
        else:
            label = SentimentLabel.NEUTRAL
        
        return final_score, label
    
    def calculate_polarity_score(self, bull_count: int, bear_count: int) -> float:
        """
        Calculate sentiment percentage based on Bull/Bear ratio.
        Score = (Bullish_Count / (Bullish_Count + Bearish_Count)) * 100
        """
        total_active = bull_count + bear_count
        if total_active == 0:
            return 50.0  # Neutral when no active signals
        return round((bull_count / total_active) * 100, 1)
    
    def aggregate_sentiment(self, scores: list[float]) -> tuple[float, SentimentLabel, PolarityCounts]:
        """
        Aggregate multiple sentiment scores using polarity counting.
        Returns: (average score -1 to 1, overall label, polarity counts)
        """
        counts = PolarityCounts()
        
        if not scores:
            return 0.0, SentimentLabel.NEUTRAL, counts
        
        for score in scores:
            if score > BULL_THRESHOLD:
                counts.bull_count += 1
            elif score < BEAR_THRESHOLD:
                counts.bear_count += 1
            else:
                counts.neutral_count += 1
        
        # Calculate polarity-based score
        polarity_score = self.calculate_polarity_score(counts.bull_count, counts.bear_count)
        
        # Determine overall label based on polarity score
        if polarity_score > 55:
            label = SentimentLabel.POSITIVE
        elif polarity_score < 45:
            label = SentimentLabel.NEGATIVE
        else:
            label = SentimentLabel.NEUTRAL
        
        # Convert polarity percentage to -1 to 1 scale for compatibility
        normalized_score = (polarity_score - 50) / 50  # -1 to 1
        
        return normalized_score, label, counts
    
    def aggregate_sentiment_legacy(self, scores: list[float]) -> tuple[float, SentimentLabel]:
        """
        Legacy aggregation method (for backward compatibility).
        """
        score, label, _ = self.aggregate_sentiment(scores)
        return score, label


# Singleton instance
analyzer = SentimentAnalyzer()
