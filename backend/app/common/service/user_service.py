#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import Request
from sqlalchemy import Select

from backend.app.common.crud.crud_dept import dept_dao
from backend.app.common.crud.crud_role import role_dao
from backend.app.common.crud.crud_user import user_dao
from backend.app.common.model import User
from backend.app.common.schema.user import (
    AddUserParam,
    AvatarParam,
    RegisterUserParam,
    ResetPasswordParam,
    UpdateUserParam,
    UpdateUserRoleParam,
)
from backend.common.exception import errors
from backend.common.security.jwt import get_hash_password, get_token, jwt_decode, password_verify, superuser_verify
from backend.core.conf import settings
from backend.database.db import async_db_session
from backend.database.redis import redis_client


class UserService:
    @staticmethod
    async def register(*, user_type: str, obj: RegisterUserParam) -> None:
        async with async_db_session.begin() as db:
            if not obj.password:
                raise errors.ForbiddenError(msg='密码为空')

            phone = await user_dao.check_phone(db, obj.phone, user_type=user_type)
            if phone:
                raise errors.ForbiddenError(msg='手机号已注册')
            obj.username = obj.username if obj.username else phone
            # username = await user_dao.get_by_username(db, obj.username)
            # if username:
            #     raise errors.ForbiddenError(msg='用户已注册')
            obj.nickname = obj.nickname if obj.nickname else '测试' + phone[7:11]
            # nickname = await user_dao.get_by_nickname(db, obj.nickname)
            # if nickname:
            #     raise errors.ForbiddenError(msg='昵称已注册')
            await user_dao.create(db, obj)

    @staticmethod
    async def add(*, request: Request, obj: AddUserParam) -> None:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            user_type = request.user.user_type
            store_id = request.user.store_id
            phone = await user_dao.check_phone(db, obj.phone, user_type)
            if phone:
                raise errors.ForbiddenError(msg='手机号已存在')
            obj.username = obj.username if obj.username else obj.phone
            obj.nickname = obj.nickname if obj.nickname else '测试' + obj.phone[7:11]
            if not obj.password:
                raise errors.ForbiddenError(msg='密码为空')
            dept = await dept_dao.get(db, obj.dept_id, store_id)
            if not dept:
                raise errors.NotFoundError(msg='部门不存在')
            for role_id in obj.roles:
                role = await role_dao.get(db, role_id, store_id)
                if not role:
                    raise errors.NotFoundError(msg='角色不存在')
            await user_dao.add(db, user_type, store_id, obj)

    @staticmethod
    async def pwd_reset(*, request: Request, obj: ResetPasswordParam) -> int:
        async with async_db_session.begin() as db:
            user = await user_dao.get(db, request.user.id, request.user.store_id)
            if not password_verify(obj.old_password, user.password):
                raise errors.ForbiddenError(msg='原密码错误')
            np1 = obj.new_password
            np2 = obj.confirm_password
            if np1 != np2:
                raise errors.ForbiddenError(msg='密码输入不一致')
            new_pwd = get_hash_password(obj.new_password, user.salt)
            count = await user_dao.reset_password(db, request.user.id, new_pwd)
            key_prefix = [
                f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}',
                f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}',
                f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}',
            ]
            for prefix in key_prefix:
                await redis_client.delete_prefix(prefix)
            return count

    @staticmethod
    async def get_userinfo(*, request: Request, phone: str) -> User:
        async with async_db_session() as db:
            superuser_verify(request)
            user = await user_dao.get_with_relation(db, store_id=request.user.store_id, phone=phone)
            if not user:
                raise errors.NotFoundError(msg='用户不存在')
            return user

    @staticmethod
    async def update(*, request: Request, phone: str, obj: UpdateUserParam) -> int:
        async with async_db_session.begin() as db:
            if not request.user.is_superuser:
                if request.user.phone != phone:
                    raise errors.ForbiddenError(msg='你只能修改自己的信息')
            input_user = await user_dao.get_with_relation(db, store_id=request.user.store_id, phone=phone)
            if not input_user:
                raise errors.NotFoundError(msg='用户不存在')
            if input_user.phone != obj.phone:
                _phone = await user_dao.get_by_phone(db, obj.phone, user_type=request.user.user_type)
                if _phone:
                    raise errors.ForbiddenError(msg='手机号已注册')
            # if input_user.nickname != obj.nickname:
            #     nickname = await user_dao.get_by_nickname(db, obj.nickname)
            #     if nickname:
            #         raise errors.ForbiddenError(msg='昵称已注册')
            # if input_user.email != obj.email:
            #     email = await user_dao.check_email(db, obj.email)
            #     if email:
            #         raise errors.ForbiddenError(msg='邮箱已注册')
            count = await user_dao.update_userinfo(db, input_user.id, obj)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def update_roles(*, request: Request, phone: str, obj: UpdateUserRoleParam) -> None:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            if not request.user.is_superuser:
                if request.user.phone != phone:
                    raise errors.AuthorizationError
            input_user = await user_dao.get_with_relation(db, store_id=request.user.store_id, phone=phone)
            if not input_user:
                raise errors.NotFoundError(msg='用户不存在')
            for role_id in obj.roles:
                role = await role_dao.get(db, role_id, request.user.store_id)
                if not role:
                    raise errors.NotFoundError(msg='角色不存在')
            await user_dao.update_role(db, input_user, obj)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{input_user.id}')

    @staticmethod
    async def update_avatar(*, request: Request, phone: str, avatar: AvatarParam) -> int:
        async with async_db_session.begin() as db:
            if not request.user.is_superuser:
                if request.user.phone != phone:
                    raise errors.AuthorizationError
            input_user = await user_dao.get_by_phone(db, phone, user_type=request.user.user_type)
            if not input_user:
                raise errors.NotFoundError(msg='用户不存在')
            count = await user_dao.update_avatar(db, input_user.id, avatar)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def get_select(*, request: Request, dept: int, username: str = None, phone: str = None, status: int = None,
                         user_id: int = None) -> Select:
        async with async_db_session():
            superuser_verify(request)
            return await user_dao.get_list(dept=dept,
                                           username=username,
                                           phone=phone, status=status,
                                           user_id=user_id,
                                           store_id=request.user.store_id)

    @staticmethod
    async def update_permission(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            if not await user_dao.get(db, pk, store_id=request.user.store_id):
                raise errors.NotFoundError(msg='用户不存在')
            else:
                if pk == request.user.id:
                    raise errors.ForbiddenError(msg='非法操作')
                super_status = await user_dao.get_super(db, pk)
                count = await user_dao.set_super(db, pk, False if super_status else True)
                await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{pk}')
                return count

    @staticmethod
    async def update_staff(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            if not await user_dao.get(db, pk, request.user.store_id):
                raise errors.NotFoundError(msg='用户不存在')
            else:
                if pk == request.user.id:
                    raise errors.ForbiddenError(msg='非法操作')
                staff_status = await user_dao.get_staff(db, user_id=pk, store_id=request.user.store_id)
                count = await user_dao.set_staff(db, pk, False if staff_status else True)
                await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{pk}')
                return count

    @staticmethod
    async def update_status(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            if not await user_dao.get(db, pk, request.user.store_id):
                raise errors.NotFoundError(msg='用户不存在')
            else:
                if pk == request.user.id:
                    raise errors.ForbiddenError(msg='非法操作')
                status = await user_dao.get_status(db, pk, request.user.store_id)
                count = await user_dao.set_status(db, pk, False if status else True)
                await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{pk}')
                return count

    @staticmethod
    async def update_multi_login(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            if not await user_dao.get(db, pk, request.user.store_id):
                raise errors.NotFoundError(msg='用户不存在')
            else:
                user_id = request.user.id
                multi_login = await user_dao.get_multi_login(db, pk,
                                                             request.user.store_id) if pk != user_id else request.user.is_multi_login
                count = await user_dao.set_multi_login(db, pk, False if multi_login else True)
                await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
                token = get_token(request)
                token_payload = jwt_decode(token)
                latest_multi_login = await user_dao.get_multi_login(db, pk, request.user.store_id)
                # 超级用户修改自身时，除当前token外，其他token失效
                if pk == user_id:
                    if not latest_multi_login:
                        key_prefix = f'{settings.TOKEN_REDIS_PREFIX}:{pk}'
                        await redis_client.delete_prefix(
                            key_prefix, exclude=f'{key_prefix}:{token_payload.session_uuid}'
                        )
                        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY)
                        if refresh_token:
                            key_prefix = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{pk}'
                            await redis_client.delete_prefix(key_prefix, exclude=f'{key_prefix}:{refresh_token}')
                # 超级用户修改他人时，其他token将全部失效
                else:
                    if not latest_multi_login:
                        key_prefix = [f'{settings.TOKEN_REDIS_PREFIX}:{pk}']
                        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY)
                        if refresh_token:
                            key_prefix.append(f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{pk}')
                        for prefix in key_prefix:
                            await redis_client.delete_prefix(prefix)
                return count

    @staticmethod
    async def delete(*, request: Request, user_id: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            input_user = await user_dao.get(db, user_id=user_id, store_id=request.user.store_id)
            if not input_user:
                raise errors.NotFoundError(msg='用户不存在')
            count = await user_dao.delete(db, input_user.id)
            key_prefix = [
                f'{settings.TOKEN_REDIS_PREFIX}:{input_user.id}',
                f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{input_user.id}',
            ]
            for key in key_prefix:
                await redis_client.delete_prefix(key)
            return count


user_service: UserService = UserService()
