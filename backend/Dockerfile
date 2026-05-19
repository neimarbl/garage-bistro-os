FROM python:3.11-alpine

WORKDIR /app

# Instala dependências de sistema necessárias para compilação
RUN apk add --no-cache gcc musl-dev postgresql-dev

# Copia os arquivos de dependência primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY ./app ./app

EXPOSE 8000

# Executa o Uvicorn apontando para a instância da API (que criaremos no arquivo main.py)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
