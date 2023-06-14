# web-check
指定したwebページに更新があれば、Slackにメッセージを送る

## 準備
Slack APIのトークンが必要

## 使い方
crontabでスケジュールを設定
```
$ crontab -e
```
(例だと6時間ごと)
```
* /6 * * * python web-check.py
```