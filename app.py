import json
from urllib.parse import quote_plus, urlencode

from os import environ as env
from dotenv import load_dotenv, find_dotenv

from flask import Flask, url_for, session, redirect, render_template
from authlib.integrations.flask_client import OAuth

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Main Application Call
app = Flask(__name__, template_folder='templates')
app.secret_key = env.get('APP_SECRET_KEY')

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect( #type: ignore
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=['GET', 'POST'])
def callback():
    token = oauth.auth0.authorize_access_token() #type: ignore
    session['user'] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN") #type: ignore
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/")
def home():
    return render_template("home.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
