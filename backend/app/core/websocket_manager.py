# backend/app/core/websocket_manager.py
from fastapi import WebSocket
from typing import List, Dict

class NotificationManager:
    def __init__(self):
        # Dicionário para separar conexões por grupo (ex: 'garcons', 'caixa', 'cozinha')
        self.active_connections: Dict[str, List[WebSocket]] = {
            "garcons": [],
            "caixa": [],
            "cozinha": [],
            "clientes": []
        }

    async def connect(self, websocket: WebSocket, grupo: str):
        await websocket.accept()
        if grupo in self.active_connections:
            self.active_connections[grupo].append(websocket)

    def disconnect(self, websocket: WebSocket, grupo: str):
        if grupo in self.active_connections and websocket in self.active_connections[grupo]:
            self.active_connections[grupo].remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast_to_group(self, grupo: str, message: dict):
        """
        Envia uma notificação em tempo real para todos os dispositivos de um grupo específico.
        """
        if grupo in self.active_connections:
            for connection in self.active_connections[grupo]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Remove conexões inativas se o celular perder o sinal Wi-Fi
                    self.active_connections[grupo].remove(connection)

# Instância global do gerenciador para ser importada nas routers
notifier = NotificationManager()
