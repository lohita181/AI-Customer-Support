import pandas as pd
import random
import os

def prepare_data(input_csv, output_csv, brand='AppleSupport', sample_size=500):
    print(f"Loading {input_csv}...")
    # Read the dataset. It's large, so we might want to specify dtypes or just let pandas figure it out.
    df = pd.read_csv(input_csv)
    
    print(f"Total tweets: {len(df)}")
    
    # Get all tweets from the brand
    brand_tweets = df[df['author_id'] == brand]
    print(f"Total {brand} tweets: {len(brand_tweets)}")
    
    # Filter brand tweets that are responses to a user
    # dropna ensures we only look at replies, not top-level broadcasts
    brand_replies = brand_tweets.dropna(subset=['in_response_to_tweet_id'])
    
    # Get the corresponding user inbound tweets
    inbound_tweet_ids = brand_replies['in_response_to_tweet_id'].unique()
    inbound_tweets = df[df['tweet_id'].isin(inbound_tweet_ids)]
    print(f"Total inbound customer tweets found: {len(inbound_tweets)}")
    
    # Merge them together to form threads (Customer -> Brand)
    # We rename columns to make them clear
    merged = pd.merge(
        inbound_tweets[['tweet_id', 'author_id', 'text', 'created_at']],
        brand_replies[['in_response_to_tweet_id', 'text']],
        left_on='tweet_id',
        right_on='in_response_to_tweet_id',
        suffixes=('_customer', '_brand')
    )
    
    print(f"Total conversation threads reconstructed: {len(merged)}")
    
    # Drop duplicates if any
    merged = merged.drop_duplicates(subset=['tweet_id'])
    
    # Sample 500 rows randomly
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
