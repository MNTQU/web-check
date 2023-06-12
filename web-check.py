import requests
from bs4 import BeautifulSoup
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import config
import locale
from datetime import datetime, timedelta

# Slackのトークンをセットする
client = WebClient(token=config.slack_token)

# 監視するWebページのURLとタイトルをリストでセットする
urls = [
    {"url": "https://www.examole1.html", "title": "例1"},
    {"url": "https://www.examole2.html", "title": "例2"},
]

# ロケールを設定する
locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')

changeCount = 0
# 現在の日時を取得
now = datetime.now()
# 日付と曜日を表示するフォーマットに変換
date_string = now.strftime("%Y年%m月%d日(%a)%H:%M")

message=""

#slackに送る関数
def send_message(channel, message, thread_ts=None):
    client = WebClient(token=config.slack_token)
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=message,
            thread_ts=thread_ts
        )
        print("Message sent: ", response['ts'])
    except SlackApiError as e:
        print("Error sending message: ", e)
        
#slackのタイムスタンプを得る関数
def get_previous_message_timestamp(channel):
    client = WebClient(token=config.slack_token)
    try:
        response = client.conversations_history(
            channel=channel,
            limit=1
        )
        messages = response['messages']
        if len(messages) > 0:
            previous_message = messages[0]
            return previous_message['ts']
    except SlackApiError as e:
        print("Error retrieving previous message: ", e)

# 各Webページの変更前の状態を取得する
old_pages = {}
for url in urls:
    #file_path = f"{url['url'].replace('https://', '').replace('/', '_')}.txt"
    file_path = os.path.join("/home/example/url/", url['url'].replace('https://', '').replace('/', '_') + ".txt")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            old_pages[url['url']] = f.read()
    else:
        old_pages[url['url']] = ""

# 各Webページの状態を取得する
new_pages = {}
for url in urls:
    response = requests.get(url['url'])
    soup = BeautifulSoup(response.content, "html.parser")
    new_pages[url['url']] = str(soup)

# 変更があったWebページをSlackに通知する
for url in urls:
    if old_pages[url['url']] != new_pages[url['url']]:
        message+=f"「{url['title']}」が更新されました！\n{url['url']}\n"
        changeCount += 1
        #file_path = f"{url['url'].replace('https://', '').replace('/', '_')}.txt"
        file_path = os.path.join("/home/example/url/", url['url'].replace('https://', '').replace('/', '_') + ".txt")
        with open(file_path, "w") as f:
            f.write(new_pages[url['url']])

if changeCount == 0:
    text_no=f"\n{date_string}\n更新はありませんでした"
    send_message(config.slack_channel, text_no)
else:
    text_yes=f"\n{date_string}\n{changeCount}件の更新がありました！"
    send_message(config.slack_channel, text_yes)
    previous_message_ts = get_previous_message_timestamp(channel=config.slack_channel)
    send_message(config.slack_channel, message, thread_ts=previous_message_ts)