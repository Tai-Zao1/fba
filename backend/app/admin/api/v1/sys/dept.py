#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, Request

from backend.app.admin.schema.dept import CreateDeptParam, GetDeptDetail, UpdateDeptParam
from backend.app.admin.schema.user import GetCurrentUserInfoDetail
from backend.app.admin.service.dept_service import dept_service
from backend.app.admin.service.user_service import UserService
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.utils.serializers import select_as_dict

router = APIRouter()


@router.get('/{pk}', summary='获取部门详情', dependencies=[DependsJwtAuth])
async def get_dept(pk: Annotated[int, Path(...)],
                   request: Request
                   ) -> ResponseSchemaModel[GetDeptDetail]:
    store_id = request.user.store_id
    dept = await dept_service.get(pk=pk, store_id=store_id)
    data = GetDeptDetail(**select_as_dict(dept))
    return response_base.success(data=data)


@router.get('', summary='获取所有部门展示树', dependencies=[DependsJwtAuth])
async def get_all_depts_tree(
        request: Request,
        name: Annotated[str | None, Query()] = None,
        leader: Annotated[str | None, Query()] = None,
        phone: Annotated[str | None, Query()] = None,
        status: Annotated[int | None, Query()] = None,

) -> ResponseSchemaModel[list[dict[str, Any]]]:
    store_id = request.user.store_id
    dept = await dept_service.get_dept_tree(name=name, leader=leader, phone=phone, status=status, store_id=store_id)
    return response_base.success(data=dept)


@router.post(
    '',
    summary='创建部门',
    dependencies=[
        Depends(RequestPermission('sys:dept:add')),
        DependsRBAC,
    ],
)
async def create_dept(request: Request, obj: CreateDeptParam) -> ResponseModel:
    store_id = request.user.store_id
    obj.store_id = store_id
    await dept_service.create(obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新部门',
    dependencies=[
        Depends(RequestPermission('sys:dept:edit')),
        DependsRBAC,
    ],
)
async def update_dept(pk: Annotated[int, Path(...)], obj: UpdateDeptParam) -> ResponseModel:
    count = await dept_service.update(pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除部门',
    dependencies=[
        Depends(RequestPermission('sys:dept:del')),
        DependsRBAC,
    ],
)
async def delete_dept(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    count = await dept_service.delete(request=request, pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
