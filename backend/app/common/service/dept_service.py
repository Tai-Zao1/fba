#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

from fastapi import Request

from backend.app.common.crud.crud_dept import dept_dao
from backend.app.common.model import Dept
from backend.app.common.schema.dept import CreateDeptParam, UpdateDeptParam
from backend.common.exception import errors
from backend.core.conf import settings
from backend.database.db import async_db_session
from backend.database.redis import redis_client
from backend.utils.build_tree import get_tree_data


class DeptService:
    @staticmethod
    async def get(*, request: Request, pk: int) -> Dept:
        async with async_db_session() as db:
            dept = await dept_dao.get(db, pk, request.user.store_id)
            if not dept:
                raise errors.NotFoundError(msg='部门不存在')
            return dept

    @staticmethod
    async def get_dept_tree(
        *, request: Request, name: str | None = None, leader: str | None = None,
            phone: str | None = None, status: int | None = None,
    ) -> list[dict[str, Any]]:
        async with async_db_session() as db:
            dept_select = await dept_dao.get_all(db=db, name=name, leader=leader,
                                                 phone=phone, status=status, store_id=request.user.store_id)
            tree_data = get_tree_data(dept_select)
            return tree_data

    @staticmethod
    async def create(*, request: Request, obj: CreateDeptParam) -> None:
        async with async_db_session.begin() as db:
            dept = await dept_dao.get_by_name(db, obj.name, request.user.store_id)
            if dept:
                raise errors.ForbiddenError(msg='部门名称已存在')
            if obj.parent_id:
                parent_dept = await dept_dao.get(db, obj.parent_id, request.user.store_id)
                if not parent_dept:
                    raise errors.NotFoundError(msg='父级部门不存在')
            await dept_dao.create(db, obj, request.user.store_id)

    @staticmethod
    async def update(*, request: Request, pk: int, obj: UpdateDeptParam) -> int:
        async with async_db_session.begin() as db:
            dept = await dept_dao.get(db, pk, store_id=request.user.store_id)
            if not dept:
                raise errors.NotFoundError(msg='部门不存在')
            if dept.name != obj.name:
                if await dept_dao.get_by_name(db, obj.name, store_id=request.user.store_id):
                    raise errors.ForbiddenError(msg='部门名称已存在')
            if obj.parent_id:
                parent_dept = await dept_dao.get(db, obj.parent_id, store_id=request.user.store_id)
                if not parent_dept:
                    raise errors.NotFoundError(msg='父级部门不存在')
            if obj.parent_id == dept.id:
                raise errors.ForbiddenError(msg='禁止关联自身为父级')
            count = await dept_dao.update(db, pk, obj)
            return count

    @staticmethod
    async def delete(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            store_id = request.user.store_id
            user_type = request.user.user_type
            dept = await dept_dao.get(db, pk, store_id=store_id)
            if not dept:
                raise errors.NotFoundError(msg='部门不存在')
            dept_user = await dept_dao.get_with_relation(db, pk, store_id)
            if dept_user:
                raise errors.ForbiddenError(msg='部门下存在用户，无法删除')
            children = await dept_dao.get_children(db, pk, store_id)
            if children:
                raise errors.ForbiddenError(msg='部门下存在子部门，无法删除')
            count = await dept_dao.delete(db, pk)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count


dept_service: DeptService = DeptService()
