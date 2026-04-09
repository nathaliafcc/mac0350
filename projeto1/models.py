from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

#os dados principais como sexo, mao dominante (etc serao utilizados em atualizacoes posteriores caso haja tempo habil para tal )

class Jogador(SQLModel, table=True):
    nusp: int = Field(primary_key=True)
    nome: str
    idade: int = Field(ge=1)
    sexo: str
    mao_dominante: str
    pontos_totais:int = Field(default=0)
    vitorias: List["Partida"] = Relationship(
        back_populates="vencedor",
        sa_relationship_kwargs={"primaryjoin": "Jogador.nusp==Partida.vencedor_id"}
    )
    derrotas: List["Partida"] = Relationship(
        back_populates="perdedor",
        sa_relationship_kwargs={"primaryjoin": "Jogador.nusp==Partida.perdedor_id"}
    )
    


class Partida(SQLModel, table=True):
    
    id_partida: Optional[int] = Field(default=None, primary_key=True)
    placar: str
    
    vencedor_id: int = Field(foreign_key="jogador.nusp")
    perdedor_id: int = Field(foreign_key="jogador.nusp")


    vencedor: Optional["Jogador"] = Relationship(
        back_populates="vitorias",
        sa_relationship_kwargs={"foreign_keys": "[Partida.vencedor_id]"}
    )
    perdedor: Optional["Jogador"] = Relationship(
        back_populates="derrotas",
        sa_relationship_kwargs={"foreign_keys": "[Partida.perdedor_id]"}
    )

    
    