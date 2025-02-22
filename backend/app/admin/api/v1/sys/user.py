#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.sql.functions import current_user

from backend.app.common.schema.user import (
    AddUserParam,
    AvatarParam,
    GetCurrentUserInfoDetail,
    GetUserInfoDetail,
    RegisterUserParam,
    ResetPasswordParam,
    UpdateUserParam,
    UpdateUserRoleParam,
)
from backend.app.common.service.user_service import user_service
from backend.common.pagination import DependsPagination, paging_data, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession
from backend.utils.serializers import select_as_dict

router = APIRouter()


@router.post('/register', summary='注册平台用户', include_in_schema=False)
async def register_user(obj: RegisterUserParam) -> ResponseModel:
    await user_service.register(obj=obj, user_type='00')
    return response_base.success()


@router.post('/add', summary='添加用户', dependencies=[DependsRBAC, Depends(RequestPermission('sys:user:add'))])
async def add_user(request: Request, obj: AddUserParam) -> ResponseSchemaModel[GetUserInfoDetail]:
    await user_service.add(request=request, obj=obj)
    current_user = await user_service.get_userinfo(request=request, phone=obj.phone)
    data = GetUserInfoDetail(**select_as_dict(current_user))
    return response_base.success(data=data)


@router.post('/password/reset', summary='密码重置', dependencies=[DependsJwtAuth])
async def password_reset(request: Request, obj: ResetPasswordParam) -> ResponseModel:
    count = await user_service.pwd_reset(request=request, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.get('/me', summary='获取当前用户信息', dependencies=[DependsJwtAuth], response_model_exclude={'password'})
async def get_current_user(request: Request) -> ResponseSchemaModel[GetCurrentUserInfoDetail]:
    data = GetCurrentUserInfoDetail(**request.user.model_dump())
    return response_base.success(data=data)


@router.get('/{phone}', summary='查看用户信息', dependencies=[DependsJwtAuth])
async def get_user(request: Request, phone: Annotated[str, Path(...)]) -> ResponseSchemaModel[GetUserInfoDetail]:
    current_user = await user_service.get_userinfo(request=request, phone=phone)
    data = GetUserInfoDetail(**select_as_dict(current_user))
    return response_base.success(data=data)


@router.put('/{phone}', summary='更新用户信息', dependencies=[DependsJwtAuth])
async def update_user(request: Request, phone: Annotated[str, Path(...)], obj: UpdateUserParam) -> ResponseModel:
    count = await user_service.update(request=request, phone=phone, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{phone}/role',
    summary='更新用户角色',
    dependencies=[
        Depends(RequestPermission('sys:role:edit')),
        DependsRBAC,
    ],
)
async def update_user_role(
        request: Request, phone: Annotated[str, Path(...)], obj: UpdateUserRoleParam
) -> ResponseModel:
    await user_service.update_roles(request=request, phone=phone, obj=obj)
    return response_base.success()


@router.put('/{phone}/avatar', summary='更新头像', dependencies=[DependsJwtAuth])
async def update_avatar(request: Request, phone: Annotated[str, Path(...)], avatar: AvatarParam) -> ResponseModel:
    count = await user_service.update_avatar(request=request, phone=phone, avatar=avatar)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.get(
    '',
    summary='（模糊条件）分页获取所有用户',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
        DependsRBAC,
        Depends(RequestPermission('sys:user:query'))
    ],
)
async def get_pagination_users(
        db: CurrentSession,
        request: Request,
        dept: Annotated[int | None, Query()] = None,
        username: Annotated[str | None, Query()] = None,
        phone: Annotated[str | None, Query()] = None,
        status: Annotated[int | None, Query()] = None,
        user_id: Annotated[int | None, Query()] = None,
) -> ResponseSchemaModel[PageData[GetUserInfoDetail]]:
    user_select = await user_service.get_select(request=request,
                                                dept=dept,
                                                username=username,
                                                phone=phone,
                                                status=status,
                                                user_id=user_id)
    page_data = await paging_data(db, user_select)
    return response_base.success(data=page_data)


@router.put('/{pk}/super', summary='修改用户超级权限',
            dependencies=[DependsRBAC, Depends(RequestPermission('sys:user:edit'))])
async def super_set(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    count = await user_service.update_permission(request=request, pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/{pk}/staff', summary='修改用户后台登录权限',
            dependencies=[DependsRBAC, Depends(RequestPermission('sys:user:edit'))])
async def staff_set(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    count = await user_service.update_staff(request=request, pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/{pk}/status', summary='修改用户状态',
            dependencies=[DependsRBAC, Depends(RequestPermission('sys:user:edit'))])
async def status_set(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    count = await user_service.update_status(request=request, pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/{pk}/multi', summary='修改用户多点登录状态',
            dependencies=[DependsRBAC, Depends(RequestPermission('sys:user:edit'))])
async def multi_set(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    count = await user_service.update_multi_login(request=request, pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    path='/{user_id}',
    summary='用户注销',
    description='用户注销 != 用户登出，注销之后用户将从数据库删除',
    dependencies=[
        Depends(RequestPermission('sys:user:del')),
        DependsRBAC,
    ],
)
async def delete_user(request: Request, user_id: Annotated[int, Path(...)]) -> ResponseModel:
    count = await user_service.delete(request=request, user_id=user_id)
    if count > 0:
        return response_base.success()
    return response_base.fail()
