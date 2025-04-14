#!/usr/bin/env python3
"""
NTUST 英簡單系統啟動器
同時執行後端 API 和爬蟲服務，並將輸出顯示在終端上
"""

import argparse
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime


# 定義顏色代碼，用於區分不同應用的輸出
class Colors:
    RESET = "\033[0m"
    API = "\033[36m"  # 青色
    CRAWLER = "\033[33m"  # 黃色
    SYSTEM = "\033[35m"  # 紫色
    ERROR = "\033[31m"  # 紅色


def log(tag, message, color=Colors.SYSTEM):
    """記錄訊息，並附加時間戳記"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{color}[{timestamp}] [{tag}] {message}{Colors.RESET}")


def stream_output(process, tag, color):
    """將進程的輸出串流到終端"""
    for line in iter(process.stdout.readline, b''):
        if line:
            decoded_line = line.decode('utf-8', errors='replace').rstrip()
            print(f"{color}[{tag}] {decoded_line}{Colors.RESET}")

    if process.poll() is not None:
        log(tag, f"進程已結束，返回代碼: {process.returncode}", Colors.ERROR if process.returncode != 0 else color)


def start_app(app_dir, app_name, tag, color, args):
    """啟動應用程式並返回進程對象"""
    log("系統", f"正在啟動 {app_name}...", Colors.SYSTEM)

    cmd = [sys.executable, "app.py"]

    # 添加命令列參數
    if app_name == "API" and args.api_args:
        cmd.extend(args.api_args.split())
    elif app_name == "爬蟲" and args.crawler_args:
        cmd.extend(args.crawler_args.split())

    try:
        process = subprocess.Popen(
            cmd,
            cwd=app_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=False,
            preexec_fn=os.setsid  # 使用新的進程組
        )

        # 創建新線程來處理輸出
        output_thread = threading.Thread(
            target=stream_output,
            args=(process, tag, color),
            daemon=True
        )
        output_thread.start()

        log("系統", f"{app_name} 已啟動，PID: {process.pid}", Colors.SYSTEM)
        return process, output_thread

    except Exception as e:
        log("系統", f"啟動 {app_name} 時出錯: {str(e)}", Colors.ERROR)
        return None, None


def stop_app(process, app_name):
    """停止應用程式"""
    if process and process.poll() is None:
        log("系統", f"正在停止 {app_name}...", Colors.SYSTEM)
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            # 給進程一些時間來優雅地關閉
            for _ in range(5):
                if process.poll() is not None:
                    break
                time.sleep(0.5)

            # 如果進程仍在運行，強制終止
            if process.poll() is None:
                log("系統", f"{app_name} 沒有響應，強制終止...", Colors.ERROR)
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)

            log("系統", f"{app_name} 已停止", Colors.SYSTEM)
        except Exception as e:
            log("系統", f"停止 {app_name} 時出錯: {str(e)}", Colors.ERROR)


def handle_signals(api_process, crawler_process):
    """處理終止信號"""

    def signal_handler(sig, frame):
        log("系統", "收到終止信號，正在關閉應用...", Colors.SYSTEM)
        stop_app(crawler_process, "爬蟲")
        stop_app(api_process, "API")
        log("系統", "所有應用已停止", Colors.SYSTEM)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="NTUST 英簡單系統啟動器")
    parser.add_argument("--api-only", action="store_true", help="僅啟動 API 服務")
    parser.add_argument("--crawler-only", action="store_true", help="僅啟動爬蟲服務")
    parser.add_argument("--api-args", type=str, help="傳遞給 API 應用的命令列參數")
    parser.add_argument("--crawler-args", type=str, help="傳遞給爬蟲應用的命令列參數")
    args = parser.parse_args()

    # 定義目錄路徑
    base_dir = os.path.dirname(os.path.abspath(__file__))
    api_dir = os.path.join(base_dir, "backend")
    crawler_dir = os.path.join(base_dir, "auto_fetch_practice")

    # 檢查目錄是否存在
    if not args.crawler_only and not os.path.exists(api_dir):
        log("系統", f"錯誤: API 目錄 {api_dir} 不存在", Colors.ERROR)
        return 1

    if not args.api_only and not os.path.exists(crawler_dir):
        log("系統", f"錯誤: 爬蟲目錄 {crawler_dir} 不存在", Colors.ERROR)
        return 1

    api_process = None
    crawler_process = None
    api_thread = None
    crawler_thread = None

    try:
        log("系統", "正在啟動 NTUST 英簡單系統...", Colors.SYSTEM)

        # 啟動 API 服務
        if not args.crawler_only:
            api_process, api_thread = start_app(api_dir, "API", "API", Colors.API, args)

        # 啟動爬蟲服務
        if not args.api_only:
            crawler_process, crawler_thread = start_app(crawler_dir, "爬蟲", "爬蟲", Colors.CRAWLER, args)

        # 設置信號處理
        handle_signals(api_process, crawler_process)

        # 保持主線程運行
        log("系統", "所有服務已啟動。按 Ctrl+C 停止...", Colors.SYSTEM)

        # 等待所有進程結束
        while True:
            # 檢查 API 進程
            if api_process and api_process.poll() is not None:
                log("系統", f"API 服務已意外停止，返回代碼: {api_process.returncode}",
                    Colors.ERROR if api_process.returncode != 0 else Colors.SYSTEM)
                if args.crawler_only:
                    break
                # 自動重啟 API
                log("系統", "正在重新啟動 API 服務...", Colors.SYSTEM)
                api_process, api_thread = start_app(api_dir, "API", "API", Colors.API, args)

            # 檢查爬蟲進程
            if crawler_process and crawler_process.poll() is not None:
                log("系統", f"爬蟲服務已意外停止，返回代碼: {crawler_process.returncode}",
                    Colors.ERROR if crawler_process.returncode != 0 else Colors.SYSTEM)
                if args.api_only:
                    break
                # 自動重啟爬蟲
                log("系統", "正在重新啟動爬蟲服務...", Colors.SYSTEM)
                crawler_process, crawler_thread = start_app(crawler_dir, "爬蟲", "爬蟲", Colors.CRAWLER, args)

            # 避免 CPU 使用率過高
            time.sleep(1)

    except KeyboardInterrupt:
        log("系統", "程式被手動停止", Colors.SYSTEM)
    except Exception as e:
        log("系統", f"發生未預期的錯誤: {str(e)}", Colors.ERROR)
    finally:
        # 確保所有進程在退出前停止
        stop_app(crawler_process, "爬蟲")
        stop_app(api_process, "API")
        log("系統", "所有服務已停止", Colors.SYSTEM)

    return 0


if __name__ == "__main__":
    sys.exit(main())
