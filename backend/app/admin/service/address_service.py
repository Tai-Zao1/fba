from backend.app.admin.crud.crud_address import address_dao
from backend.app.admin.model.address import Address
from backend.database.db import async_db_session


class AddressService:
    @staticmethod
    async def get_address_list(*, parent_id: int | None) -> list[Address]:
        async with async_db_session() as db:
            address_list = await address_dao.get_list(db, parent_id=parent_id)
            if not address_list:
                print("=========================================")
            return address_list


address_service: AddressService = AddressService()
