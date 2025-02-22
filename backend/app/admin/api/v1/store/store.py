from typing import Annotated

from fastapi import APIRouter, Query, Request, Depends

from backend.app.common.schema.store import CreateStoreParam, GetStoreInfoList, ReviewStoreParam, UpdateStoreParam
from backend.app.common.service.store_service import store_service
from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession

router = APIRouter()


@router.get("/list",
            summary='（模糊条件）分页获取所有商户',
            dependencies=[DependsJwtAuth, Depends(RequestPermission('tenant:store:list')), DependsRBAC,
                          DependsPagination])
async def list_store(
        db: CurrentSession,
        request: Request,
        store_name: Annotated[str | None, Query(description='店铺名称')] = None,
        province_id: Annotated[int | None, Query(description='省份id')] = None,
        city_id: Annotated[int | None, Query(description='城市id')] = None,
        area_id: Annotated[int | None, Query(description='区县id')] = None,
        status: Annotated[int | None, Query(description='店铺状态,0:审核中，1:审核通过，2:审核拒绝')] = None
) -> ResponseSchemaModel[PageData[GetStoreInfoList]]:
    store_select = await store_service.get_select(request=request, store_name=store_name,
                                                  province_id=province_id, city_id=city_id,
                                                  area_id=area_id, status=status)
    store_page = await paging_data(db, store_select)
    return response_base.success(data=store_page)


@router.post("/create", summary='创建店铺',
             dependencies=[DependsJwtAuth, Depends(RequestPermission('tenant:store:add')), DependsRBAC])
async def create_store(request: Request, obj: CreateStoreParam) -> ResponseSchemaModel:
    await store_service.add(request=request, obj=obj)
    return response_base.success()


@router.put("/review", summary='审核店铺',
            dependencies=[DependsJwtAuth, Depends(RequestPermission('tenant:store:review')), DependsRBAC])
async def review_store(request: Request, obj: ReviewStoreParam) -> ResponseSchemaModel:
    await store_service.review(request=request, obj=obj)
    return response_base.success()


@router.put("/update", summary='修改店铺信息',
            dependencies=[DependsJwtAuth, Depends(RequestPermission('Tenant:store:update')), DependsRBAC])
async def update_store(request: Request, obj: UpdateStoreParam) -> ResponseSchemaModel:
    await store_service.update(request=request, obj=obj)
    return response_base.success()
