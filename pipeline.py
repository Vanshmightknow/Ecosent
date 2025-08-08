# pipeline.py

import app
import roberta_sentiment_local

def run_pipeline():
    print("\n Step 1: Fetching tweets from Twitter API...")
    app.main()

    print("\n Step 2: Performing sentiment analysis on new tweets...")
    roberta_sentiment_local.run_sentiment_pipeline()

if __name__ == "__main__":
    run_pipeline()
