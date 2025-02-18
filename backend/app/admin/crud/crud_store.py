import bcrypt
from sqlalchemy import Select, select, desc, and_, alias
from sqlalchemy_crud_plus import CRUDPlus
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.model.address import Address
from backend.app.admin.model.role import Role
from backend.app.admin.model.store import Store
from backend.app.admin.model.user import User
from backend.app.admin.schema.store import CreateStoreParam
from backend.common.security.jwt import get_hash_password


class CRUDStore(CRUDPlus[Store]):
    async def check_code(self, db: AsyncSession, code: str) -> Store | None:
        """
        检查商户编码是否存在
        """
        return await self.select_model_by_column(db, code=code)

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
                self.model.province_id.label("provinceId"),
                ParentAddress.c.name.label("provinceName"),
                self.model.city_id.label("cityId"),
                CityAddress.c.name.label("cityName"),
                self.model.area_id.label("areaId"),
                AreaAddress.c.name.label("areaName"),
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



    async def add(self, db, obj: CreateStoreParam) -> Store:
        """
        创建商户
        """
        dict_obj = obj.model_dump(exclude={'username', 'phone'})
        dict_obj['status'] = 0  # 设置初始状态为0
        
        db_obj = self.model(**dict_obj)
        db.add(db_obj)
        await db.flush()  # 确保获得 id
        return db_obj
            

    async def add_store_user(self, db: AsyncSession, username: str, nickname: str, phone: str, password: str, store_id: int, dept_id: int, role_id: int) -> None:
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
            'user_type': '20'
        }
        
        new_user = User(**user_dict)
        role = await db.get(Role, role_id)
        if role:
            new_user.roles = [role]
        db.add(new_user)


store_dao: CRUDStore = CRUDStore(Store)
