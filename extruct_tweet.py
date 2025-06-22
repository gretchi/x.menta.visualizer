#!/usr/bin/env python3

import os
import json
import re
import datetime
import csv
import sqlite3


CREATED_AT_DATE_FORMAT = '%a %b %d %H:%M:%S %z %Y'
JST = datetime.timedelta(hours=+9)

read_since = '2020-04-01T00:00:00+09:00'
write_since = '2024-04-01T00:00:00+09:00'


target_accounts = [
    "Gretel_net",
    "Gretel_io",
]

tweets_js_dir = "./tweets"

retweet_pattern = re.compile(r'RT .*\n$')
reply_pattern = re.compile(r'@[\w]+\s')
url_pattern = re.compile(r'https?:\/\/[\w/:%#\$&\?\(\)~\.=\+\-]+')

exclude_retweet_pattern = re.compile(r'^RT @.*')

DATABASE = "tweets.sqlite3"
# DATABASE = ":memory:"
conn = sqlite3.connect(DATABASE)
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


def update_table(tweets_json, target_account):
    since_date = datetime.datetime.fromisoformat(read_since)
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
                           target_account,
                           fav_cnt,
                           rt_cnt,
                           tweet_text,
                           created_at_jst
                       ))

    conn.commit()


def write_tweets_txt(output_file: str = 'tweets.txt'):
    since_date = datetime.datetime.fromisoformat(write_since)

    with open(output_file, 'w', encoding='utf-8') as output:
        csv_writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        cursor = conn.cursor()
        query = """SELECT
            account,
            fav,
            rt,
            tweet,
            created_at
        FROM tweets
        WHERE created_at > ?
        ORDER BY created_at ASC
        """
        cursor.execute(query, (since_date, ))

        for row in cursor.fetchall():
            account = row[0]
            fav = row[1]
            rt = row[2]
            tweet_text = row[3]
            created_at = datetime.datetime.fromisoformat(row[4])

            # timestamp_jst = created_at_jst.strftime('%Y-%m-%d%H:%M:%S')
            timestamp_jst = created_at.isoformat()

            # 行整形
            row_buf = [
                timestamp_jst,
                account,
                fav,
                rt,
                tweet_text
            ]

            csv_writer.writerow(row_buf)


def write_tweets_prompt_txt(output_file: str = 'tweets_prompt.txt'):
    since_date = datetime.datetime.fromisoformat(write_since)
    proc_since_date = since_date + datetime.timedelta(hours=4)
    proc_until_date = proc_since_date + datetime.timedelta(days=1)
    last_day_text = ""

    with open(output_file, 'w', encoding='utf-8') as output:
        csv_writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        cursor = conn.cursor()
        query = """SELECT
            account,
            fav,
            rt,
            tweet,
            created_at,
            strftime('%Y年%m月%d日', created_at) as day
        FROM tweets
        WHERE created_at BETWEEN ? AND ?
        ORDER BY created_at ASC
        """

        while datetime.datetime.now(datetime.timezone(JST)) > proc_since_date:

            cursor.execute(query, (proc_since_date, proc_until_date, ))

            output.write("# ---- " + proc_since_date.strftime("%Y/%m/%d") + " ----\n")

            for row in cursor.fetchall():
                account = row[0]
                fav = row[1]
                rt = row[2]
                tweet_text = row[3]
                created_at = datetime.datetime.fromisoformat(row[4])
                day_text = row[5]

                timestamp_jst = created_at.strftime('%H:%M')

                # 行整形
                row_buf = [
                    timestamp_jst,
                    account,
                    fav,
                    rt,
                    tweet_text
                ]

                csv_writer.writerow(row_buf)

            output.write("EOL\n\n")
            # output.write("\n")

            proc_since_date = proc_since_date + datetime.timedelta(days=1)
            proc_until_date = proc_since_date + datetime.timedelta(days=1)


if __name__ == '__main__':
    for target_account in target_accounts:
        tweet_js_path = os.path.join(tweets_js_dir, f"{target_account}.js")
        tweets_json = load_tweets_json(tweet_js_path)
        update_table(tweets_json, target_account)

    write_tweets_txt()
    # write_tweets_prompt_txt()

    conn.close()
