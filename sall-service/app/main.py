from fastapi import FastAPI
from . import database, models
from .routes import router
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


app = FastAPI()

# This will ensure the database tables are created when the app starts.
@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=database.engine)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)