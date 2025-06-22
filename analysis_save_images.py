#!/home/gretel/.pyenv/versions/3.13.3/envs/x.menta.visualizer/bin/python

import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, periodogram

output_dir = "./exclude/output"

# CSV読み込み（ヘッダーあり、日単位）
df = pd.read_csv("oai_result.csv")
columns_to_analyze = columns_to_analyze = [
    "情動 (-1.0~+1.0)",
    "安定性 (-1.0~0.0)",
    "活動性 (-1.0~+1.0)",
    "攻撃性 (0.0~+1.0)",
    "衝動性 (0.0~+1.0)",
    "万能感 (-1.0~+1.0)",
    "内向外向 (-1.0~+1.0)",
    "総合評価 (-1.0~+1.0)",
]

# 時系列軸
x = np.arange(len(df))

# パラメータ設定
window_size = 7
cutoff_period = 20  # バターワースのカットオフ（周期で指定）

# グラフの描画設定
plt.rc('font', family='BIZ UDGothic')
plt.figure(figsize=(14, 5 * len(columns_to_analyze)))

i = 0

for col in columns_to_analyze:
    signal = df[col].values

    # 平滑化
    moving_avg = np.convolve(signal, np.ones(window_size)/window_size, mode='same')
    b, a = butter(N=2, Wn=1/cutoff_period, btype='low', fs=1)
    butter_filtered = filtfilt(b, a, signal)

    # 周期
    freqs, power = periodogram(signal, fs=1)

    # グラフ作成
    fig, axs = plt.subplots(2, 1, figsize=(10, 6))
    axs[0].plot(x, signal, label="Raw", alpha=0.4)
    axs[0].plot(x, moving_avg, label="Moving Avg", linewidth=2)
    axs[0].plot(x, butter_filtered, label="Butterworth LPF", linewidth=2)
    axs[0].set_title(f"{col} の時系列と平滑化")
    axs[0].set_xlabel("日数")
    axs[0].set_ylabel(col)
    axs[0].legend()
    axs[0].grid(True)

    # 周期解析グラフ
    periods = 1 / freqs[1:]
    powers = power[1:]
    mask = (periods >= 1) & (periods <= 250)
    periods_filtered = periods[mask]
    powers_filtered = powers[mask]

    axs[1].plot(periods_filtered, powers_filtered)
    axs[1].set_title(f"{col} のスペクトル解析(周期)")
    axs[1].set_xlabel("frequency (日)")
    axs[1].set_ylabel("power")
    axs[1].grid(True)

    # 保存
    output_path = os.path.join(output_dir, f"{i+1}. {col}.png")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    i += 1

    print(f"{output_path} に保存しました。")
