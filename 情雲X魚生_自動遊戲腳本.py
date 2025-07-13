import tkinter as tk
import threading
import time
import os
import base64
import requests
import re
import random

# ===== 基本設定 =====
API_KEY = os.getenv("OPENAI_API_KEY")
SLEEP_TIME = 5
running = False
paused = False

# 螢幕縮放倍率（針對解析度不同做修正）
SCALE_X = 1.0
SCALE_Y = 1.0

# ===== 啟動檢查 =====
if not API_KEY:
    raise ValueError("請先設定環境變數 OPENAI_API_KEY 嗷！ฅ(>﹏<*ฅ)")

# ===== 顯示簽名動畫 =====
def fade_out(window, duration=1000, steps=20):
    def step(i=0):
        if i < steps:
            alpha = 1 - (i + 1) / steps
            window.attributes('-alpha', alpha)
            window.after(duration // steps, step, i + 1)
        else:
            window.destroy()
    step()

def show_signature():
    window = tk.Toplevel()
    window.overrideredirect(True)
    window.attributes('-topmost', True)
    x = random.randint(100, 800)
    y = random.randint(100, 500)
    window.geometry(f"400x100+{x}+{y}")
    window.configure(bg='black')
    window.attributes('-alpha', 1)
    label = tk.Label(window, text="魚生(工程領導者)", fg="white", bg="black", font=("Arial", 32))
    label.pack(expand=True, fill="both")
    window.update()
    window.after(2000, lambda: fade_out(window))

# ===== GPT Bot 主程式邏輯 =====
def get_screenshot():
    os.system("adb shell screencap -p /sdcard/screenshot.png")
    os.system("adb pull /sdcard/screenshot.png ./screenshot.png")

def read_image_base64(path="screenshot.png"):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def call_gpt(img_base64, retries=3):
    for attempt in range(retries):
        try:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "請根據畫面提供明確的操作指令（例如：tap 500 1600 或 swipe 400 1200 400 800），幫我繼續遊戲。"},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                        ]
                    }
                ],
                "max_tokens": 1000
            }
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"❗ GPT 錯誤（第 {attempt+1} 次）：{e}")
            if attempt == retries - 1:
                raise
            time.sleep(2)

def extract_commands(gpt_response):
    return re.findall(r"(tap \d+ \d+|swipe \d+ \d+ \d+ \d+)", gpt_response)

def adjust_command(cmd):
    parts = cmd.split()
    if parts[0] == "tap":
        x, y = int(parts[1]), int(parts[2])
        return f"tap {int(x*SCALE_X)} {int(y*SCALE_Y)}"
    elif parts[0] == "swipe":
        x1, y1, x2, y2 = map(int, parts[1:])
        return f"swipe {int(x1*SCALE_X)} {int(y1*SCALE_Y)} {int(x2*SCALE_X)} {int(y2*SCALE_Y)}"
    return cmd

def run_commands(commands):
    for cmd in commands:
        adjusted = adjust_command(cmd)
        shell_cmd = f"adb shell input {adjusted}"
        print(f"執行：{shell_cmd}")
        os.system(shell_cmd)
        time.sleep(1)

def bot_loop():
    global running, paused
    loop_count = 0
    print("🤖 GPT 自動遊戲啟動！")
    while running:
        if paused:
            print("⏸ 已暫停中，等待中...")
            time.sleep(1)
            continue

        loop_count += 1
        print(f"\n==== 第 {loop_count} 輪操作 ====")
        try:
            print("📸 擷取畫面...")
            get_screenshot()

            print("🧠 分析畫面內容...")
            img_base64 = read_image_base64()
            gpt_response = call_gpt(img_base64)
            print("🤖 GPT 回覆：\n", gpt_response)

            cmds = extract_commands(gpt_response)
            if cmds:
                print("✅ 執行指令：", cmds)
                run_commands(cmds)
            else:
                print("⚠️ 沒有偵測到指令，稍後重試")
        except Exception as e:
            print("❌ 發生錯誤：", e)

        print(f"⏳ 等待 {SLEEP_TIME} 秒...")
        time.sleep(SLEEP_TIME)
    print("🛑 Bot 已停止")

# ===== GUI 控制介面 =====
def start_bot():
    global running
    if not running:
        running = True
        threading.Thread(target=bot_loop, daemon=True).start()
        show_signature()
        start_button.config(state="disabled")
        stop_button.config(state="normal")
        pause_button.config(state="normal")

def stop_bot():
    global running
    running = False
    start_button.config(state="normal")
    stop_button.config(state="disabled")
    pause_button.config(state="disabled")

def toggle_pause():
    global paused
    paused = not paused
    pause_button.config(text="▶️ 恢復 BOT" if paused else "⏸ 暫停 BOT")

# ===== 主 GUI 視窗 =====
root = tk.Tk()
root.title("🎮 GPT 自動遊戲助手")
root.geometry("400x250")

title_label = tk.Label(root, text="GPT 自動遊戲機器人", font=("Arial", 20))
title_label.pack(pady=20)

start_button = tk.Button(root, text="▶️ 開始 BOT", font=("Arial", 16), command=start_bot)
start_button.pack(pady=5)

pause_button = tk.Button(root, text="⏸ 暫停 BOT", font=("Arial", 16), command=toggle_pause, state="disabled")
pause_button.pack(pady=5)

stop_button = tk.Button(root, text="⏹ 停止 BOT", font=("Arial", 16), command=stop_bot, state="disabled")
stop_button.pack(pady=5)

root.mainloop()
