import random
import redis.asyncio as aioredis
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.models import User, Block, Conversation
from app.schemas.schemas import MatchFilters
from app.core.config import settings

# Nomes anônimos criativos
NOMES = [
    "Vento Azul", "Chuva Suave", "Mar Calmo", "Brisa Leve", "Névoa Clara",
    "Rio Sereno", "Lua Nova", "Sol Tímido", "Folha Verde", "Pedra Firme",
    "Estrela Pálida", "Nuvem Livre", "Terra Úmida", "Chama Quieta", "Onda Mansa",
    "Campo Aberto", "Céu Distante", "Raiz Profunda", "Sombra Suave", "Pétala Leve"
]

async def gerar_nome_anonimo() -> str:
    return random.choice(NOMES) + f" #{random.randint(100, 999)}"

async def encontrar_match(
    db: AsyncSession,
    user_id: UUID,
    filters: MatchFilters
) -> User | None:
    """
    Busca um usuário disponível (is_listening=True) que:
    - Não está bloqueado pelo solicitante
    - Não bloqueou o solicitante
    - Atende aos filtros opcionais (gênero, faixa etária)
    """

    # Buscar IDs bloqueados (nos dois sentidos)
    bloqueados_query = select(Block).where(
        (Block.blocker_id == user_id) | (Block.blocked_id == user_id)
    )
    resultado = await db.execute(bloqueados_query)
    blocos = resultado.scalars().all()

    ids_bloqueados = set()
    for b in blocos:
        ids_bloqueados.add(b.blocker_id)
        ids_bloqueados.add(b.blocked_id)
    ids_bloqueados.discard(user_id)  # remove o próprio user

    # Montar query de candidatos
    conditions = [
        User.is_active == True,
        User.is_listening == True,
        User.id != user_id,
    ]

    if filters.gender:
        conditions.append(User.gender == filters.gender)

    if filters.age_range:
        conditions.append(User.age_range == filters.age_range)

    query = select(User).where(and_(*conditions))
    resultado = await db.execute(query)
    candidatos = resultado.scalars().all()

    # Filtrar bloqueados
    candidatos = [u for u in candidatos if u.id not in ids_bloqueados]

    if not candidatos:
        return None

    return random.choice(candidatos)

async def criar_conversa(
    db: AsyncSession,
    user_a_id: UUID,
    user_b_id: UUID
) -> Conversation:
    conversa = Conversation(user_a_id=user_a_id, user_b_id=user_b_id)
    db.add(conversa)
    await db.commit()
    await db.refresh(conversa)
    return conversa
