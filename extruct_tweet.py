#!/usr/bin/env python3

import json
import re
import datetime
import csv
import sqlite3


CREATED_AT_DATE_FORMAT = '%a %b %d %H:%M:%S %z %Y'
JST = datetime.timedelta(hours=+9)

read_since = '2020-04-01T00:00:00+09:00'

account = "Gretel_net"
tweets_js_path = f"./tweets-{account}.js"

retweet_pattern = re.compile(r'RT .*\n$')
reply_pattern = re.compile(r'@[\w]+\s')
url_pattern = re.compile(r'https?:\/\/[\w/:%#\$&\?\(\)~\.=\+\-]+')


conn = sqlite3.connect("tweets.sqlite3")
conn.execute("""
CREATE TABLE IF NOT EXISTS tweets (
        id INTEGER NOT NULL PRIMARY KEY,
        account TEXT NOT NULL,
        fav INTEGER NOT NULL,
        rt INTEGER NOT NULL,
        tweet TEXT,
        created_at TIMESTAMP NOT NULL
);
""")


def exclude_specific_pattern(s: str):
    s = retweet_pattern.sub('', s)
    # s = reply_pattern.sub('', s)
    s = url_pattern.sub('', s)
    return s


def escape_special_chars(s: str):
    s = s.replace('\n', '\\n')
    # s = s.replace('"', '\\"')

    return s


def is_newer_than(twitter_date_str: str, comparison_date: datetime.datetime):
    parsed_date = datetime.datetime.strptime(
        twitter_date_str, CREATED_AT_DATE_FORMAT)
    return parsed_date > comparison_date


def load_tweets_json(tweets_js_file: str):
    with open(tweets_js_file, 'r', encoding='utf-8') as file:
        content = file.read()
        cleaned_content = content.replace('window.YTD.tweets.part0 = ', '', 1)
    return json.loads(cleaned_content)


def write_tweets_txt(tweets_json, output_file: str = 'tweets.txt'):
    since_date = datetime.datetime.fromisoformat(read_since)
    with open(output_file, 'w', encoding='utf-8') as output:
        csv_writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        cursor = conn.cursor()

        for tw in tweets_json:
            tweet = tw["tweet"]
            if not is_newer_than(tweet["created_at"], since_date):
                continue

            # id
            id_str = tweet["id_str"]

            # タイムスタンプを取得
            created_at_utc = datetime.datetime.strptime(tweet["created_at"], CREATED_AT_DATE_FORMAT)
            created_at_jst = created_at_utc.astimezone(datetime.timezone(JST))
            timestamp_jst = created_at_jst.strftime('%Y-%m-%d (%a) %H:%M:%S')

            # ツイートの取得とクリーニング
            tweet_text = escape_special_chars(tweet["full_text"]) + '\n'
            tweet_text = exclude_specific_pattern(tweet_text)
            tweet_text = tweet_text.strip()

            if not tweet_text.strip():
                # 空であればスルー
                continue

            # ふぁぼ, RT取得
            fav_cnt = tweet["favorite_count"]
            rt_cnt = tweet["retweet_count"]

            # 行整形
            row_buf = [
                timestamp_jst,
                fav_cnt,
                rt_cnt,
                tweet_text
            ]
            csv_writer.writerow(row_buf)

            cursor.execute("""
            INSERT INTO tweets (id, account, fav, rt, tweet, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                account = excluded.account,
                fav = excluded.fav,
                rt = excluded.rt,
                tweet = excluded.tweet,
                created_at = excluded.created_at;
            """,
                           (
                               int(id_str),
                               account,
                               fav_cnt,
                               rt_cnt,
                               tweet_text,
                               created_at_jst
                           ))

        conn.commit()
        # output.write(line_text)


if __name__ == '__main__':
    tweets_json = load_tweets_json(tweets_js_path)
    write_tweets_txt(tweets_json)

    conn.close()
