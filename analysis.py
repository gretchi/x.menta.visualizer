#!/home/gretel/.pyenv/versions/3.13.3/envs/x.menta.visualizer/bin/python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, periodogram

# CSV読み込み（ヘッダーあり、日単位）
df = pd.read_csv("your_data.csv")  # ← ファイル名を適宜修正
columns_to_analyze = ["情動", "活動性", "総合評価"]  # ← 必要な項目を追加/削除

# 時系列軸
x = np.arange(len(df))

# パラメータ設定
window_size = 7
cutoff_period = 20  # バターワースのカットオフ（周期で指定）

# グラフの描画設定
plt.figure(figsize=(14, 5 * len(columns_to_analyze)))

for i, col in enumerate(columns_to_analyze):
    signal = df[col].values

    # 移動平均
    moving_avg = np.convolve(signal, np.ones(window_size)/window_size, mode='same')

    # バターワースフィルタ
    b, a = butter(N=2, Wn=1/cutoff_period, btype='low', fs=1)
    butter_filtered = filtfilt(b, a, signal)

    # 周波数解析
    freqs, power = periodogram(signal, fs=1)

    # 描画
    plt.subplot(len(columns_to_analyze), 2, i*2 + 1)
    plt.plot(x, signal, label="Raw", alpha=0.4)
    plt.plot(x, moving_avg, label=f"Moving Avg ({window_size}d)", linewidth=2)
    plt.plot(x, butter_filtered, label=f"Butterworth LPF (~{cutoff_period}d)", linewidth=2)
    plt.title(f"{col} の時系列と平滑化")
    plt.xlabel("日数")
    plt.ylabel(col)
    plt.legend()
    plt.grid(True)

    plt.subplot(len(columns_to_analyze), 2, i*2 + 2)
    plt.plot(1/freqs[1:], power[1:])  # 周期 vs パワー（f=0除外）
    plt.title(f"{col} の周期解析")
    plt.xlabel("周期（日）")
    plt.ylabel("パワー")
    plt.grid(True)

plt.tight_layout()
plt.show()
