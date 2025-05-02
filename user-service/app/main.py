from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
import os
import secrets
import  uvicorn
from .routes import router

load_dotenv()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
GOOGLE_CLIENT_ID="265076716869-jbc2behs1oe2djbjgh25babe2t5op6d0.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"
GOOGLE_REDIRECT_URI="http://localhost:8000/auth"
oauth = OAuth()
oauth.register(
    name='google',
    client_id= GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    }
)

@app.get("/")
async def index(request: Request):
    user = request.session.get("user")
    if user:
        return HTMLResponse(f"<h1>Bienvenue {user['email']}</h1>")
    return HTMLResponse('<a href="/oauth/google">Connexion avec Google</a>')

@app.get("/oauth/google")
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/oauth/google/authorized" , name="auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = await oauth.google.parse_id_token(request, token)
        request.session["user"] = dict(user)
        return RedirectResponse(url="/")
    except Exception as e:
        print("Erreur d'authentification :", e)
        return HTMLResponse("<h1>Erreur lors de la connexion.</h1>", status_code=500)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

app.include_router(router)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)