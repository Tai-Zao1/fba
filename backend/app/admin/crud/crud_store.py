import bcrypt
from sqlalchemy import Select, select, desc, and_, alias
from sqlalchemy_crud_plus import CRUDPlus
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.model.address import Address
from backend.app.admin.model.role import Role
from backend.app.admin.model.store import Store
from backend.app.admin.model.user import User
from backend.app.admin.schema.store import CreateStoreParam, ReviewStoreParam, UpdateStoreParam
from backend.common.security.jwt import get_hash_password


class CRUDStore(CRUDPlus[Store]):
    async def check_code(self, db: AsyncSession, code: str) -> Store | None:
        """
        检查商户编码是否存在
        """
        return await self.select_model_by_column(db, code=code)

    async def check_id(self, db: AsyncSession, store_id: int) -> Store | None:
        """
        检查商户ID是否存在
        """
        return await self.select_model_by_column(db, id=store_id)

    async def get_list(self,
                       store_name: str | None,
                       province_id: int | None,
                       city_id: int | None,
                       area_id: int | None,
                       status: int | None) -> Select:
        """
        根据查询条件查询商户列表
        :param store_name:
        :param province_id:
        :param city_id:
        :param area_id:
        :param status:
        """
        ParentAddress = alias(Address, name="parent_address")
        CityAddress = alias(Address, name="city_address")
        AreaAddress = alias(Address, name="area_address")

        # 构建查询语句
        stmt = (
            select(
                self.model.id,
                self.model.name,
                self.model.code,
                self.model.status,
                self.model.created_by,
                self.model.created_time,
                self.model.updated_by,
                self.model.updated_time,
                self.model.province_id,
                ParentAddress.c.name.label("province_name"),
                self.model.city_id,
                CityAddress.c.name.label("city_name"),
                self.model.area_id,
                AreaAddress.c.name.label("area_name"),
                self.model.address,
                self.model.logo,
                User.id.label("user_id"),
                User.username.label("username"),
                User.phone.label("phone")
            )
            .join(User, self.model.id == User.store_id)
            .join(ParentAddress, self.model.province_id == ParentAddress.c.id)
            .join(CityAddress, self.model.city_id == CityAddress.c.id)
            .join(AreaAddress, self.model.area_id == AreaAddress.c.id)
            .where(User.store_superuser == True)
            .order_by(desc(self.model.id))
        )
        where_list = []
        if store_name:
            where_list.append(self.model.name == store_name)
        if province_id:
            where_list.append(self.model.province_id == province_id)
            if city_id:
                where_list.append(self.model.city_id == city_id)
                if area_id:
                    where_list.append(self.model.area_id == area_id)
        if status:
            where_list.append(self.model.status == status)
        if where_list:
            stmt = stmt.where(and_(*where_list))
        return stmt

    async def add(self, db, obj: CreateStoreParam, user_id: int) -> Store:
        """
        创建商户
        """
        dict_obj = obj.model_dump(exclude={'username', 'phone'})
        dict_obj['status'] = 0  # 设置初始状态为0
        dict_obj['created_by'] = user_id
        db_obj = self.model(**dict_obj)
        db.add(db_obj)
        await db.flush()  # 确保获得 id
        return db_obj

    async def add_store_user(self, db: AsyncSession, username: str, nickname: str, phone: str, password: str,
                             store_id: int, dept_id: int, role_id: int) -> None:
        """
        创建商户用户
        """

        salt = bcrypt.gensalt()
        hashed_password = get_hash_password(password, salt)

        user_dict = {
            'username': username,
            'nickname': nickname,
            'phone': phone,
            'password': hashed_password,
            'salt': salt,
            'dept_id': dept_id,
            'store_id': store_id,
            'is_staff': True,
            'user_type': '20',
            'store_superuser': 1
        }

        new_user = User(**user_dict)
        role = await db.get(Role, role_id)
        if role:
            new_user.roles = [role]
        db.add(new_user)

    async def review_store(self, db: AsyncSession, store_id: int, updated_by: str, obj: ReviewStoreParam) -> int:
        """
        更新商户审核状态
        param store_id:
        """
        dict_obj = obj.model_dump()
        dict_obj["updated_by"] = updated_by
        return await self.update_model(db, store_id, dict_obj)

    async def update_store(self, db: AsyncSession, store_id: int, updated_by: str, obj: UpdateStoreParam) -> int:
        """
        更新商户信息
        param store_id:
        """
        dict_obj = obj.model_dump(exclude={'username', 'phone'})
        dict_obj["updated_by"] = updated_by
        return await self.update_model(db, store_id, dict_obj)


store_dao: CRUDStore = CRUDStore(Store)
