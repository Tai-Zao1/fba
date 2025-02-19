from typing import Annotated

from fastapi import APIRouter, Query, Request

from backend.app.admin.schema.store import CreateStoreParam, GetStoreInfoList, ReviewStoreParam
from backend.app.admin.service.store_service import store_service
from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession

router = APIRouter()


@router.get("/list", summary='（模糊条件）分页获取所有商户', dependencies=[DependsJwtAuth, DependsPagination])
async def list_store(
        db: CurrentSession,
        store_name: Annotated[str | None, Query()] = None,
        province_id: Annotated[int | None, Query()] = None,
        city_id: Annotated[int | None, Query()] = None,
        area_id: Annotated[int | None, Query()] = None,
        status: Annotated[int | None, Query()] = None) -> ResponseSchemaModel[PageData[GetStoreInfoList]]:
    store_select = await store_service.get_select(store_name=store_name, province_id=province_id, city_id=city_id,
                                                  area_id=area_id, status=status)
    store_page = await paging_data(db, store_select)
    return response_base.success(data=store_page)


@router.post("/create", summary='创建店铺', dependencies=[DependsJwtAuth])
async def create_store(request: Request, obj: CreateStoreParam) -> ResponseSchemaModel:
    await store_service.add(request=request, obj=obj)
    return response_base.success()


@router.post("/review", summary='审核店铺', dependencies=[DependsJwtAuth])
async def review_store(request: Request, obj: ReviewStoreParam) -> ResponseSchemaModel:
    await store_service.review(request=request, obj=obj)
    return response_base.success()
