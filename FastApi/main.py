from fastapi import FastAPI
from routers import users
from fastapi.staticfiles import  StaticFiles
app = FastAPI()
app.include_router(users.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def raiz():
    return "Welcome to the page"


