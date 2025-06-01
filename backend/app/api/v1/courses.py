from core.database import db_helper
from fastapi import APIRouter, Depends
from models import CourseModel, ModuleModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

courses_router = APIRouter(tags=["learning"])


@courses_router.get("/user-courses")
async def get_user_courses(db: AsyncSession = Depends(db_helper.get_session)):
    stmt = select(CourseModel).options(
        selectinload(CourseModel.modules).selectinload(ModuleModel.lessons)
    )
    return (await db.execute(stmt)).scalars().all()
