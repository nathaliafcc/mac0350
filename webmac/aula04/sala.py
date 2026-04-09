# Arquivo main.py

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

# aramazena users
usuarios = []

class Usuario(BaseModel):
    nome: str
    idade: int

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # le arq html 
    with open("sala_ht.html", "r", encoding="utf-8") as arquivo:
        html_content = arquivo.read()
    return html_content

@app.post("/users")
async def create_user(user: Usuario):
    usuarios.append(user)
    return usuarios

@app.get("/users")
async def get_users(index: int | None = None):
    # retorna index se existir usuario com esse inedex
    if index is not None:
        if 0 <= index < len(usuarios):
            return usuarios[index]
        return {"erro": "Índice inválido"}
    #caso nao tenha, retorna todos
    return usuarios

@app.delete("/users")
async def delete_users():
    usuarios.clear()
    return usuarios