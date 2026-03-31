"""Database operations for learners."""
import logging
from datetime import datetime
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.learner import Learner

logger = logging.getLogger(__name__)

async def read_learners(
    session: AsyncSession, enrolled_after: datetime | None = None
) -> list[Learner]:
    """Read all learners from the database, optionally filtered by enrollment date."""
    try:
        logger.info("db_query", extra={"event": "db_query", "table": "learner", "operation": "select"})
        statement = select(Learner)
        if enrolled_after is not None:
            statement = statement.where(col(Learner.enrolled_at) >= enrolled_after)
        result = await session.exec(statement)
        return list(result.all())
    except Exception as exc:
        logger.error(
            "db_query",
            extra={"event": "db_query", "table": "learner", "operation": "select", "error": str(exc)},
        )
        raise

async def create_learner(
    session: AsyncSession, external_id: str, student_group: str = ""
) -> Learner:
    """Create a new learner in the database."""
    try:
        logger.info("db_query", extra={"event": "db_query", "table": "learner", "operation": "insert"})
        learner = Learner(
            external_id=external_id, student_group=student_group, enrolled_at=datetime.now()
        )
        session.add(learner)
        await session.commit()
        await session.refresh(learner)
        return learner
    except Exception as exc:
        logger.error(
            "db_query",
            extra={"event": "db_query", "table": "learner", "operation": "insert", "error": str(exc)},
        )
        raise
