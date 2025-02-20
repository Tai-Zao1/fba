from fastapi import Request
from sqlalchemy import Select

from backend.app.common.crud.crud_store import store_dao
from backend.app.common.schema.dept import CreateDeptParam
from backend.app.common.schema.role import CreateRoleParam
from backend.app.common.schema.store import CreateStoreParam, ReviewStoreParam, UpdateStoreParam
from backend.common.exception import errors
from backend.common.security.jwt import superuser_verify
from backend.database.db import async_db_session
from backend.app.common.crud.crud_user import user_dao
from backend.app.common.crud.crud_dept import dept_dao
from backend.app.common.crud.crud_role import role_dao


class StoreService:
    @staticmethod
    async def get_select(*,
                         store_name: str | None,
                         province_id: int | None,
                         city_id: int | None,
                         area_id: int | None,
                         status: int | None) -> Select:
        """
        获取商户列表
        """

        return await store_dao.get_list(store_name=store_name, province_id=province_id, city_id=city_id,
                                        area_id=area_id, status=status)

    @staticmethod
    async def add(*, request: Request, obj: CreateStoreParam) -> None:
        """
        新增商户
        """
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
            store = await store_dao.add(db, obj, request.user.id)
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

    @staticmethod
    async def review(*, request: Request, obj: ReviewStoreParam) -> None:
        """
        审核商户
        """
        async with async_db_session.begin() as db:
            # 验证权限
            superuser_verify(request)
            # 验证工厂是否存在
            store = await store_dao.check_id(db, obj.id)
            if not store:
                raise errors.NotFoundError(msg='商户不存在')
            if store.status == 1:
                raise errors.ForbiddenError(msg='商户已审核通过')
            if obj.status == 2:
                if not obj.remark:
                    raise errors.ForbiddenError(msg='审核不通过原因不能为空')
            # 审核商户
            await store_dao.review_store(db, obj.id, request.user.id, obj)

    @staticmethod
    async def update(*, request: Request, obj: UpdateStoreParam):
        """
        更新商户
        """
        async with async_db_session.begin() as db:
            # 验证权限
            superuser_verify(request)
            # 验证商户是否存在
            store = await store_dao.check_id(db, store_id=obj.id)
            if not store:
                raise errors.NotFoundError(msg='商户不存在')
            # 验证商户Code是否被修改
            if store.code != obj.code:
                raise errors.ForbiddenError(msg='商户编码不支持修改')
            await store_dao.update_store(db, obj.id, request.user.id, obj)



store_service: StoreService = StoreService()
