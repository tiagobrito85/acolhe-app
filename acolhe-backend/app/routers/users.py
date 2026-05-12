from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserOut
from app.services.matchmaking import gerar_nome_anonimo

router = APIRouter(prefix="/users", tags=["Usuários"])

@router.post("/", response_model=UserOut)
async def criar_usuario(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Cria um usuário anônimo.
    Retorna o ID que será usado como identidade temporária.
    """
    nome = await gerar_nome_anonimo()
    user = User(
        anonymous_name=nome,
        gender=data.gender,
        age_range=data.age_range,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.patch("/{user_id}/listening", response_model=UserOut)
async def toggle_disponivel(user_id: str, disponivel: bool, db: AsyncSession = Depends(get_db)):
    """
    Marca o usuário como disponível (is_listening=True) ou não para conversar.
    """
    from sqlalchemy import select
    from uuid import UUID
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.is_listening = disponivel
    await db.commit()
    await db.refresh(user)
    return user
