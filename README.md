# 🚀 Garage Bistrô OS

[![FastAPI](https://shields.io)](https://tiangolo.com)
[![React](https://shields.io)](https://reactjs.org)
[![PostgreSQL](https://shields.io)](https://postgresql.org)
[![Docker](https://shields.io)](https://docker.com)

O **Garage Bistrô OS (DEV Bistro II)** é um ecossistema omnichannel assíncrono projetado sob medida para gerenciar a operação física, o fluxo produtivo e a engenharia financeira de um bistrô dinâmico com capacidade de atendimento simultâneo. O sistema foi construído focando em **resiliência máxima local (LAN)** sobre redes Wi-Fi 5G, eliminando comandas manuscritas e perdas no almoxarifado.

---

## 🛠️ Diferenciais de Engenharia de Software (Vitrine Sênior)

Este projeto foi desenvolvido aplicando padrões arquiteturais rigorosos para mitigar problemas reais de sistemas de alta concorrência:

*   **Arquitetura Assíncrona Full-Duplex:** Backend construído sobre **FastAPI** aproveitando o loop de eventos nativo do `asyncio` e protocolo **WebSockets** nativo para broadcasts instantâneos entre salão, cozinha e caixa.
*   **Blindagem Antifraude Omnichannel (Anti-IDOR):** O autoatendimento do cliente implementa verificação cruzada baseada no algoritmo **HMAC-SHA256**. O sistema valida o token criptográfico contido no QR Code combinando o número do PVC com a chave randômica diária do caixa, mitigando ataques de manipulação de parâmetros e invasão de contas alheias.
*   **Strategy Pattern Financeiro (B2B/B2C):** Camada financeira desacoplada que chaveia dinamicamente as políticas de rateio no banco de dados se houver um evento corporativo ativo (Consumo Individual, Total Empresa ou Híbrido Fixo de Comidas/Bebidas).
*   **Baixa Automatizada via Matriz FEFO:** Eventos de despacho no KDS disparam gatilhos relacionais no SQLAlchemy que deduzem ingredientes do almoxarifado varrendo os lotes por data de validade (*First Expired, First Out*).
*   **Desacoplamento Estatístico de Loops:** Uso estrito de **Lazy Imports (Importações Tardias)** locais para estirpar referências cruzadas e acoplamentos rígidos na inicialização da tabela de símbolos do interpretador Python.

---

## 📦 Arquitetura do Sistema e Topologia de Rotas

O frontend utiliza uma abordagem *State-Driven* orientada a sequestro de perfil por URL (*Url Profiling Hijacking*). Um único ponto de entrada (`App.jsx`) gerencia dinamicamente quatro perfis operacionais isolados na mesma LAN:

### 💼 1. Frente A — Painel do Garçom (`/`)
*   Grid tátil responsivo mobile-first otimizado para smartphones corporativos.
*   Monitoramento visual de mesas e agrupamentos lógicos de aniversários.
*   Retenção de carrinho em memória estruturado por chaves compostas (`id + observacao`) para isolar pedidos customizados à cozinha.

### 📱 2. Frente B — Web App do Cliente (`/?mesa=X&pvc=Y&token=Z`)
*   Interceptador de parâmetros criptográficos antifraude.
*   Menu de autoatendimento minimalista focado em alta conversão e experiência estável.
*   Monitoramento passivo via WebSocket da esteira de preparo do KDS.

### 📺 3. Monitor KDS da Cozinha/Bar (`/?modo=kds`)
*   Interface projetada para Smart TVs de salão (Layout 16:9).
*   Cronômetro de SLA reativo com alertas visuais de atraso em vermelho.
*   **Captura de Hardware Dedicado:** Eventos JavaScript globais integrados para entrada e controle de preparo através de **teclados numéricos USB [1-9]**.

### 📊 4. Terminal Desktop do Caixa (`/?modo=caixa`)
*   Agregações matemáticas financeiras em tempo real do faturamento diário segregado por espécie.
*   Central de alertas preventivos de perdas (Avisos de validade de congelados < 5 dias e quebras de estoque mínimo).

---

## 📂 Estrutura de Diretórios do Projeto

```text
garage-bistro-os/
├── backend/
│   ├── app/
│   │   ├── core/           # Banco de dados, Criptografia HMAC e Sockets
│   │   ├── models/         # Mapeamento Declarativo SQLAlchemy 2.0 (Modelos Físicos)
│   │   ├── repositories/   # Camada estrita de acesso a dados (FEFO, Strategy, Aggregations)
│   │   ├── routers/        # Endpoints FastAPI expostos no Swagger
│   │   └── main.py         # Inicializador e middlewares de CORS
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── context/        # Estado Global Nativo (SocketContext e AtendimentoContext)
│   │   ├── pages/          # Views Operacionais do Garçom (Frente A)
│   │   │   ├── cliente/    # Views Seguras de Autoatendimento (Frente B)
│   │   │   ├── kds/        # Grade de Produção por Hardware Teclado USB
│   │   │   └── caixa/      # Terminal Desktop Financeiro e Auditoria de Lote
│   │   ├── App.jsx         # Roteador Omnichannel State-Driven
│   │   └── main.jsx        # Ponto de Inicialização DOM React 18 StrictMode
│   ├── Dockerfile          # Build Multi-Stage Otimizado
│   └── nginx.conf          # Configuração SPA Nginx Alpine (Evita erros 404)
└── docker-compose.yml      # Orquestrador da Malha Multi-Container (PostgreSQL Master-Slave)
```

---

## 🚀 Como Executar o Ecossistema em Produção

Toda a infraestrutura, banco de dados relacional e servidores estão empacotados e automatizados. Garanta que o Docker e o WSL2 estão ativos e execute um único comando centralizado na raiz do projeto:

```bash
# Clone o repositório
git clone https://github.com
cd garage-bistro-os

# Suba a infraestrutura completa unificada
docker compose up -d --build
```

### 🔬 Portas e Acessos Disponíveis na LAN:
*   **Swagger UI (Endpoints Core API):** `http://localhost:8080/docs`
*   **Frontend Omnichannel (React App):** `http://localhost:5173/`
*   **PostgreSQL Master Container:** Porta `5432`

---

## 📈 Carga Inicial de Teste (Seed)

Para ver o salão ganhar vida com dados de mesas, produtos e comandas PVC pré-configurados, injete a semente diretamente no banco de dados rodando:

```bash
docker exec -i gb_db_master psql -U garage_admin -d garage_bistro_prod < seed.sql
```
