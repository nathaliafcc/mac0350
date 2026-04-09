from sqlmodel import create_engine, SQLModel, Session

arquivo_sqlite = "database.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite, echo=True)

def create_db_and_tables():
    
    SQLModel.metadata.create_all(engine)

def get_session():

    with Session(engine) as session:

        yield session

        

