from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.core.database import get_db
from app.models.models import Conversation, Message, User
from app.schemas.schemas import MatchFilters, ConversationOut, MessageOut
from app.services.matchmaking import encontrar_match, criar_conversa
from app.services.websocket_manager import manager
from app.services.crisis_detector import analisar_mensagem, RiskLevel
from app.services.content_filter import filtrar_mensagem
from datetime import datetime

router = APIRouter(prefix="/conversations", tags=["Conversas"])

@router.post("/match", response_model=ConversationOut)
async def buscar_match(
    user_id: str,
    filters: MatchFilters,
    db: AsyncSession = Depends(get_db)
):
    """
    Busca um parceiro disponível e cria uma conversa.
    """
    uid = UUID(user_id)
    match = await encontrar_match(db, uid, filters)

    if not match:
        raise HTTPException(
            status_code=404,
            detail="Nenhum parceiro disponível agora. Tente novamente em instantes."
        )

    conversa = await criar_conversa(db, uid, match.id)

    # Marca ambos como não disponíveis
    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if user:
        user.is_listening = False

    match.is_listening = False
    await db.commit()
    await db.refresh(conversa)
    return conversa

@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def listar_mensagens(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """
    Retorna o histórico de mensagens de uma conversa.
    """
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == UUID(conversation_id))
        .order_by(Message.sent_at)
    )
    return result.scalars().all()

@router.post("/{conversation_id}/end")
async def encerrar_conversa(
    conversation_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Encerra uma conversa e notifica o outro participante via WebSocket.
    """
    result = await db.execute(
        select(Conversation).where(Conversation.id == UUID(conversation_id))
    )
    conversa = result.scalar_one_or_none()

    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")

    conversa.is_active = False
    conversa.ended_at = datetime.utcnow()
    await db.commit()

    # Notifica o outro via WebSocket
    await manager.notificar_encerramento(conversation_id, user_id)

    return {"detail": "Conversa encerrada"}

@router.websocket("/ws/{conversation_id}/{user_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket de chat em tempo real.
    Suporta mensagens de texto e áudio (base64).
    """
    await manager.conectar(websocket, conversation_id, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "text")
            conteudo = data.get("content", "")

            # 1. FILTRO DE CONTEÚDO — bloqueia links, contatos, PIX, sexual
            if msg_type == "text" and conteudo:
                filtro = filtrar_mensagem(conteudo)
                if filtro.blocked:
                    await websocket.send_json({
                        "type": "warning",
                        "content": filtro.warning_to_user,
                        "blocked": True,
                    })
                    continue  # não salva nem envia a mensagem

            # 2. DETECTOR DE CRISE — ideação suicida, manipulação, risco
            if msg_type == "text" and conteudo:
                risco = analisar_mensagem(conteudo)
                if risco.level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                    # Envia recursos para quem enviou
                    if risco.message_to_user:
                        await websocket.send_json({
                            "type": "crisis_support",
                            "content": risco.message_to_user,
                        })
                    # Orienta o ouvinte
                    if risco.message_to_listener:
                        await manager.enviar_para_conversa(
                            conversation_id,
                            {"type": "listener_guidance", "content": risco.message_to_listener},
                            sender_id="system"
                        )

            # Salva a mensagem no banco
            msg = Message(
                conversation_id=UUID(conversation_id),
                sender_id=UUID(user_id),
                content=data.get("content") if msg_type == "text" else None,
                audio_url=data.get("audio_url") if msg_type == "audio" else None,
            )
            db.add(msg)
            await db.commit()
            await db.refresh(msg)

            # Repassa para o outro participante
            await manager.enviar_para_conversa(
                conversation_id,
                {
                    "type": msg_type,
                    "sender_id": user_id,
                    "content": msg.content,
                    "audio_url": msg.audio_url,
                    "sent_at": msg.sent_at.isoformat(),
                },
                sender_id=user_id
            )

    except WebSocketDisconnect:
        manager.desconectar(conversation_id, user_id)
        await manager.notificar_encerramento(conversation_id, user_id)
