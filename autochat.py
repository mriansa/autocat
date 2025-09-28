import requests
import json
import time
import random
from threading import Thread
from googletrans import Translator

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def get_messages_from_file():
    try:
        with open("chat.txt", "r") as file:
            messages = [line.strip() for line in file if line.strip()]
            return messages
    except FileNotFoundError:
        print(f"{Colors.RED}Tệp chat.txt không tồn tại!{Colors.RESET}")
        return []

def translate_message(message, target_lang):
    if target_lang == "auto": 
        return message
    translator = Translator()
    try:
        translated = translator.translate(message, dest=target_lang)
        return translated.text
    except Exception as e:
        print(f"{Colors.RED}Không thể dịch tin nhắn: {e}{Colors.RESET}")
        return message

def delete_message(channel_id, message_id, authorization, message_content):
    header = {
        "Authorization": authorization,
        "Content-Type": "application/json",
    }
    time.sleep(delete_time)  # Đợi thời gian xóa
    try:
        res = requests.delete(f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}", headers=header)
        if res.status_code == 204:
            print(f"{Colors.RED}Đã xoá tin nhắn: {Colors.YELLOW}\'{message_content}\'{Colors.RED} thành công!{Colors.RESET}")
        else:
            print(f"{Colors.RED}Không thể xoá tin nhắn {Colors.YELLOW}{message_id}{Colors.RED}. Mã trạng thái: {res.status_code}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Lỗi khi xoá tin nhắn {Colors.YELLOW}{message_id}{Colors.RED}: {e}{Colors.RESET}")

def send_message(channel_id, message, authorization, target_lang, auto_delete):
    header = {
        "Authorization": authorization,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    }
    translated_message = translate_message(message, target_lang)
    msg = {
        "content": translated_message,
        "nonce": "82329451214{}33232234".format(random.randrange(0, 1000)),
        "tts": False,
    }
    discord_url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    try:
        res = requests.post(url=discord_url, headers=header, data=json.dumps(msg))
        if res.status_code == 200:
            message_id = res.json()["id"]
            print(f"{Colors.GREEN}Đã gửi tin nhắn: {Colors.YELLOW}'{translated_message}'{Colors.GREEN} thành công!{Colors.RESET}")
            if auto_delete:
                Thread(target=delete_message, args=(channel_id, message_id, authorization, translated_message)).start()
        else:
            print(f"{Colors.RED}Kiểm tra lại token {authorization[:10]} (Mã trạng thái: {res.status_code}){Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Lỗi với token {authorization[:10]}: {e}{Colors.RESET}")

if __name__ == "__main__":
    channels = ["1260240731726151721"]  # Discord Channel ID
    messages = get_messages_from_file()
    if not messages:
        exit()

    try:
        with open("token.txt", "r") as file:
            tokens = [line.strip() for line in file.readlines() if line.strip()]
        
        target_language = input("Chọn ngôn ngữ (mặc định là Vi): ").strip()
        if not target_language:
            target_language = "vi"

        delay_between_messages = input("Khoảng thời gian giữa các tin nhắn (mặc định 25-30 giây): ").strip()
        delay_between_messages = random.randint(25, 30) if not delay_between_messages.isdigit() else int(delay_between_messages)

        auto_delete = input("Bạn có muốn tự động xoá tin nhắn không? (yes hoặc no): ").strip().lower() == "yes"
        global delete_time
        delete_time = 10
        if auto_delete:
            delete_time_input = input("Bạn muốn xoá tin nhắn sau bao lâu? (mặc định 10 giây): ").strip()
            delete_time = 10 if not delete_time_input.isdigit() else int(delete_time_input)

        failed_tokens = []

        while True:
            try:
                for token in tokens:
                    for message in messages:
                        for channel_id in channels:
                            send_message(channel_id, message, token, target_language, auto_delete)
                        time.sleep(delay_between_messages)
            except KeyboardInterrupt:
                print(f"{Colors.RED}\nĐã dừng gửi tin nhắn!{Colors.RESET}")
                break
    except FileNotFoundError:
        print(f"{Colors.RED}Tệp token.txt không tồn tại. Vui lòng tạo tệp và thêm token Discord của bạn.{Colors.RESET}")