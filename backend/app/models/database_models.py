import enum
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, Numeric, DateTime, Enum, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class StatusMesa(enum.Enum):
    LIVRE = "livre"
    OCUPADA = "ocupada"
    RESERVADA = "reservada"

class StatusComanda(enum.Enum):
    ATIVA = "ativa"
    PAGA = "paga"
    EXTRAVIADA = "extraviada"

class StatusItem(enum.Enum):
    PENDENTE = "pendente"    # Enviado para a cozinha/bar
    EM_PREPARO = "em_preparo"# Auxiliar/Barman aceitou o preparo
    PRONTO = "pronto"        # Pronto para o garçom entregar
    ENTREGUE = "entregue"    # Já na mesa do cliente

class CategoriaProduto(enum.Enum):
    PORCAO = "porcao"
    HAMBURGUER = "hamburguer"
    PRATO = "prato"
    CHURRASCO = "churrasco"
    ESPETINHO = "espetinho"
    FEIJOADA = "feijoada"
    BEBIDA = "bebida"

class Mesa(Base):
    __tablename__ = "mesas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_identificador: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    status: Mapped[StatusMesa] = mapped_column(Enum(StatusMesa), default=StatusMesa.LIVRE)
    
    # Campo chave para o agrupamento flexível: armazena o ID da mesa 'mãe' quando unidas
    mesa_pai_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("mesas.id"), nullable=True)
    
    # Relacionamento de auto-referência para junção de mesas
    mesas_filhas: Mapped[List["Mesa"]] = relationship("Mesa", back_populates="mesa_pai")
    mesa_pai: Mapped[Optional["Mesa"]] = relationship("Mesa", remote_side=[id], back_populates="mesas_filhas")
    
    pedidos: Mapped[List["Pedido"]] = relationship("Pedido", back_populates="mesa")

class Comanda(Base):
    __tablename__ = "comandas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_pvc: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)  # Número impresso no cartão PVC
    status: Mapped[StatusComanda] = mapped_column(Enum(StatusComanda), default=StatusComanda.ATIVA)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fechado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    pedidos: Mapped[List["Pedido"]] = relationship("Pedido", back_populates="comanda")

class Produto(Base):
    __tablename__ = "produtos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    preco: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    categoria: Mapped[CategoriaProduto] = mapped_column(Enum(CategoriaProduto), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True) # Cardápio dinâmico: ativa/desativa itens sem apagar

    itens_pedido: Mapped[List["ItemPedido"]] = relationship("ItemPedido", back_populates="produto")

class Pedido(Base):
    __tablename__ = "pedidos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mesa_id: Mapped[int] = mapped_column(Integer, ForeignKey("mesas.id"), nullable=False)
    comanda_id: Mapped[int] = mapped_column(Integer, ForeignKey("comandas.id"), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    mesa: Mapped["Mesa"] = relationship("Mesa", back_populates="pedidos")
    comanda: Mapped["Comanda"] = relationship("Comanda", back_populates="pedidos")
    
    # Relacionamento de composição: Um pedido possui vários itens
    itens: Mapped[List["ItemPedido"]] = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")

class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pedido_id: Mapped[int] = mapped_column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id: Mapped[int] = mapped_column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, default=1)
    observacao: Mapped[Optional[str]] = mapped_column(String(200), nullable=True) # Ex: "Sem cebola", "Gelo e limão"
    status: Mapped[StatusItem] = mapped_column(Enum(StatusItem), default=StatusItem.PENDENTE)
    
    pedido: Mapped["Pedido"] = relationship("Pedido", back_populates="itens")
    produto: Mapped["Produto"] = relationship("Produto", back_populates="itens_pedido")


class Insumo(Base):
    __tablename__ = "insumos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    quantidade_atual: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    quantidade_minima: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    data_validade: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    congelado: Mapped[bool] = mapped_column(Boolean, default=False)


#class Pedido(Base):
#    __tablename__ = "pedidos"
#
#    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#    mesa_id: Mapped[int] = mapped_column(Integer, ForeignKey("mesas.id"), nullable=False)
#    comanda_id: Mapped[int] = mapped_column(Integer, ForeignKey("comandas.id"), nullable=False)
#    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
#    
#    mesa: Mapped["Mesa"] = relationship("Mesa", back_populates="pedidos")
#    comanda: Mapped["Comanda"] = relationship("Comanda", back_populates="pedidos")
