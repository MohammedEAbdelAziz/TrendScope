
import time
import random
import string
from collections import defaultdict
import os
import sys

# Add the backend directory to the path so we can import from it
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import get_top_keywords, init_db, get_db_connection

def setup_benchmark_data(num_rows=10000):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing headlines
    cursor.execute("DELETE FROM headlines_history")

    sentiment_labels = ["positive", "negative", "neutral"]

    print(f"Generating {num_rows} rows of data...")
    for i in range(num_rows):
        region_id = "test_region"
        # Use more predictable words for correctness check if num_rows is small
        if num_rows <= 10:
             title = f"word{i} wordextra"
        else:
             title = " ".join([''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10))) for _ in range(10)])

        source = "test_source"
        url = "http://test.com"
        sentiment_score = random.random()
        sentiment_label = random.choice(sentiment_labels)

        cursor.execute("""
            INSERT INTO headlines_history (region_id, title, source, url, sentiment_score, sentiment_label)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (region_id, title, source, url, sentiment_score, sentiment_label))

    conn.commit()
    conn.close()
    print("Data generation complete.")

def benchmark_get_top_keywords(iterations=5):
    start_time = time.time()
    for _ in range(iterations):
        get_top_keywords("test_region", hours=24, limit=10)
    end_time = time.time()

    avg_time = (end_time - start_time) / iterations
    print(f"Average time for get_top_keywords: {avg_time:.4f} seconds")
    return avg_time

def test_correctness():
    print("Testing correctness...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM headlines_history")

    # Insert specific data
    test_data = [
        ("test_region", "Apple is great", "source", "url", 0.9, "positive"),
        ("test_region", "Apple is bad", "source", "url", 0.1, "negative"),
        ("test_region", "Banana is yellow", "source", "url", 0.5, "neutral"),
        ("test_region", "Apple and Banana", "source", "url", 0.5, "neutral"),
    ]

    for row in test_data:
        cursor.execute("""
            INSERT INTO headlines_history (region_id, title, source, url, sentiment_score, sentiment_label)
            VALUES (?, ?, ?, ?, ?, ?)
        """, row)
    conn.commit()
    conn.close()

    results = get_top_keywords("test_region", hours=24, limit=10)

    # Expected:
    # "apple" (len 5): 3 times (1 pos, 1 neg, 1 neutral)
    # "banana" (len 6): 2 times (2 neutral)
    # "great" (len 5): 1 time (1 pos)
    # "yellow" (len 6): 1 time (1 neutral)
    # Short words like "is", "and" should be skipped

    expected = {
        "apple": {"count": 3, "positive": 1, "negative": 1, "neutral": 1},
        "banana": {"count": 2, "positive": 0, "negative": 0, "neutral": 2},
        "great": {"count": 1, "positive": 1, "negative": 0, "neutral": 0},
        "yellow": {"count": 1, "positive": 0, "negative": 0, "neutral": 1},
    }

    result_dict = {r["word"]: {k: v for k, v in r.items() if k != "word"} for r in results}

    for word, exp_values in expected.items():
        if word not in result_dict:
            print(f"FAILED: Word '{word}' not found in results")
            return False
        for key, val in exp_values.items():
            if result_dict[word][key] != val:
                print(f"FAILED: Word '{word}' key '{key}' expected {val}, got {result_dict[word][key]}")
                return False

    print("Correctness test PASSED.")
    return True

if __name__ == "__main__":
    init_db()
    if test_correctness():
        setup_benchmark_data(10000)
        benchmark_get_top_keywords()
