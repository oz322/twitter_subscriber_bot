# import tweepy
# import telegram
# import time
# import datetime
# import os
#
# # Twitter API credentials
# consumer_key = 'your_consumer_key'
# consumer_secret = 'your_consumer_secret'
# access_key = 'your_access_key'
# access_secret = 'your_access_secret'
#
# # Telegram Bot API credentials
# bot_token = 'your_bot_token'
# chat_id = 'your_chat_id'
#
# # Authenticate with Twitter API
# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_key, access_secret)
# api = tweepy.API(auth)
#
# # Authenticate with Telegram Bot API
# bot = telegram.Bot(bot_token)
#
# # Function to check Twitter subscribers
# def check_twitter_subs():
#     # Get list of current followers
#     followers = api.followers_ids('your_twitter_handle')
#     # Get list of previous followers
#     prev_followers_path = 'prev_followers.txt'
#     if os.path.isfile(prev_followers_path):
#         with open(prev_followers_path, 'r') as f:
#             prev_followers = [int(line.strip()) for line in f.readlines()]
#     else:
#         prev_followers = []
#     # Find new and lost followers
#     new_followers = list(set(followers) - set(prev_followers))
#     lost_followers = list(set(prev_followers) - set(followers))
#     # Save current followers to file
#     with open(prev_followers_path, 'w') as f:
#         for follower in followers:
#             f.write(str(follower) + '\n')
#     # Get profile links of new and lost followers
#     new_links = [f'https://twitter.com/{api.get_user(follower).screen_name}' for follower in new_followers]
#     lost_links = [f'https://twitter.com/{api.get_user(follower).screen_name}' for follower in lost_followers]
#     # Send message to Telegram if there are new or lost followers
#     if new_links or lost_links:
#         message = ''
#         if new_links:
#             message += 'New Twitter Subscribers:\n\n'
#             for link in new_links:
#                 message += f'{link}\n'
#             message += '\n'
#         if lost_links:
#             message += 'Unsubscribed Twitter Profiles:\n\n'
#             for link in lost_links:
#                 message += f'{link}\n'
#             message += '\n'
#         message += f'Total Twitter Subscribers: {len(followers)}'
#         bot.send_message(chat_id=chat_id, text=message)
#
# # Main function to run bot
# def main():
#     # Loop to check Twitter subscribers once per day
#     while True:
#         # Check time
#         now = datetime.datetime.now()
#         if now.hour == 12 and now.minute == 0:
#             check_twitter_subs()
#         # Wait until next day
#         time.sleep(60)
#
# if __name__ == '__main__':
#     main()

import tweepy
import logging
import os
from telegram.ext import Updater, CommandHandler
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Twitter API credentials
consumer_key = 'your_consumer_key'
consumer_secret = 'your_consumer_secret'
access_key = 'your_access_key'
access_secret = 'your_access_secret'

# Twitter handle to check followers for
twitter_handle = 'your_twitter_handle'

# Telegram bot token and chat ID to send updates to
bot_token = 'your_bot_token'
chat_id = 'your_chat_id'

# Logging setup
log_dir = os.path.join(os.getcwd(), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = os.path.join(log_dir, f'{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Authenticate Twitter API credentials
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

# Authenticate Telegram bot credentials
updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher


# Function to get follower list
def get_follower_list():
    follower_list = []
    for follower in tweepy.Cursor(api.followers, screen_name=twitter_handle).items():
        follower_list.append(follower.screen_name)
    return follower_list


# Function to send Telegram message
def send_telegram_message(message):
    try:
        dispatcher.bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logging.error(f'Error sending Telegram message: {e}')


# Function to plot subscriber timelines
def plot_timeline(subscribed_dates, unsubscribed_dates):
    plt.plot(subscribed_dates, [1] * len(subscribed_dates), 'o', label='subscribed')
    plt.plot(unsubscribed_dates, [0] * len(unsubscribed_dates), 'o', label='unsubscribed')
    plt.yticks([0, 1], ['unsubscribed', 'subscribed'])
    plt.legend()
    plt.tight_layout()
    plt.savefig('timeline.png')
    plt.close()


# Function to process new followers
def process_new_followers(new_followers, prev_followers):
    subscribed_list = []
    for follower in new_followers:
        if follower not in prev_followers:
            subscribed_list.append(follower)
            logging.info(f'{follower} subscribed for the first time at {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
    if subscribed_list:
        send_telegram_message(f'New subscribers: {", ".join(subscribed_list)}')
    return set(new_followers)


# Function to process unfollowers
def process_unfollowers(new_followers, prev_followers):
    unsubscribed_list = []
    for follower in prev_followers:
        if follower not in new_followers:
            unsubscribed_list.append(follower)
            logging.info(f'{follower} unsubscribed at {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
    if unsubscribed_list:
        send_telegram_message(f'Unsubscribed profiles: {", ".join(unsubscribed_list)}')
    return set(new_followers)


# Function to update previous follower list
def update_prev_followers(new_followers):
    with open('prev_followers.txt', 'w') as f:
        f.write('\n'.join(new_followers))


# Function to check for new followers and send Telegram message
def check_followers():
    # Load previous follower list
    try:
        with open('prev_followers.txt', 'r') as f:
            prev_followers = set(f.read().splitlines())
    except FileNotFoundError:
        prev_followers = set()

    # Get current follower list
    new_followers = get_follower_list()

    # Process new subscribers and unsubscribers
    new_followers = process_new_followers(new_followers, prev_followers)
    new_followers = process_unfollowers(new_followers, prev_followers)

    # Update previous follower list
    update_prev_followers(new_followers)

    # Plot subscriber timeline
    subscribed_dates = []
    unsubscribed_dates = []
    with open(log_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'subscribed for the first time at' in line:
                subscribed_dates.append(datetime.strptime(line.split(' ')[-2], '%d-%m-%Y'))
            elif 'unsubscribed at' in line:
                unsubscribed_dates.append(datetime.strptime(line.split(' ')[-2], '%d-%m-%Y'))
    if subscribed_dates and unsubscribed_dates:
        subscribed_dates_str = [d.strftime('%d.%m.%Y') for d in sorted(subscribed_dates)]
        unsubscribed_dates_str = [d.strftime('%d.%m.%Y') for d in sorted(unsubscribed_dates)]
        if subscribed_dates_str != unsubscribed_dates_str:
            plot_timeline(subscribed_dates, unsubscribed_dates)


if __name__ == '__main__':
    # Schedule check_followers function to run every day at 12:00
    now = datetime.now()
    run_time = datetime(now.year, now.month, now.day, hour=12, minute=0, second=0)
    if now > run_time:
        run_time += timedelta(days=1)
    delta_t = run_time - now
    secs = delta_t.seconds + 1
    updater.job_queue.run_repeating(check_followers, interval=secs, first=0)

    # Start bot
    updater.start_polling()
    updater.idle()
