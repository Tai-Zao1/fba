from typing import List

from pydantic import ConfigDict, Field

from backend.app.admin.schema.user import AuthSchemaBase, UserStoreIns
from backend.common.schema import SchemaBase

class StoreSchema(SchemaBase):
    name: str
    code: str


class GetStoreInfoList(StoreSchema):
    """
    店铺详情
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(...)
    name: str = Field(...)
    code: str = Field(...)
    status: int = Field(...)
    province_id: int = Field(alias="provinceId")
    city_id: int = Field(alias="cityId")
    area_id: int = Field(alias="areaId")
    address: str | None = None
    logo: str | None = None
    
    # 地址信息
    province_name: str = Field(alias="provinceName")
    city_name: str = Field(alias="cityName")
    area_name: str = Field(alias="areaName")

    # 用户信息
    user_id: int = Field(alias="userId")
    username: str = Field(alias="username")
    phone: str = Field(alias="phone")

class CreateStoreParam(StoreSchema):
    """
    创建店铺
    """
    username: str
    phone: str
    province_id: int
    city_id: int
    area_id: int
    address: str | None = None
    logo: str | None = None

class CreateStoreUserParam(AuthSchemaBase):
    """
    创建店铺用户
    """
    username: str | None = None
    nickname: str | None = None