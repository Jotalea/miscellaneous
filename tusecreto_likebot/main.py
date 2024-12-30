import requests
import time

logo = """
  _______        _____                         _         
 |__   __|      / ____|                       | |        
    | | _   _  | (___    ___   ___  _ __  ___ | |_  ___  
    | || | | |  \___ \  / _ \ / __|| '__|/ _ \| __|/ _ \ 
    | || |_| |  ____) ||  __/| (__ | |  |  __/| |_| (_) |
    |_| \__,_| |_____/  \___| \___||_|   \___| \__|\___/ 
   _       _  _          _             _                 
  | |     (_)| |        | |           | |                
  | |      _ | | __ ___ | |__    ___  | |_               
  | |     | || |/ // _ \| '_ \  / _ \ | __|              
  | |____ | ||   <|  __/| |_) || (_) || |_               
  |______||_||_|\_\\___||_.__/  \___/  \__|              
                                                         
                                                         """
print(logo)

try:
    postid = int(input("Pega la ID del post: ")) # 81963915
    amount = int(input("Cuantos likes: "))
    atoken = str(input("Token de autorización: "))
except Exception as e:
    exit()

url = f'https://tusecreto.io/api/secrets/{postid}/upvote'

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json',
    'Content-Type': 'application/json;charset=utf-8',
    'x-access-token': atoken
}

error_count = 0

for i in range(amount):
    try:
        # Make the POST request to upvote
        response = requests.post(url, headers=headers, json={}, timeout=10)
        
        if response.status_code == 200:
            print(f"{i} {'like' if i <= 1 else 'likes'}")
        else:
            print(f"Error: {response.status_code}")
    
    except Exception as e:
        error_count += 1
        print(f"Error: {e}")
        if error_count > 5:
            break# out of the loop if there's an error
