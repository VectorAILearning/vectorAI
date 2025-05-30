from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import db_helper
from fastapi import APIRouter, Depends
from models import CourseModel, ModuleModel

courses_router = APIRouter()


@courses_router.get("/user-courses")
async def get_user_courses(db: AsyncSession = Depends(db_helper.get_session)):
    stmt = select(CourseModel).options(
        selectinload(CourseModel.modules).selectinload(ModuleModel.lessons)
    )
    return (await db.execute(stmt)).scalars().all()
