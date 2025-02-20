from sqlalchemy import Select, select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.common.model import Address


class CRUDAddress(CRUDPlus[Address]):
    async def get_by_id(self, db: AsyncSession, parent_id: int) -> Address:
        """
        通过ID获取地址信息
        :param db:
        :param parent_id:
        """

        return await self.select_model_by_column(db, pcode=parent_id)

    async def get_list(self, db: AsyncSession, parent_id: int = None) -> list[Address] | None:
        """
        获取地址列表
        :param db:
        :param parent_id:
        """
        stmt = (
            select(
                self.model.id,
                self.model.adcode,
                self.model.pcode,
                self.model.name
            )
            .order_by(asc(self.model.id))
        )
        if parent_id is not None:
            stmt = stmt.where(self.model.pcode == parent_id)
        result = await db.execute(stmt)
        return result.mappings().all()


address_dao: CRUDAddress = CRUDAddress(Address)
