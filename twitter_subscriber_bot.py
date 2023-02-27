import tweepy
import telegram
import time
import datetime
import os

# Twitter API credentials
consumer_key = 'your_consumer_key'
consumer_secret = 'your_consumer_secret'
access_key = 'your_access_key'
access_secret = 'your_access_secret'

# Telegram Bot API credentials
bot_token = 'your_bot_token'
chat_id = 'your_chat_id'

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

# Authenticate with Telegram Bot API
bot = telegram.Bot(bot_token)

# Function to check Twitter subscribers
def check_twitter_subs():
    # Get list of current followers
    followers = api.followers_ids('your_twitter_handle')
    # Get list of previous followers
    prev_followers_path = 'prev_followers.txt'
    if os.path.isfile(prev_followers_path):
        with open(prev_followers_path, 'r') as f:
            prev_followers = [int(line.strip()) for line in f.readlines()]
    else:
        prev_followers = []
    # Find new and lost followers
    new_followers = list(set(followers) - set(prev_followers))
    lost_followers = list(set(prev_followers) - set(followers))
    # Save current followers to file
    with open(prev_followers_path, 'w') as f:
        for follower in followers:
            f.write(str(follower) + '\n')
    # Get profile links of new and lost followers
    new_links = [f'https://twitter.com/{api.get_user(follower).screen_name}' for follower in new_followers]
    lost_links = [f'https://twitter.com/{api.get_user(follower).screen_name}' for follower in lost_followers]
    # Send message to Telegram if there are new or lost followers
    if new_links or lost_links:
        message = ''
        if new_links:
            message += 'New Twitter Subscribers:\n\n'
            for link in new_links:
                message += f'{link}\n'
            message += '\n'
        if lost_links:
            message += 'Unsubscribed Twitter Profiles:\n\n'
            for link in lost_links:
                message += f'{link}\n'
            message += '\n'
        message += f'Total Twitter Subscribers: {len(followers)}'
        bot.send_message(chat_id=chat_id, text=message)

# Main function to run bot
def main():
    # Loop to check Twitter subscribers once per day
    while True:
        # Check time
        now = datetime.datetime.now()
        if now.hour == 12 and now.minute == 0:
            check_twitter_subs()
        # Wait until next day
        time.sleep(60)

if __name__ == '__main__':
    main()