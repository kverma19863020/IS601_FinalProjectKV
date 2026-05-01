from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.database import Base, engine
from app.models import user, calculation  # noqa: import to register models
from app.routers import auth, calculations as calc_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Calculations App")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(calc_router.router)

templates = Jinja2Templates(directory="templates")

@app.get("/")
def root():
    return RedirectResponse("/calculations")
