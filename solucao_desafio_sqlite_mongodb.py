"""
Script para solução do desafio
"""
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String, Float
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session


Base = declarative_base()


class Cliente(Base):
    """
    Dados do cliente
    """
    __tablename__ = 'cliente'

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    cpf = Column(String)
    endereco = Column(String)
    conta = relationship("Conta", backref="cliente")

    def __repr__(self):
        return f"Cliente(id={self.id}, nome={self.nome}, cpf={self.cpf})"


class Conta(Base):
    """
    Dados da conta
    """
    __tablename__ = 'conta'

    id = Column(Integer, primary_key=True)
    tipo = Column(String, nullable=False)
    agencia = Column(String, nullable=False)
    num = Column(Integer)
    saldo = Column(Float)
    cliente_id = Column(ForeignKey("cliente.id"))

    def __repr__(self):
        return f"Conta(id={self.id}, agencia={self.agencia}, num={self.num})"


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)

with Session(engine) as session:
    marley = Cliente(
        nome='Marley Adriano',
        cpf='65101537691',
        endereco='Rua são Tarcisio, 201 - Presidente Kennedy - Betim/MG',
        conta=[
            Conta(tipo='conta corrente', agencia='0001', num=28873, saldo=0.0),
            Conta(tipo='conta poupança', agencia='0001', num=18873, saldo=1050.90)
        ]
    )
    adriana = Cliente(
        nome='Adriana Ferreira',
        cpf='96888237672',
        endereco='Rua são Tarcisio, 201 - Presidente Kennedy - Betim/MG',
        conta=[Conta(tipo='conta corrente', agencia='0001', num=22572, saldo=0.0)]
    )
    andreia = Cliente(
        nome='Andreia Porto',
        cpf='04499866677',
        endereco='Rua são Tarcisio, 201 - Presidente Kennedy - Betim/MG',
        conta=[Conta(tipo='conta corrente', agencia='0002', num=21452, saldo=0.0)]
    )
    session.add_all([marley, adriana, andreia])
    session.commit()

print("Recuperando os clientes cadastrados e suas respecitvas contas")
order_stmt = select(Cliente).order_by(Cliente.nome.desc())
for result in session.scalars(order_stmt):
    print(result, result.conta)
