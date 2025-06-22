#!/home/gretel/.pyenv/versions/3.13.3/envs/x.menta.visualizer/bin/python

import os
import json
import re
import datetime
import pprint
import sqlite3

from openai import OpenAI

# from extruct_tweet import target_accounts, tweets_js_dir, load_tweets_json, update_table
from extruct_tweet import DATABASE

JST = datetime.timedelta(hours=+9)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY
)

write_since = '2024-04-01T00:00:00+09:00'
conn = sqlite3.connect(DATABASE)

system_prompt = """ある日のツイートデータから、この私の精神状態を以下の6項目+総合得点でスコアで評価してください。
評価に使用するものはツイート数、fav/RT(他者からの共感、他者が理解できうる内容である)、ツイート内容、時間帯などの総合得点です。
これは振り返りに使用する他、主治医へ共有する資料とします。

入力フォーマットは下記のCSV形式です。
時刻,いいね,リツイート,内容\n

【指標】
1. 情動: (-1.0 ~ +1.0): -1.0 ほどネガティブ、+1.0ほどポジティブ
2. 安定性: (-1.0 ~ 0.0): 0に近づくほど精神的に安定している
3. 活動性: (-1.0 ~ +1.0): -1.0ほど引きこもりや活動の停滞がみられ、+ほど活動的である
4. 攻撃性: (0.0 ~ +1.0): 0.0ほど寛容であり、1.0ほど攻撃的である
5. 衝動性: (0.0 ~ +1.0): 0.0ほど落ち着いており、1.0ほど衝動的である
6. 万能感: (-1.0 ~ +1.0): 0.0ほど地に足がついており、-1.0に近づくほど無力感や無力化がみられ、1.0近づくほど万能感がみられる
7. 内向的・外交的: (-1.0 ~ +1.0): -ほど内向的であり+ほど外交的である
8. 総合評価: (-1.0 ~ +1.0): -1.0に近づくほど精神的に不健康であり、+1.0に近づくほど精神的に健康である(躁状態は-)
9. コメント: (string): この評価に至った根拠や特徴的な出来事や傾向、を記載してください（例：「攻撃性と衝動性が高く、自責的な内容が目立つ。うつ状態の兆候が見られる。」）。無ければ空

出力は1~9をカンマ(',')区切りの1行で出力してください。

出力例:
0.2,-0.4,-0.1,0.5,0.7,-0.3,-0.6,-0.5,攻撃性と衝動性が高く、自責的な内容が目立ち、うつ状態の兆候が見られる。
"""


def main():

    for proc_since_date, day_tweets in extruct_tweets_prompt_txt():
        proc_since_date.strftime("%Y/%m/%d")

        tweets = ""
        for tweet in day_tweets:
            timestamp_jst, fav, rt, tweet_text = tweet

            tweets += f"{timestamp_jst},{fav},{rt},{tweet_text}\n"

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {
                    "role": "system", "content": system_prompt
                },
                {
                    "role": "user", "content": tweets

                }
            ]
        )

        str_since_date = proc_since_date.strftime("%Y/%m/%d")
        content = completion.choices[0].message.content
        content = content.strip()

        # print(str_since_date)
        # print(completion.choices[0].message.content)

        # pprint.pprint(completion.choices)

        # [Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='0.6,-0.1,0.4,0.0,0.0,0.3,0.5,0.4,0.5,ポジティブな内容が目立ち、特に春の訪れや入園式の嬉しさを表現している。精神的には安定している様子がうかがえる。,特に目立ったネガティブな表現は見られないため、健康的な精神状態が伺える。', refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=None))]

        line_text = f"{str_since_date},{content}\n"

        print(line_text)

        with open("oai_result.csv", "a", encoding="utf-8", newline="\n") as fh:
            fh.write(line_text)


def extruct_tweets_prompt_txt():
    since_date = datetime.datetime.fromisoformat(write_since)
    proc_since_date = since_date + datetime.timedelta(hours=4)
    proc_until_date = proc_since_date + datetime.timedelta(days=1)
    last_day_text = ""

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

        # output.write("# ---- " + proc_since_date.strftime("%Y/%m/%d") + " ----\n")
        day_tweets = []

        for row in cursor.fetchall():
            account = row[0]
            fav = row[1]
            rt = row[2]
            tweet_text = row[3]
            created_at = datetime.datetime.fromisoformat(row[4])
            day_text = row[5]

            timestamp_jst = created_at.strftime('%H:%M')

            # 行整形
            # 時刻,いいね,リツイート,内容
            day_tweets.append([
                timestamp_jst,
                fav,
                rt,
                tweet_text
            ])

        # print(day_tweets)

        yield (proc_since_date, day_tweets)

        proc_since_date = proc_since_date + datetime.timedelta(days=1)
        proc_until_date = proc_since_date + datetime.timedelta(days=1)


if __name__ == "__main__":
    main()
