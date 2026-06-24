# tests/locustfile.py
import json
import random
import time
from locust import HttpUser, task, between, events
from websocket import create_connection

# Token HMAC válido gerado na nossa seed do banco para a comanda 15
TOKEN_TESTE = "f03da73117498c1170940bf7cb9ea9c37953cb7e9c90b8f05e4dfa9f7e34efee"

class SimulaçãoGarçom(HttpUser):
    """Simula o comportamento dos garçons operando o PWA via chamadas HTTP REST"""
    weight = 1  # Proporção: 1 garçom para cada X clientes
    wait_time = between(2, 5)  # Garçom espera de 2 a 5 segundos entre ações

    @task(3)
    def consultar_mapa_mesas(self):
        """Simula a abertura do grid de mesas inicial"""
        with self.client.get("/atendimento/mesas", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Falha ao carregar salão: {response.status_code}")

    @task(2)
    def consultar_cardapio(self):
        """Simula a navegação pelas abas de categorias do cardápio"""
        self.client.get("/atendimento/produtos")

    @task(1)
    def lancar_pedido_cozinha(self):
        """Simula o disparo em bloco de pedidos para o KDS (Cozinha/Bar)"""
        payload = {
            "mesa_id": random.choice([1, 2, 3, 4, 5]),
            "comanda_id": 15,
            "origem": "garcon",
            "itens": [
                {
                    "produto_id": random.choice([1, 2, 3, 4]),
                    "quantidade": random.randint(1, 3),
                    "observacao": random.choice([None, "Sem cebola", "Bem passado"])
                }
            ]
        }
        
        headers = {"Content-Type": "application/json"}
        with self.client.post("/pedidos/", json=payload, headers=headers, catch_response=True) as response:
            # 🟢 CORREÇÃO 1: Inserido o array de validação de status de criação [200, 201]
            if response.status_code in:
                response.success()
            else:
                response.failure(f"Erro ao injetar pedido no KDS: {response.text}")


class SimulaçãoClienteWebSocket(HttpUser):
    """Simula os clientes que abrem o autoatendimento e seguram conexões WebSocket"""
    weight = 5  # Simula maior volume de clientes conectados simultaneamente
    wait_time = between(4, 8)

    def on_start(self):
        """Gatilho de entrada: Abre a conexão estável de socket com o FastAPI"""
        # Converte a URL HTTP do Locust para o protocolo WS de forma dinâmica
        base_ws_url = self.host.replace("http://", "ws://").replace("https://", "wss://")
        ws_endpoint = f"{base_ws_url}/pedidos/ws/garcons" # Barramento global escutado
        
        start_time = time.time()
        try:
            self.ws = create_connection(ws_endpoint)
            # Registra o sucesso da conexão estável no relatório do Locust
            events.request.fire(
                request_type="WS_CONNECT",
                name="/pedidos/ws/garcons",
                response_time=int((time.time() - start_time) * 1000),
                response_length=0
            )
        except Exception as e:
            events.request.fire(
                request_type="WS_CONNECT",
                name="/pedidos/ws/garcons",
                response_time=int((time.time() - start_time) * 1000),
                response_length=0,
                exception=e
            )
            self.ws = None

    def on_stop(self):
        """Gatilho de saída: Encerra o socket limpando a memória do servidor ASGI"""
        if self.ws:
            self.ws.close()

    @task
    def manter_ouvinte_ativo(self):
        """Escuta passivamente as transmissões de broadcast do KDS (Cozinha/Bar)"""
        if not self.ws:
            self.on_start() # Tenta reconectar se o Wi-Fi 5G simulado cair
            return

        start_time = time.time()
        try:
            # Configura um timeout curto para não travar a thread do Locust esperando eternamente
            self.ws.settimeout(1.0)
            mensagem = self.ws.recv()
            dados = json.loads(mensagem)
            
            # Registra o recebimento com sucesso do evento assíncrono push
            events.request.fire(
                request_type="WS_RECV",
                name=f"Push: {dados.get('evento', 'desconhecido')}",
                response_time=int((time.time() - start_time) * 1000),
                response_length=len(mensagem)
            )
        except Exception:
            # Timeout normal em WebSockets passivos (Nenhum prato mudou de status nesse segundo)
            pass
