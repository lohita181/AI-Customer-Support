import pandas as pd
import random
import os

def prepare_data(input_csv, output_csv, brand='AppleSupport', sample_size=500):
    print(f"Loading {input_csv}...")
    df = pd.read_csv(input_csv)
    
    print(f"Total tweets: {len(df)}")
    
    brand_tweets = df[df['author_id'] == brand]
    print(f"Total {brand} tweets: {len(brand_tweets)}")
    
    brand_replies = brand_tweets.dropna(subset=['in_response_to_tweet_id'])
    
    inbound_tweet_ids = brand_replies['in_response_to_tweet_id'].unique()
    inbound_tweets = df[df['tweet_id'].isin(inbound_tweet_ids)]
    print(f"Total inbound customer tweets found: {len(inbound_tweets)}")
    
    merged = pd.merge(
        inbound_tweets[['tweet_id', 'author_id', 'text', 'created_at']],
        brand_replies[['in_response_to_tweet_id', 'text']],
        left_on='tweet_id',
        right_on='in_response_to_tweet_id',
        suffixes=('_customer', '_brand')
    )
    
    print(f"Total conversation threads reconstructed: {len(merged)}")
    
    merged = merged.drop_duplicates(subset=['tweet_id'])
    
    if len(merged) > sample_size:
        sampled = merged.sample(n=sample_size, random_state=42)
    else:
        sampled = merged
        
    print(f"Saving {len(sampled)} sampled threads to {output_csv}...")
    sampled.to_csv(output_csv, index=False)
    print("Done!")

if __name__ == '__main__':
    if not os.path.exists('twcs.csv'):
        print("Error: twcs.csv not found in the current directory.")
    else:
        prepare_data('twcs.csv', 'processed_data.csv', brand='AppleSupport', sample_size=500)