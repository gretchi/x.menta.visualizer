# x.menta.visualizer

Python: 3.13.3
CUDA: 12.8

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128


## models

- elyza/ELYZA-japanese-Llama-2-13b-fast-instruct
- nlptown/bert-base-multilingual-uncased-sentiment
- mistralai/Mistral-Nemo-Instruct-2407


sudo nvidia-smi --gpu-reset -i 0
watch nvidia-smi


## 分析用SQL

```sh
sqlite3 tweets.sqlite3 <<EOF
.headers on
.mode tabs
.output stdout
SELECT
    strftime('%Y-%m-%d', created_at) as day,
    COUNT(*) as cnt,
    avg(fav) as avg_fav,
    avg(rt) as avg_rt
FROM tweets
WHERE fav < 100
GROUP BY strftime('%Y-%m-%d', created_at)
ORDER BY created_at ASC;
EOF
```

```sql
.headers ON
.mode column

SELECT
    strftime('%Y-%m', created_at) as month,
    COUNT(*) as cnt,
    avg(fav),
    avg(rt)
FROM tweets
WHERE fav < 100
GROUP BY strftime('%Y-%m', created_at)
ORDER BY created_at ASC;


SELECT
    strftime('%Y', created_at) || '-W' || strftime('%W', created_at) AS week,
    COUNT(*) as cnt,
    avg(fav) as avg_fav,
    avg(rt) as avg_rt
FROM tweets
WHERE fav < 100
GROUP BY week
ORDER BY created_at ASC;


SELECT
    strftime('%Y-%m', created_at) as month,
    COUNT(*) as cnt,
    avg(fav),
    avg(rt)
FROM tweets
WHERE fav < 100
GROUP BY strftime('%Y-%m', created_at)
ORDER BY created_at ASC;

SELECT
    strftime('%Y', created_at) || '-Q' ||
        ((cast(strftime('%m', created_at) as integer) - 1) / 3 + 1) as quarter,
    COUNT(*) as cnt,
    avg(fav),
    avg(rt)
FROM tweets
WHERE fav < 200
GROUP BY quarter
ORDER BY MIN(created_at) ASC;
```
