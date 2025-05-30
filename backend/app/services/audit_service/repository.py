from sqlalchemy.ext.asyncio import AsyncSession


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user_preference(self, preference: str):
        # TODO: сделать создание session + preference
        pass
