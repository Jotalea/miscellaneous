from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_post_request():
    data = request.data.decode('utf-8')  # Decode the received data
    print("Received POST request data:")
    print(data)
    return "POST request data received and printed on the server."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # Run the server on all available network interfaces
