from datetime import datetime

from pydantic import ConfigDict, Field

from backend.app.admin.schema.user import AuthSchemaBase
from backend.common.schema import SchemaBase


class StoreSchema(SchemaBase):
    name: str
    code: str


class GetStoreInfoList(StoreSchema):
    """
    店铺详情
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: int
    created_by: int | None = None
    created_time: datetime | None = None
    updated_by: int | None = None
    updated_time: datetime | None = None
    province_id: int
    city_id: int
    area_id: int
    address: str | None = None
    logo: str | None = None

    # 地址信息
    province_name: str
    city_name: str
    area_name: str

    # 用户信息
    user_id: int
    username: str
    phone: str


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
    created_ty: int | None = None
    updated_ty: int | None = None


class CreateStoreUserParam(AuthSchemaBase):
    """
    创建店铺用户
    """
    username: str | None = None
    nickname: str | None = None


class ReviewStoreParam(SchemaBase):
    """
    审核店铺
    """
    id: int
    remark: str | None = None
    status: int = Field(description='1:审核通过， 2：审核不通过')
