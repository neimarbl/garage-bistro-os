# backend/app/models/database_models.py
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
    PENDENTE = "pendente"
    EM_PREPARO = "em_preparo"
    PRONTO = "pronto"
    ENTREGUE = "entregue"

class OrigemPedido(enum.Enum):
    GARCON = "garcon"
    AUTOATENDIMENTO = "autoatendimento"

class StatusChamado(enum.Enum):
    ABERTO = "aberto"
    ATENDIDO = "atendido"

class MetodoPagamento(enum.Enum):
    DINHEIRO = "dinheiro"
    PIX = "pix"
    DEBITO = "debito"
    CREDITO = "credito"

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
    mesa_pai_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("mesas.id"), nullable=True)
    
    mesas_filhas: Mapped[List["Mesa"]] = relationship("Mesa", back_populates="mesa_pai")
    mesa_pai: Mapped[Optional["Mesa"]] = relationship("Mesa", remote_side=[id], back_populates="mesas_filhas")
    pedidos: Mapped[List["Pedido"]] = relationship("Pedido", back_populates="mesa")
    chamados: Mapped[List["ChamadoAtendimento"]] = relationship("ChamadoAtendimento", back_populates="mesa")

class Comanda(Base):
    __tablename__ = "comandas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_pvc: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    status: Mapped[StatusComanda] = mapped_column(Enum(StatusComanda), default=StatusComanda.ATIVA)
    token_sessao: Mapped[str] = mapped_column(String(255), nullable=False) # Token automático de segurança contra fraudes no QR Code
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fechado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    pedidos: Mapped[List["Pedido"]] = relationship("Pedido", back_populates="comanda")
    pagamentos: Mapped[List["PagamentoParcial"]] = relationship("PagamentoParcial", back_populates="comanda")

class Produto(Base):
    __tablename__ = "produtos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    preco: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    categoria: Mapped[CategoriaProduto] = mapped_column(Enum(CategoriaProduto), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    itens_pedido: Mapped[List["ItemPedido"]] = relationship("ItemPedido", back_populates="produto")

class Pedido(Base):
    __tablename__ = "pedidos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mesa_id: Mapped[int] = mapped_column(Integer, ForeignKey("mesas.id"), nullable=False)
    comanda_id: Mapped[int] = mapped_column(Integer, ForeignKey("comandas.id"), nullable=False)
    origem: Mapped[OrigemPedido] = mapped_column(Enum(OrigemPedido), default=OrigemPedido.GARCON) # Garçom ou Cliente
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    mesa: Mapped["Mesa"] = relationship("Mesa", back_populates="pedidos")
    comanda: Mapped["Comanda"] = relationship("Comanda", back_populates="pedidos")
    itens: Mapped[List["ItemPedido"]] = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")

class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pedido_id: Mapped[int] = mapped_column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id: Mapped[int] = mapped_column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, default=1)
    observacao: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    status: Mapped[StatusItem] = mapped_column(Enum(StatusItem), default=StatusItem.PENDENTE)
    
    pedido: Mapped["Pedido"] = relationship("Pedido", back_populates="itens")
    produto: Mapped["Produto"] = relationship("Produto", back_populates="itens_pedido")

# 🆕 NOVA TABELA PARA PAGAMENTOS FRACIONADOS E PARCIAIS
class PagamentoParcial(Base):
    __tablename__ = "pagamentos_parciais"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comanda_id: Mapped[int] = mapped_column(Integer, ForeignKey("comandas.id"), nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    metodo: Mapped[MetodoPagamento] = mapped_column(Enum(MetodoPagamento), nullable=False)
    pago_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    id_transacao_externa: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # ID do PIX vindo do PagBank
    
    comanda: Mapped["Comanda"] = relationship("Comanda", back_populates="pagamentos")

# 🆕 NOVA TABELA PARA CHAMADOS DE ATENDIMENTO (SOLICITAR GARÇOM)
class ChamadoAtendimento(Base):
    __tablename__ = "chamados_atendimento"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mesa_id: Mapped[int] = mapped_column(Integer, ForeignKey("mesas.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), default="duvida") # "duvida" ou "maquininha"
    status: Mapped[StatusChamado] = mapped_column(Enum(StatusChamado), default=StatusChamado.ABERTO)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    mesa: Mapped["Mesa"] = relationship("Mesa", back_populates="chamados")
