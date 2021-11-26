import asyncio
from logging import exception
from quart import Quart, request
import quart_auth #type: ignore
import json
import argon2
import asyncpg
import toml
thing = toml.load("config.toml")
loop = asyncio.get_event_loop()
pool = loop.run_until_complete(asyncpg.create_pool(f"postgres://postgres:{thing['postgres']['password']}@localhost:5432/spot_a_fly", loop=loop))
app = Quart(__name__, )
app.secret_key = __import__("secrets").token_urlsafe(16)
quart_auth.AuthManager(app)

@app.route('/', methods=["GET"])
async def index():
	return "Spot-a-fly, the world's first app that lets you keep track of the flies you have spotted in your lifetime. Made by MrKomodoDragon and Jay3332."
@app.route('/login', methods=['GET'])
async def login():
	data = request.args
	password = data['password']
	try:
		ph = argon2.PasswordHasher()
		hash = await pool.fetchval("SELECT password from users WHERE email = $1", data['email'])
		ph.verify(hash, password)
		quart_auth.login_user(quart_auth.AuthUser(await pool.fetchval("SELECT username from users WHERE email = $1", data['email'])))
		return "Logged in"
	except Exception as e:
		return f"Authentication failed :(. Error: {e}\n"
@app.route("/username")
@quart_auth.login_required
async def username():
	return quart_auth.current_user.auth_id

app.run(loop=loop)
