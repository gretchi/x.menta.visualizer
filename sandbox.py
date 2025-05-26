#!/usr/bin/env python3

from pprint import pprint

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


prompt = """
以下はある日のツイートデータです。このユーザーの精神状態を以下の5項目で-1.0〜+1.0のスコアで評価してください。

【指標】
1. 情動の傾き（ポジティブ〜ネガティブ）
2. 活動性・活力（エネルギー量）
3. 思考の流暢さ（論理性・一貫性）
4. 自己/他者への評価（肯定感、攻撃性、自責・他責など）
5. 統制感・衝動性（抑制の程度）

また、特徴的な出来事や傾向が見られた場合は簡単にコメントを付けてください。

【ツイート例】
- 「今日はなんかイライラしてる。ちょっとしたことで噛みつきそうになる。」
- 「このままで本当に大丈夫なんだろうか。将来が不安すぎる。」
- 「ようやく落ち着いてコーヒー飲めた。少しだけホッとする。」
"""

# prompt = """
# 以下のツイートを読んで、感情スコアを5つの指標（情動の傾き、活動性、思考の流暢さ、自己/他者評価、統制感）で-1.0〜+1.0の範囲で出力してください。

# 【ツイート】
# 「もうなんか全部がだるい。何やっても意味ない気がする。」

# 【出力フォーマット】
# 情動の傾き: -0.9
# 活動性: -0.8
# 思考の流暢さ: +0.1
# 自己/他者評価: -0.7
# 統制感: -0.4
# """


# model_name = "elyza/ELYZA-japanese-Llama-2-7b-fast-instruct"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
# pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

# out = pipe(prompt, max_new_tokens=256)[0]['generated_text']

# out = pipe(prompt, max_new_tokens=256)
# pprint(out)


# model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
# pipe = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# out = pipe(prompt)[0]['generated_text']


# model_name = "elyza/ELYZA-japanese-Llama-2-13b-fast-instruct"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
# pipe = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)


model_name = "AXCXEPT/EZO-gemma-2-2b-jpn-it"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
pipe = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)


out = pipe(prompt)
pprint(out)
