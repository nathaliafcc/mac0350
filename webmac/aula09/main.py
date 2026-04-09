from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from Models import Aluno
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, create_engine, Session, select, col, func

@asynccontextmanager
async def initFunction(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=initFunction)
app.mount("/static", StaticFiles(directory="static"), name="static")

arquivo_sqlite = "HTMX2.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"
engine = create_engine(url_sqlite)
templates = Jinja2Templates(directory="templates")

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.get("/", response_class=HTMLResponse)
@app.get("/busca", response_class=HTMLResponse)
def busca(request: Request):
    return templates.TemplateResponse(request, "index.html", {"pagina": "/lista"})

@app.get("/lista", response_class=HTMLResponse)
def lista(request: Request, busca: str = '', p: int = 1):
    limit = 10
    offset = (p - 1) * limit
    
    with Session(engine) as session:
        # Busca paginada
        query = select(Aluno).where(col(Aluno.nome).contains(busca)).order_by(Aluno.nome).offset(offset).limit(limit)
        alunos = session.exec(query).all()
        
        # Contagem total para lógica de botões
        total_query = select(func.count(Aluno.id)).where(col(Aluno.nome).contains(busca))
        total_alunos = session.exec(total_query).one()
        
        tem_proximo = (offset + limit) < total_alunos
        tem_anterior = p > 1
        
    return templates.TemplateResponse(request, "lista.html", {
        "alunos": alunos, 
        "busca": busca, 
        "p": p, 
        "tem_proximo": tem_proximo, 
        "tem_anterior": tem_anterior
    })

@app.get("/editarAlunos")
def novo_aluno_page(request: Request):
    return templates.TemplateResponse(request, "options.html")

@app.post("/novoAluno", response_class=HTMLResponse)
def criar_aluno(nome: str = Form(...)):
    with Session(engine) as session:
        novo_aluno = Aluno(nome=nome)
        session.add(novo_aluno)
        session.commit()
        session.refresh(novo_aluno)
        return HTMLResponse(content=f"<p>O(a) aluno(a) {novo_aluno.nome} foi registrado(a)!</p>")

@app.delete("/deletaAluno", response_class=HTMLResponse)
def deletar_aluno(id: int):
    with Session(engine) as session:
        aluno = session.get(Aluno, id)
        if not aluno:
            raise HTTPException(404, "Aluno não encontrado")
        session.delete(aluno)
        session.commit()
        return HTMLResponse(content=f"<p>ID {id} deletado com sucesso.</p>")

@app.delete("/apagar", response_class=HTMLResponse)
def apagar():
    return ""