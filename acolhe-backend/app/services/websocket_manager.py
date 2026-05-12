from fastapi import WebSocket
from uuid import UUID
from typing import Dict

class ConnectionManager:
    """
    Gerencia conexões WebSocket ativas.
    Mapeia conversation_id -> lista de WebSockets conectados.
    """

    def __init__(self):
        # { conversation_id: { user_id: websocket } }
        self.active: Dict[str, Dict[str, WebSocket]] = {}

    async def conectar(self, websocket: WebSocket, conversation_id: str, user_id: str):
        await websocket.accept()
        if conversation_id not in self.active:
            self.active[conversation_id] = {}
        self.active[conversation_id][user_id] = websocket

    def desconectar(self, conversation_id: str, user_id: str):
        if conversation_id in self.active:
            self.active[conversation_id].pop(user_id, None)
            if not self.active[conversation_id]:
                del self.active[conversation_id]

    async def enviar_para_conversa(self, conversation_id: str, mensagem: dict, sender_id: str):
        """Envia mensagem para todos na conversa exceto o remetente."""
        if conversation_id in self.active:
            for uid, ws in self.active[conversation_id].items():
                if uid != sender_id:
                    await ws.send_json(mensagem)

    async def notificar_encerramento(self, conversation_id: str, sender_id: str):
        """Avisa o outro participante que a conversa foi encerrada."""
        await self.enviar_para_conversa(conversation_id, {
            "type": "conversation_ended",
            "message": "O outro participante encerrou a conversa."
        }, sender_id)

manager = ConnectionManager()
