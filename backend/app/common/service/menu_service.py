#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

from fastapi import Request

from backend.app.common.crud.crud_menu import menu_dao
from backend.app.common.crud.crud_role import role_dao
from backend.app.common.model import Menu
from backend.app.common.schema.menu import CreateMenuParam, UpdateMenuParam
from backend.common.exception import errors
from backend.core.conf import settings
from backend.database.db import async_db_session
from backend.database.redis import redis_client
from backend.utils.build_tree import get_tree_data


class MenuService:
    @staticmethod
    async def get(*, request: Request, pk: int) -> Menu:
        async with async_db_session() as db:
            if request.user.user_type == '00':
                is_admin = 1
            else:
                is_admin = 0
            menu = await menu_dao.get(db, menu_id=pk, is_admin=is_admin)
            if not menu:
                raise errors.NotFoundError(msg='菜单不存在')
            return menu

    @staticmethod
    async def get_menu_tree(*, request: Request, title: str | None = None, status: int | None = None) -> list[
        dict[str, Any]]:
        async with async_db_session() as db:
            if request.user.user_type == '00':
                is_admin = 1
            else:
                is_admin = 0
            menu_select = await menu_dao.get_all(db, title=title, status=status, is_admin=is_admin)
            menu_tree = get_tree_data(menu_select)
            return menu_tree

    @staticmethod
    async def get_role_menu_tree(*, request: Request, pk: int) -> list[dict[str, Any]]:
        async with async_db_session() as db:
            role = await role_dao.get_with_relation(db, pk, request.user.store_id)
            if not role:
                raise errors.NotFoundError(msg='角色不存在')
            menu_ids = [menu.id for menu in role.menus]
            if request.user.user_type == '00':
                is_admin = 1
            else:
                is_admin = 0
            menu_select = await menu_dao.get_role_menus(db, False, menu_ids, is_admin)
            menu_tree = get_tree_data(menu_select)
            return menu_tree

    @staticmethod
    async def get_user_menu_tree(*, request: Request) -> list[dict[str, Any]]:
        async with async_db_session() as db:
            roles = request.user.roles
            if request.user.user_type == '00':
                is_admin = 1
            else:
                is_admin = 0
            menu_ids = []
            menu_tree = []
            if roles:
                for role in roles:
                    menu_ids.extend([menu.id for menu in role.menus])
                menu_select = await menu_dao.get_role_menus(db, request.user.is_superuser, menu_ids, is_admin)
                menu_tree = get_tree_data(menu_select)
            return menu_tree

    @staticmethod
    async def create(*, request: Request, obj: CreateMenuParam) -> None:
        async with async_db_session.begin() as db:
            if request.user.user_type == '00':
                is_admin = 1
            else:
                is_admin = 0
            title = await menu_dao.get_by_title(db, obj.title, is_admin=is_admin)
            if title:
                raise errors.ForbiddenError(msg='菜单标题已存在')
            if obj.parent_id:
                parent_menu = await menu_dao.get(db, obj.parent_id, is_admin=is_admin)
                if not parent_menu:
                    raise errors.NotFoundError(msg='父级菜单不存在')
            await menu_dao.create(db, obj, is_admin)

    @staticmethod
    async def update(*, request: Request, pk: int, obj: UpdateMenuParam) -> int:
        async with async_db_session.begin() as db:
            if request.user.user_type == '00':
                is_admin = 1
            else:
                is_admin = 0
            menu = await menu_dao.get(db, pk, is_admin)
            if not menu:
                raise errors.NotFoundError(msg='菜单不存在')
            if menu.title != obj.title:
                if await menu_dao.get_by_title(db, obj.title, is_admin):
                    raise errors.ForbiddenError(msg='菜单标题已存在')
            if obj.parent_id:
                parent_menu = await menu_dao.get(db, obj.parent_id, is_admin)
                if not parent_menu:
                    raise errors.NotFoundError(msg='父级菜单不存在')
            if obj.parent_id == menu.id:
                raise errors.ForbiddenError(msg='禁止关联自身为父级')
            count = await menu_dao.update(db, pk, obj)
            return count

    @staticmethod
    async def delete(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            if request.user.user_type == '00':
                is_admin = 1
            else:
                is_admin = 0
            children = await menu_dao.get_children(db, pk, is_admin)
            if children:
                raise errors.ForbiddenError(msg='菜单下存在子菜单，无法删除')
            menu = await menu_dao.get(db, pk, is_admin)
            if not menu:
                raise errors.NotFoundError(msg='菜单不存在')
            count = await menu_dao.delete(db, pk)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count


menu_service: MenuService = MenuService()
