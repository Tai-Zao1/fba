from typing import Annotated
from fastapi import APIRouter, Path

from backend.app.admin.schema.address import GetAddressDetail
from backend.app.admin.service.address_service import address_service
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.utils.serializers import select_as_dict

router = APIRouter()


@router.get("/{parent_id}", summary='根据上级取下级城市')
async def get_address_list(parent_id: Annotated[int, Path(...)]) -> ResponseSchemaModel[list[GetAddressDetail]] | None:
    # address_dataslist = GetAddressDetail(**select_as_dict(parent_id))
    data = await address_service.get_address_list(parent_id=parent_id)
    return response_base.success(data=data)
