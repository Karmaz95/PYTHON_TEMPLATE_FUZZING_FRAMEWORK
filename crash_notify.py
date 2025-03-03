import os
import time
import requests

def is_pid_alive(pid):
    """Check if a PID is alive."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True

def send_telegram_message(bot_token, chat_id, message):
    """Send a Telegram message using the bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")

def monitor_pid(pid, bot_token, chat_id, check_interval=1):
    """
    Monitor the given PID. Send a Telegram message when the process dies.

    Args:
    pid (int): Process ID to monitor.
    bot_token (str): Telegram bot token.
    chat_id (str): Chat ID to send the message.
    check_interval (int): Time interval (in seconds) between checks.
    """
    print(f"Monitoring PID {pid}...")
    while True:
        if not is_pid_alive(pid):
            message = f"Alert: Process with PID {pid} has terminated."
            print(message)
            send_telegram_message(bot_token, chat_id, message)
            break
        time.sleep(check_interval)

if __name__ == "__main__":
    pid_to_monitor = 94022
    bot_token = "1234567890:AAAAAAA"
    chat_id = 123456789
    monitor_pid(pid_to_monitor, bot_token, chat_id)
