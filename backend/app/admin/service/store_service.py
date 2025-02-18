from fastapi import Request
from sqlalchemy import Select

from backend.app.admin.crud.crud_store import store_dao
from backend.app.admin.schema.dept import CreateDeptParam
from backend.app.admin.schema.role import CreateRoleParam
from backend.app.admin.schema.store import CreateStoreParam
from backend.app.admin.schema.user import AddUserParam
from backend.app.admin.service.user_service import user_service
from backend.common.exception import errors
from backend.common.security.jwt import superuser_verify
from backend.database.db import async_db_session
from backend.app.admin.crud.crud_user import user_dao
from backend.app.admin.crud.crud_dept import dept_dao
from backend.app.admin.crud.crud_role import role_dao

class StoreService:
    @staticmethod
    async def get_select(*,
                         store_name: str | None,
                         province_id: int | None,
                         city_id: int | None,
                         area_id: int | None,
                         status: int | None) -> Select:
        return await store_dao.get_list(store_name=store_name, province_id=province_id, city_id=city_id,
                                        area_id=area_id, status=status)

    @staticmethod
    async def add(*, request: Request, obj: CreateStoreParam) -> None:
        async with async_db_session.begin() as db:
        # 验证权限
            superuser_verify(request)
            # 验证手机号和商户编码
            phone = await user_dao.check_phone(db, obj.phone)
            if phone:
                raise errors.ForbiddenError(msg='手机号已存在')
            store_code = await store_dao.check_code(db, obj.code)
            if store_code:
                raise errors.ForbiddenError(msg='商户编码已存在')
            # 创建商户
            store = await store_dao.add(db, obj)
            # 准备用户信息
            username = obj.username or obj.phone
            nickname = '测试' + obj.phone[7:11]
            password = '123456'
            # 创建部门
            dept_data = {
                'name': '主部门',
                'level': 0,
                'status': 1,
                'store_id': store.id
            }
            dept = await dept_dao.create(db, CreateDeptParam(**dept_data))
            # 创建角色
            role_data = {
                'name': '商户管理员',
                'status': 1,
                'store_id': store.id
            }
            role = await role_dao.create(db, CreateRoleParam(**role_data))
            # 创建用户
            await store_dao.add_store_user(
                db,
                username=username,
                nickname=nickname,
                phone=obj.phone,
                password=password,
                store_id=store.id,
                dept_id=dept.id,
                role_id=role.id
            )

store_service: StoreService = StoreService()