import asyncio
from logging import exception
import re
from quart import Quart, request
import quart
from quart.helpers import url_for
from quart.templating import render_template
from quart.utils import redirect
import quart_auth   # type: ignore
import json
import argon2
import asyncpg
import toml

config = toml.load('config.toml')
loop = asyncio.get_event_loop()
pool = loop.run_until_complete(
    asyncpg.create_pool(
        f"postgres://postgres:{config['postgres']['password']}@localhost:5432/spot_a_fly",
        loop=loop,
    )
)
app = Quart(
    __name__, template_folder='templates'
)
app.secret_key = __import__('secrets').token_urlsafe(16)
quart_auth.AuthManager(app)


@app.route('/', methods=['GET'])
async def index():
    return "Spot-a-fly, the world's first app that lets you keep track of the flies you have spotted in your lifetime. Made by MrKomodoDragon and Jay3332."



@app.route('/login', methods=['GET', 'POST'])
async def login_():
    if request.method == "POST":
        data = await request.form
        password = data['password']
        try:
            ph = argon2.PasswordHasher()
            hash = await pool.fetchval('SELECT password from users WHERE email = $1', data['email'])
            ph.verify(hash, password)
            quart_auth.login_user(quart_auth.AuthUser(await pool.fetchval('SELECT username from users WHERE email = $1',data['email'],)))
            return quart.redirect(url_for('home'))
        except Exception as e:
            return f'Authentication failed :(. Error: {e}\n'
    return await render_template("login.html")


@app.route('/home')
@quart_auth.login_required
async def home():
    return f" Welcome, {quart_auth.current_user.auth_id}, to Spot-a-fly!"

@app.route("/sus_login", methods=["POST"])
async def sus_login():
    print(await request.form)
    return (await request.form)


app.run(loop=loop)
