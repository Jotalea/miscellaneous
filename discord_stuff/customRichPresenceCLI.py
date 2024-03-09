from discordrp import Presence
import time

client_id = "1082768804217639032"

with Presence(client_id) as presence:
    print("Connected")
    presence.set(
        {
            "state": "Playing GDRMK",
            "timestamps": {"Started": int(time.time())},
        }
    )
    print("Presence updated")

    while True:
        time.sleep(15)