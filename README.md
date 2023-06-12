# web-check
指定したwebページに更新があれば、Slackにメッセージを送る

## 使い方
crontabでスケジュールを設定
```
$ crontab -e
```
(例だと6時間ごと)
```
* /6 * * * python web-check.py
```