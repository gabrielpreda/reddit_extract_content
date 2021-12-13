import os
import praw
import pandas as pd
import datetime as dt
from tqdm import tqdm
import time


def get_date(created):
    return dt.datetime.fromtimestamp(created)


def reddit_connection():
    personal_use_script = os.environ["REDDIT_PERSONAL_USE_SCRIPT_14_CHARS"]
    client_secret = os.environ["REDDIT_SECRET_KEY_27_CHARS"]
    user_agent = os.environ["REDDIT_APP_NAME"]
    username = os.environ["REDDIT_USER_NAME"]
    password = os.environ["REDDIT_LOGIN_PASSWORD"]

    reddit = praw.Reddit(client_id=personal_use_script, \
                         client_secret=client_secret, \
                         user_agent=user_agent, \
                         username=username, \
                         password='')
    return reddit


def build_dataset(reddit, search_words='CryptoCurrency', items_limit=2000):
    
    # Collect reddit posts
    subreddit = reddit.subreddit(search_words)
    new_subreddit = subreddit.new(limit=items_limit)
    topics_dict = { "title":[],
                "score":[],
                "id":[], "url":[],
                "comms_num": [],
                "created": [],
                "body":[]}
    
    print(f"retreive new reddit posts ...")
    for submission in tqdm(new_subreddit):
        topics_dict["title"].append(submission.title)
        topics_dict["score"].append(submission.score)
        topics_dict["id"].append(submission.id)
        topics_dict["url"].append(submission.url)
        topics_dict["comms_num"].append(submission.num_comments)
        topics_dict["created"].append(submission.created)
        topics_dict["body"].append(submission.selftext)

    for comment in tqdm(subreddit.comments(limit=2000)):
        topics_dict["title"].append("Comment")
        topics_dict["score"].append(comment.score)
        topics_dict["id"].append(comment.id)
        topics_dict["url"].append("")
        topics_dict["comms_num"].append(0)
        topics_dict["created"].append(comment.created)
        topics_dict["body"].append(comment.body)

    topics_df = pd.DataFrame(topics_dict)
    print(f"new reddit posts retrieved: {len(topics_df)}")
    topics_df['timestamp'] = topics_df['created'].apply(lambda x: get_date(x))

    return topics_df
   

def update_and_save_dataset(topics_df):   
    file_path = "reddit_cc.csv"
    if os.path.exists(file_path):
        topics_old_df = pd.read_csv(file_path)
        print(f"past reddit posts: {topics_old_df.shape}")
        topics_all_df = pd.concat([topics_old_df, topics_df], axis=0)
        print(f"new reddit posts: {topics_df.shape[0]} past posts: {topics_old_df.shape[0]} all posts: {topics_all_df.shape[0]}")
        topics_new_df = topics_all_df.drop_duplicates(subset = ["id"], keep='last', inplace=False)
        print(f"all reddit posts: {topics_new_df.shape}")
        topics_new_df.to_csv(file_path, index=False)
    else:
        print(f"reddit posts: {topics_df.shape}")
        topics_df.to_csv(file_path, index=False)


if __name__ == "__main__": 
	reddit = reddit_connection()
	topics_data_df = build_dataset(reddit)
	update_and_save_dataset(topics_data_df)
