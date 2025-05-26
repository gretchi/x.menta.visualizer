#!/usr/bin/env python3

import time
import datetime

import pprint

from transformers import AutoTokenizer, AutoModelForCausalLM

start_time = time.time()
latest_time = time.time()


def main():
    ptint_with_ts("start")

    prompt = """
ある日のツイートデータから、このユーザーの精神状態を以下の6項目+総合得点でスコアで評価してください。
評価に使用するものはツイート数、fav/RT(他者からの共感、他者が理解できうる内容である)、ツイート内容、時間帯などの総合得点です。
これは本人の振り返りに使用する他、主治医へ共有するものでもあります。

入力のフォーマットは下記のCSVです。
日時(JST),いいね,リツイート,内容\n

【指標】
1. 情動(emotions): (-1.0 ~ +1.0): -1.0 ほどネガティブ、+1.0ほどポジティブ
2. 安定性(stability): (-1.0 ~ 0.0): 0に近づくほど精神的に安定している
3. 活動性(energy): (-1.0 ~ +1.0): -1.0ほど引きこもりや活動の停滞がみられ、+ほど活動的である
4. 攻撃性(aggression): (0.0 ~ +1.0): 0.0ほど寛容であり、1.0ほど攻撃的である
5. 衝動性(impulsivity): (0.0 ~ +1.0): 0.0ほど落ち着いており、1.0ほど衝動的である
6. 万能感:(omnipotence) (-1.0 ~ +1.0): 0.0ほど地に足がついており、-1.0に近づくほど無力感や無力化がみられ、1.0近づくほど万能感がみられる
7. 内向的・外交的(introvert_extrovert): (-1.0 ~ +1.0): -ほど内向的であり+ほど外交的である
8. 総合評価: (-1.0 ~ +1.0): -1.0に近づくほど精神的に不健康であり、+1.0に近づくほど精神的に健康である(躁状態は-)


特徴的な出来事や傾向があれば event に記載してください（例：「深夜帯に怒りのツイートが集中」）。診察に参考となるコメントがあれば comment に記載してください（例：「攻撃性が高く、現実感に乏しい発言がみられる」）。特に無い場合は空で構いません。
また、この評価に至った根拠を basis に記載してください。

出力は以下の"```"より中のJSON形式でお願いします。
```
{
    "inputs": [inputs],
    "emotions": 0.2,
    "stability": -0.4,
    "energy": -0.1,
    "aggression": 0.5,
    "impulsivity": 0.7,
    "omnipotence": -0.3,
    "introvert_extrovert": -0.6,
    "total": -0.5,
    "event": "深夜帯にネガティブな連投があった",
    "comment": "攻撃性と衝動性が高く、自責的な内容が目立つ。うつ状態の兆候が見られる。",
    "basis": "この評価に至った根拠"
}
```

    """

    ptint_with_ts("before model init")

    model_name = "AXCXEPT/EZO-gemma-2-2b-jpn-it"
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", )

    ptint_with_ts("after model init")

    while True:
        input_text = ""
        while True:
            input_raw = input("> ")
            if not input_raw.strip():
                break
            input_text += input_raw + "\n"

        messages = [
            {"role": "user", "content": prompt + f"以下入力:\n {input_text}\n"}
        ]

        ptint_with_ts(pprint.pformat(messages))

        ptint_with_ts("before model apply_chat_template")
        input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt", return_dict=True).to("cuda")
        ptint_with_ts("after model apply_chat_template")

        ptint_with_ts("before model model.generate")
        outputs = model.generate(**input_ids, max_new_tokens=1024)
        ptint_with_ts(tokenizer.decode(outputs[0]))
        print("\a")

        ptint_with_ts("after model model.generate")

    ptint_with_ts("end")


def ptint_with_ts(object):
    global latest_time
    now_dt = datetime.datetime.now()
    str_ts = now_dt.strftime("%Y/%m/%d %H:%M:%S.%f")
    print(f"[{str_ts}]: <{time.time() - start_time:.04f}>", f": lap: +{time.time() - latest_time:.04f}:", object)
    latest_time = time.time()


if __name__ == "__main__":
    main()
