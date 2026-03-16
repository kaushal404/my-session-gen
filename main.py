import os
from flask import Flask, render_template, request, jsonify
from hydrogram import Client
import asyncio

app = Flask(__name__)

API_ID = 31517555
API_HASH = "6c80b37a22ac50276a4e9e26abaacdbd"

clients = {}

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    phone = request.json.get("phone")
    async def logic():
        client = Client(":memory:", API_ID, API_HASH)
        await client.connect()
        code = await client.send_code(phone)
        clients[phone] = {"client": client, "hash": code.phone_code_hash}
        return {"status": "success"}
    return jsonify(run_async(logic()))

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.json
    phone, otp = data.get("phone"), data.get("otp")
    async def logic():
        client = clients[phone]["client"]
        await client.sign_in(phone, clients[phone]["hash"], otp)
        string = await client.export_session_string()
        return {"status": "success", "string": string}
    return jsonify(run_async(logic()))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
