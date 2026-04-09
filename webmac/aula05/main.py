from fastapi import FastAPI, Request, Depends, HTTPException, status, Cookie, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# bd
usuarios_db = []

class Usuario(BaseModel):
    nome: str
    senha: str
    bio: str

# Dependência para verificar o cookie de sessão
def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    if not session_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    user = next((u for u in usuarios_db if u["nome"] == session_user), None)
    if not user:
        raise HTTPException(status_code=401)
    return user

@app.get("/")
async def pagina_registro(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

@app.post("/users")
async def criar_usuario(user: Usuario):
    usuarios_db.append(user.dict())
    return {"message": "Usuário criado com sucesso!"}

@app.get("/login")
async def pagina_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(dados: dict, response: Response):
    nome = dados.get("nome")
    senha = dados.get("senha")
    
    user = next((u for u in usuarios_db if u["nome"] == nome and u["senha"] == senha), None)
    
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    response.set_cookie(key="session_user", value=nome)
    return {"message": "Logado"}

@app.get("/home")
async def pagina_perfil(request: Request, user: dict = Depends(get_active_user)):
    return templates.TemplateResponse("perfil.html", {
        "request": request,
        "nome": user["nome"],
        "bio": user["bio"]
    })