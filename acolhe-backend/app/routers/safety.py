from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.core.database import get_db
from app.models.models import Report, Block, User
from app.schemas.schemas import ReportCreate, ReportOut, BlockCreate

router = APIRouter(prefix="/safety", tags=["Segurança"])

@router.post("/report", response_model=ReportOut)
async def denunciar_usuario(
    reporter_id: str,
    data: ReportCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Denuncia um usuário por preconceito, assédio, fraude, etc.
    """
    report = Report(
        reporter_id=UUID(reporter_id),
        reported_id=data.reported_id,
        reason=data.reason,
        description=data.description,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report

@router.post("/block")
async def bloquear_usuario(
    blocker_id: str,
    data: BlockCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Bloqueia um usuário — ele nunca mais aparecerá no matchmaking.
    """
    # Verifica se já bloqueou
    result = await db.execute(
        select(Block).where(
            Block.blocker_id == UUID(blocker_id),
            Block.blocked_id == data.blocked_id
        )
    )
    existente = result.scalar_one_or_none()
    if existente:
        return {"detail": "Usuário já bloqueado"}

    block = Block(blocker_id=UUID(blocker_id), blocked_id=data.blocked_id)
    db.add(block)
    await db.commit()
    return {"detail": "Usuário bloqueado com sucesso"}

@router.delete("/block/{blocked_id}")
async def desbloquear_usuario(
    blocker_id: str,
    blocked_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Remove um bloqueio.
    """
    result = await db.execute(
        select(Block).where(
            Block.blocker_id == UUID(blocker_id),
            Block.blocked_id == UUID(blocked_id)
        )
    )
    block = result.scalar_one_or_none()
    if not block:
        raise HTTPException(status_code=404, detail="Bloqueio não encontrado")

    await db.delete(block)
    await db.commit()
    return {"detail": "Bloqueio removido"}
