#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Sequence

from fastapi import Request
from sqlalchemy import Select

from backend.app.common.crud.crud_data_rule import data_rule_dao
from backend.app.common.crud.crud_menu import menu_dao
from backend.app.common.crud.crud_role import role_dao
from backend.app.common.crud.crud_user import user_dao
from backend.app.common.model import Role
from backend.app.common.schema.role import (
    CreateRoleParam,
    UpdateRoleMenuParam,
    UpdateRoleParam,
    UpdateRoleRuleParam,
)
from backend.common.exception import errors
from backend.core.conf import settings
from backend.database.db import async_db_session
from backend.database.redis import redis_client


class RoleService:
    @staticmethod
    async def get(*, reqeust: Request, pk: int) -> Role:
        async with async_db_session() as db:
            role = await role_dao.get_with_relation(db, pk, reqeust.user.store_id)
            if not role:
                raise errors.NotFoundError(msg='角色不存在')
            return role

    @staticmethod
    async def get_all(*, store_id: int) -> Sequence[Role]:
        async with async_db_session() as db:
            roles = await role_dao.get_all(db, store_id=store_id)
            return roles

    @staticmethod
    async def get_by_user(*, request: Request, pk: int) -> Sequence[Role]:
        async with async_db_session() as db:
            user_info = await user_dao.get(db, pk, request.user.store_id)
            if not user_info:
                raise errors.NotFoundError(msg='用户不存在')
            roles = await role_dao.get_by_user(db, user_id=pk)
            return roles

    @staticmethod
    async def get_select(*, request: Request, name: str = None, status: int = None) -> Select:
        return await role_dao.get_list(name=name, status=status, store_id=request.user.store_id)

    @staticmethod
    async def create(*, request: Request, obj: CreateRoleParam) -> None:
        async with async_db_session.begin() as db:
            role = await role_dao.get_by_name(db, obj.name, request.user.store_id)
            if role:
                raise errors.ForbiddenError(msg='角色已存在')
            await role_dao.create(db, request.user.store_id, obj)

    @staticmethod
    async def update(*, request: Request, pk: int, obj: UpdateRoleParam) -> int:
        async with async_db_session.begin() as db:
            role = await role_dao.get(db, pk, request.user.store_id)
            if not role:
                raise errors.NotFoundError(msg='角色不存在')
            if role.name != obj.name:
                role = await role_dao.get_by_name(db, obj.name, request.user.store_id)
                if role:
                    raise errors.ForbiddenError(msg='角色已存在')
            count = await role_dao.update(db, pk, request.user.store_id, obj)
            return count

    @staticmethod
    async def update_role_menu(*, request: Request, pk: int, menu_ids: UpdateRoleMenuParam) -> int:
        async with async_db_session.begin() as db:
            role = await role_dao.get(db, pk, request.user.store_id)
            if not role:
                raise errors.NotFoundError(msg='角色不存在')
            for menu_id in menu_ids.menus:
                if request.user.user_type == '00':
                    is_admin = 1
                else:
                    is_admin = 0
                menu = await menu_dao.get(db, menu_id, is_admin)
                if not menu:
                    raise errors.NotFoundError(msg='菜单不存在')
            count = await role_dao.update_menus(db, pk, request.user.store_id, menu_ids)
            if pk in [role.id for role in request.user.roles]:
                await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def update_role_rule(*, request: Request, pk: int, rule_ids: UpdateRoleRuleParam) -> int:
        async with async_db_session.begin() as db:
            role = await role_dao.get(db, pk, request.user.store_id)
            if not role:
                raise errors.NotFoundError(msg='角色不存在')
            for rule_id in rule_ids.rules:
                rule = await data_rule_dao.get(db, rule_id)
                if not rule:
                    raise errors.NotFoundError(msg='数据权限不存在')
            count = await role_dao.update_rules(db, pk, request.user.store_id, rule_ids)
            if pk in [role.id for role in request.user.roles]:
                await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def delete(*, request: Request, pk: list[int],) -> int:
        async with async_db_session.begin() as db:
            for role_id in pk:
                role_info = await role_dao.get(db, role_id, request.user.store_id)
                if not role_info:
                    raise errors.ForbiddenError(msg=f'当前角色id{role_id}，无法删除')
            count = await role_dao.delete(db, pk, request.user.store_id)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count


role_service: RoleService = RoleService()
