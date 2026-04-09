from models import Jogador, Partida
from fastapi import FastAPI, Request
from database import engine, create_db_and_tables
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Form, Depends
from sqlmodel import Session
from database import get_session 
from sqlmodel import select
from fastapi.responses import HTMLResponse

app = FastAPI()

create_db_and_tables()


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_ranking(request: Request, session: Session = Depends(get_session)):
    # Mantemos a lógica de buscar por pontos para a Home
    statement = select(Jogador).order_by(Jogador.pontos_totais.desc())
    jogadores = session.exec(statement).all()
    
    return templates.TemplateResponse(
        request=request, 
        name="ranking.html", 
        context={"jogadores": jogadores}
    )

@app.get("/cadastro")
def view_cadastro(request: Request):
    # Página limpa apenas para o formulário de novos atletas
    return templates.TemplateResponse(
        request=request, 
        name="cadastro.html"
    )

@app.get("/partida")
def view_partida(request: Request, session: Session = Depends(get_session)):
    # IMPORTANTE: Aqui precisamos dos jogadores para preencher os selects
    jogadores = session.exec(select(Jogador)).all()
    return templates.TemplateResponse(
        request=request, 
        name="partida.html", 
        context={"jogadores": jogadores}
    )

@app.post("/jogadores")
def cadastrar_jogador(
    nome: str = Form(...), 
    nusp: int = Form(...),
    idade: int = Form(...), 
    sexo: str = Form(...), 
    mao_dominante: str = Form(...),
    session: Session = Depends(get_session)
):
    # Cria o jogador
    novo_jogador = Jogador(
        nome=nome, 
        nusp = nusp,
        idade=idade, 
        sexo=sexo, 
        mao_dominante=mao_dominante
    )
    
    jogador_existente = session.get(Jogador, nusp)

    #vericacao: se o NUSP ja estiver sendo usado, da erro
    if jogador_existente:
    # Retorne um erro para o HTMX injetar na div #mensagem
        return f"<p style='color: red;'>Erro: O NUSP {nusp} já pertence ao atleta {jogador_existente.nome}!</p>"

    session.add(novo_jogador)
    session.commit()
    session.refresh(novo_jogador)
    
    # mensagem de sucesso
    return f"<p style='color: green;'>Jogador {nome} cadastrado com sucesso!</p>"

# colocandi vitoria no bd
@app.post("/partidas")
def registrar_partida(
    vencedor_nusp: int = Form(...), 
    perdedor_nusp: int = Form(...), 
    placar: str = Form(...),
    session: Session = Depends(get_session)
):
    # caso o perdedor seja igual o vencedor: erro
    if vencedor_nusp == perdedor_nusp:
        return "<p style='color: red; background: #ffebee; padding: 10px; border-radius: 5px;'>Erro: Um jogador não pode enfrentar a si mesmo</p>"

    # Busca os objetos completos no banco
    vencedor = session.get(Jogador, vencedor_nusp)
    perdedor = session.get(Jogador, perdedor_nusp)

    if not vencedor or not perdedor:
        return "<p style='color: red;'>Erro: Jogador não encontrado.</p>"

    # ganhador ganha 10 pontos
    vencedor.pontos_totais += 10
    
    # cria historico de partida (nao deu para implementar o historico)
    nova_partida = Partida(
        placar=placar, 
        vencedor_id=vencedor_nusp, 
        perdedor_id=perdedor_nusp
    )
    
    session.add(nova_partida)
    session.add(vencedor) # atualiza os pontos
    session.commit() 
    
    return f"<p style='color: #2d6a4f; background: #e8f5e9; padding: 10px; border-radius: 5px;'> Registrado!  {vencedor.nome} agora tem {vencedor.pontos_totais} pontos! </p>"

@app.get("/buscar")
def buscar_jogador(q: str, session: Session = Depends(get_session)):
    # Busca quem tem o texto digitado no nome
    statement = select(Jogador).where(Jogador.nome.contains(q)).order_by(Jogador.pontos_totais.desc())
    jogadores = session.exec(statement).all()
    
    # Retorna APENAS as linhas da tabela (HTMX style)
    html_linhas = ""
    for i, j in enumerate(jogadores):
        html_linhas += f"<tr><td>{i+1}º</td><td>{j.nome}</td><td>{j.pontos_totais}</td><td>{j.mao_dominante}</td></tr>"
    
    return HTMLResponse(content=html_linhas)

@app.delete("/jogadores/{nusp}")
def deletar_jogador(nusp: int, session: Session = Depends(get_session)):
    jogador = session.get(Jogador, nusp)
    if jogador:
        session.delete(jogador)
        session.commit()
    return "" 

@app.put("/jogadores/{nusp}/aniversario")
def fazer_aniversario(nusp: int, session: Session = Depends(get_session)):
    jogador = session.get(Jogador, nusp)
    if jogador:
        jogador.idade += 1
        session.add(jogador)
        session.commit()
    return ""

