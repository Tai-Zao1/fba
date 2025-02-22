#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, Request

from backend.app.common.schema.role import (
    CreateRoleParam,
    GetRoleDetail,
    UpdateRoleMenuParam,
    UpdateRoleParam,
    UpdateRoleRuleParam,
)
from backend.app.common.service.data_rule_service import data_rule_service
from backend.app.common.service.menu_service import menu_service
from backend.app.common.service.role_service import role_service
from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession
from backend.utils.serializers import select_as_dict, select_list_serialize

router = APIRouter()


@router.get('/all', summary='获取所有角色',
            dependencies=[
                DependsJwtAuth,
                Depends(RequestPermission('sys:role:list')),
                DependsRBAC
            ])
async def get_all_roles(request: Request) -> ResponseSchemaModel[list[GetRoleDetail]]:
    roles = await role_service.get_all(request=request)
    data = select_list_serialize(roles)
    return response_base.success(data=data)


@router.get('/{pk}/all', summary='获取用户所有角色', dependencies=[DependsJwtAuth])
async def get_user_all_roles(request: Request, pk: Annotated[int, Path(...)]) -> ResponseSchemaModel[
    list[GetRoleDetail]]:
    roles = await role_service.get_by_user(request=request, pk=pk)
    data = select_list_serialize(roles)
    return response_base.success(data=data)


@router.get('/{pk}/menus', summary='获取角色所有菜单', dependencies=[DependsJwtAuth])
async def get_role_all_menus(request: Request, pk: Annotated[int, Path(...)]) -> ResponseSchemaModel[
    list[dict[str, Any]]]:
    menu = await menu_service.get_role_menu_tree(request=request, pk=pk)
    return response_base.success(data=menu)


@router.get('/{pk}/rules', deprecated=True, description='此接口作废', summary='获取角色所有数据规则',
            dependencies=[DependsJwtAuth])
async def get_role_all_rules(request: Request, pk: Annotated[int, Path(...)]) -> ResponseSchemaModel[list[int]]:
    rule = await data_rule_service.get_role_rules(request=request, pk=pk)
    return response_base.success(data=rule)


@router.get('/{pk}', summary='获取角色详情',
            dependencies=[DependsJwtAuth,
                          Depends(RequestPermission('sys:role:query')),
                          DependsRBAC
                          ])
async def get_role(reqeust: Request, pk: Annotated[int, Path(...)]) -> ResponseSchemaModel[GetRoleDetail]:
    role = await role_service.get(reqeust=reqeust, pk=pk)
    data = GetRoleDetail(**select_as_dict(role))
    return response_base.success(data=data)


@router.get(
    '',
    summary='（模糊条件）分页获取所有角色',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
        Depends(RequestPermission('sys:role:list')),
        DependsRBAC
    ],
)
async def get_pagination_roles(
        request: Request,
        db: CurrentSession,
        name: Annotated[str | None, Query()] = None,
        status: Annotated[int | None, Query()] = None,
) -> ResponseSchemaModel[PageData[GetRoleDetail]]:
    role_select = await role_service.get_select(request=request, name=name, status=status)
    page_data = await paging_data(db, role_select)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建角色',
    dependencies=[
        Depends(RequestPermission('sys:role:add')),
        DependsRBAC,
    ],
)
async def create_role(
        request: Request,
        obj: CreateRoleParam) -> ResponseModel:
    await role_service.create(request=request, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新角色',
    dependencies=[
        Depends(RequestPermission('sys:role:edit')),
        DependsRBAC,
    ],
)
async def update_role(pk: Annotated[int, Path(...)],
                      obj: UpdateRoleParam,
                      request: Request
                      ) -> ResponseModel:
    count = await role_service.update(request=request, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/menu',
    summary='更新角色菜单',
    dependencies=[
        Depends(RequestPermission('sys:role:edit')),
        DependsRBAC,
    ],
)
async def update_role_menus(
        request: Request,
        pk: Annotated[int, Path(...)], menu_ids: UpdateRoleMenuParam,
) -> ResponseModel:
    count = await role_service.update_role_menu(request=request, pk=pk, menu_ids=menu_ids)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/rule',
    summary='更新角色数据权限规则',
    deprecated=True,
    description='此接口作废',
)
async def update_role_rules(
        request: Request, pk: Annotated[int, Path(...)], rule_ids: UpdateRoleRuleParam
) -> ResponseModel:
    count = await role_service.update_role_rule(request=request, pk=pk, rule_ids=rule_ids)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='（批量）删除角色',
    dependencies=[
        Depends(RequestPermission('sys:role:del')),
        DependsRBAC,
    ],
)
async def delete_role(request: Request, pk: Annotated[list[int], Query(...)]) -> ResponseModel:
    count = await role_service.delete(request=request, pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
