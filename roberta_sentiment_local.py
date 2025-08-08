import boto3
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax

# Load Roberta model and tokenizer
MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

# Connect to S3
s3 = boto3.client('s3', region_name='ap-south-1')
bucket_name = 'echosentbucket'
prefix = 'tweets/'

# List tweet files
response = s3.list_objects_v2(Bucket=bucket_name,Prefix=prefix)

def analyze_sentiment(text):
    encoded_input = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
    output = model(**encoded_input)
    scores = softmax(output.logits[0].detach().numpy())
    return {
        'negative': float(scores[0]),
        'neutral': float(scores[1]),
        'positive': float(scores[2])
    }
s3 = boto3.client('s3', region_name='ap-south-1')
bucket = 'echosentbucket'

def upload_sentiment_result(tweet_id, text, sentiment_dict):
    result = {
        "tweet_id": tweet_id,
        "text": text,
        "sentiment_positive": round(sentiment_dict["positive"], 4),
        "sentiment_neutral": round(sentiment_dict["neutral"], 4),
         "sentiment_negative": round(sentiment_dict["negative"], 4),
        "dominant_sentiment": max(sentiment_dict, key=sentiment_dict.get)
    }
    
    key = f"results/sentiment_{tweet_id}.json"
    s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(result))
    print(f"✅ Saved sentiment to: s3://{bucket}/{key}")

def run_sentiment_pipeline():
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    for obj in response.get('Contents', []):
        key = obj['Key']
        if key.endswith('.json'):
            file_obj = s3.get_object(Bucket=bucket_name, Key=key)
            tweet_data = json.loads(file_obj['Body'].read().decode('utf-8'))
            text = tweet_data.get('data')
            tweet_id = tweet_data.get('id')
            sentiment = analyze_sentiment(text)
            print(f"\n Tweet ID: {tweet_id}")
            print(f"Text: {text}")
            print(f"Sentiment: {sentiment}")
            upload_sentiment_result(tweet_id, text, sentiment)


