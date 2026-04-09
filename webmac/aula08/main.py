from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

app = FastAPI()
templates = Jinja2Templates(directory="templates")

curtidas_db = {"total": 0}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"pagina": "/aba-curtidas"}
    )

@app.post("/curtir", response_class=HTMLResponse)
async def curtir(request: Request, acao: Optional[str] = None):
    if acao == "reset":
        curtidas_db["total"] = 0
    else:
        curtidas_db["total"] += 1
    return templates.TemplateResponse(
        request=request, 
        name="curtidas.html", 
        context={"curtidas": curtidas_db["total"]}
    )

@app.get("/aba-curtidas", response_class=HTMLResponse)
async def aba_curtidas(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="curtidas.html", 
        context={"curtidas": curtidas_db["total"]}
    )

@app.get("/aba-jupiter", response_class=HTMLResponse)
async def aba_jupiter(request: Request):
    return templates.TemplateResponse(request=request, name="jupiter.html")

@app.get("/aba-professor", response_class=HTMLResponse)
async def aba_professor(request: Request):
    return templates.TemplateResponse(request=request, name="professor.html")