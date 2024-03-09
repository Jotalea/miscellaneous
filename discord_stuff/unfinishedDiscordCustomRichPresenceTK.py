import tkinter as tk
import time
from tkinter import messagebox
from discordrp import Presence

def update_presence():
    client_id = client_id_entry.get()
    client_state = client_state_entry.get()
    client_details = client_details_entry.get()
    option_assets = option_assets_var.get()
    option_party = option_party_var.get()

    if option_assets == "Yes":
        client_asset_large = client_asset_large_entry.get()
        client_asset_small = client_asset_small_entry.get()
    else:
        client_asset_large = None
        client_asset_small = None

    if option_party == "Yes":
        party_id = party_id_entry.get()
        party_size = party_size_entry.get()
        party_max = party_max_entry.get()
        join_secret = join_secret_entry.get()
    else:
        party_id = None
        party_size = None
        party_max = None
        join_secret = None

    with Presence(client_id) as presence:
        presence_data = {
            "state": client_state,
            "details": client_details,
            "timestamps": {"start": int(time.time())},
            "assets": {
                "large_image_text": client_asset_large,
                "small_image_text": client_asset_small
            } if option_assets == "Yes" else {},
            "party": {
                "id": party_id,
                "size": int(party_size),
                "max": int(party_max),
                "join_secret": join_secret
            } if option_party == "Yes" else {}
        }

        presence.set(presence_data)
        messagebox.showinfo("Presence Updated", "Discord Rich Presence has been updated successfully.")

app = tk.Tk()
app.title("Discord Rich Presence Setup")
app.geometry("460x450")

welcome_label = tk.Label(app, text="Welcome to Jotalea's custom Discord Rich Presence for Linux!", padx=10, pady=10)
welcome_label.place(x=5, y=5, width=410, height=30)

client_id_label = tk.Label(app, text="Discord Application ID:")
client_id_label.place(x=5, y=35, height=30)
client_id_entry = tk.Entry(app)
client_id_entry.place(x=175, y=35, width=260, height=30)

client_state_label = tk.Label(app, text="Rich Presence state:")
client_state_label.place(x=5, y=70, height=30)
client_state_entry = tk.Entry(app)
client_state_entry.place(x=175, y=70, width=260, height=30)

client_details_label = tk.Label(app, text="Rich Presence details:")
client_details_label.place(x=5, y=105, height=30)
client_details_entry = tk.Entry(app)
client_details_entry.place(x=175, y=105, width=260, height=30)

option_assets_label = tk.Label(app, text="Custom images in your CRP?")
option_assets_label.place(x=5, y=140, height=30)
option_assets_var = tk.StringVar()
option_assets_var.set("No")
option_assets_radio_yes = tk.Radiobutton(app, text="Yes", variable=option_assets_var, value="Yes")
option_assets_radio_no = tk.Radiobutton(app, text="No", variable=option_assets_var, value="No")
option_assets_radio_yes.place(x=205, y=140, width=60, height=30)
option_assets_radio_no.place(x=270, y=140, width=60, height=30)

client_asset_large_label = tk.Label(app, text="Large image asset name:")
client_asset_large_label.place(x=5, y=175, height=30)
client_asset_large_entry = tk.Entry(app)
client_asset_large_entry.place(x=175, y=175, width=260, height=30)

client_asset_small_label = tk.Label(app, text="Small image asset name:")
client_asset_small_label.place(x=5, y=210, height=30)
client_asset_small_entry = tk.Entry(app)
client_asset_small_entry.place(x=175, y=210, width=260, height=30)

option_party_label = tk.Label(app, text="Custom party in your CRP?")
option_party_label.place(x=5, y=245, height=30)
option_party_var = tk.StringVar()
option_party_var.set("No")
option_party_radio_yes = tk.Radiobutton(app, text="Yes", variable=option_party_var, value="Yes")
option_party_radio_no = tk.Radiobutton(app, text="No", variable=option_party_var, value="No")
option_party_radio_yes.place(x=205, y=245, width=60, height=30)
option_party_radio_no.place(x=270, y=245, width=60, height=30)

party_id_label = tk.Label(app, text="Party ID:")
party_id_label.place(x=5, y=280, height=30)
party_id_entry = tk.Entry(app)
party_id_entry.place(x=175, y=280, width=260, height=30)

party_size_label = tk.Label(app, text="Party size:")
party_size_label.place(x=5, y=310, height=30)
party_size_entry = tk.Entry(app)
party_size_entry.place(x=175, y=310, width=260, height=30)

party_max_label = tk.Label(app, text="Maximum party size:")
party_max_label.place(x=5, y=345, height=30)
party_max_entry = tk.Entry(app)
party_max_entry.place(x=175, y=345, width=260, height=30)

join_secret_label = tk.Label(app, text="Join secret:")
join_secret_label.place(x=5, y=380, height=30)
join_secret_entry = tk.Entry(app)
join_secret_entry.place(x=175, y=380, width=260, height=30)

update_button = tk.Button(app, text="Update Presence", command=update_presence)
update_button.place(x=5, y=415, width=160, height=30)

app.mainloop()

