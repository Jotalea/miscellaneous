import requests

# Replace with your bot token, server ID and emoji name
token = ''
guild_id = ''
emoji_name = 'thumbs_up'

# Build the URL to get information about server emojis
url = f'https://discord.com/api/v9/guilds/{guild_id}/emojis'

# Make the GET request to Discord's API
headers = {'Authorization': f'Bot {token}'}
response = requests.get(url, headers=headers)

# If the request was successfull
if response.status_code == 200:
    emojis = response.json()
    for emoji in emojis:
        if emoji['name'] == emoji_name:
            emoji_id = emoji['id']
            print(f"ID for '{emoji_name}' emoji: {emoji_id}")
            break
    else:
        print(f"No emoji called '{emoji_name}' found in the server.")
else:
    print(f"Error when making the request: {response.status_code} - {response.text}")
