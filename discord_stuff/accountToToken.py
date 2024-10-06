import requests, json

print("Discord - Log in")
email = str(input("email: "))
password = str(input("password: "))

headers = {
    "Content-Type": "application/json"
}

payload = {
    #"gift_code_sku_id": None,
    "login": email,
    #"login_source": None,
    "password": password,
    #"undelete": False
}

login_request = requests.post("https://discord.com/api/v9/auth/login", headers=headers, data=json.dumps(payload))

# Response should look like this
{
    "user_id": "",      # A ~18 digits long number formatted as str
    "token": "",        # A long string
    "user_settings": {
        "locale": "en-US",
        "theme": "dark"
    }
}

print(login_request.json())

token = login_request.json()["token"]
