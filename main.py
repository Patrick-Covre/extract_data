from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from app.routers import upload_files

templates = Jinja2Templates(directory="templates")

app = FastAPI()

@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})
app.include_router(upload_files.router)
