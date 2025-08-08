import requests
import os
import json
import boto3
import uuid

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")

search_url = "https://api.twitter.com/2/tweets/search/recent"

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
query_params = {'query': 'from:narendramodi ',
                'tweet.fields': 'author_id,text',
                'max_results': 10 }



s3 = boto3.client('s3', region_name='ap-south-1')
bucket_name = 'echosentbucket'
#new addition

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main():
    json_response = connect_to_endpoint(search_url, query_params)
    data = json_response.get("data", [])
    if data:
        for tweet in data:
            dict_value = {
                "uname": tweet["author_id"],  # Still no screen_name in free tier
                "id": tweet["id"],
                "data": tweet["text"]
            }
            file_key = f"tweets/{uuid.uuid4()}.json"
            s3.put_object(Body=json.dumps(dict_value), Bucket="echosentbucket", Key=file_key)
            print(f"✅ Saved tweet to S3: {file_key}")
        else:
         print("No tweets found.")


if __name__ == "__main__":
    main()
