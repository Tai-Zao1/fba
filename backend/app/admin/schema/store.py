from datetime import datetime

from pydantic import ConfigDict, Field

from backend.app.admin.schema.user import AuthSchemaBase
from backend.common.schema import SchemaBase


class StoreSchema(SchemaBase):
    name: str = Field(description='店铺名称')
    code: str = Field(description='店铺编号')


class GetStoreInfoList(StoreSchema):
    """
    店铺详情
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='店铺ID')
    status: int = Field(description='店铺状态')
    created_by: int | None = Field(None, description='创建者')
    created_time: datetime | None = Field(None, description='创建时间')
    updated_by: int | None = Field(None, description='修改者')
    updated_time: datetime | None = Field(None, description='更新时间')
    province_id: int = Field(description='省份ID')
    city_id: int = Field(description='城市ID')
    area_id: int = Field(description='区县ID')
    address: str | None = Field(None, description='详细地址')
    logo: str | None = Field(None, description='店铺LOGO')

    # 地址信息
    province_name: str = Field(description='省份名称')
    city_name: str = Field(description='城市名称')
    area_name: str = Field(description='区县名称')

    # 用户信息
    user_id: int
    username: str
    phone: str


class CreateStoreParam(StoreSchema):
    """
    创建店铺
    """
    username: str = Field(description='店铺管理员姓名')
    phone: str = Field(description='店铺管理员手机号')
    province_id: int = Field(description='省份ID')
    city_id: int = Field(description='城市ID')
    area_id: int = Field(description='区县ID')
    address: str | None = Field(None, description='详细地址')
    logo: str | None = Field(None, description='店铺LOGO')


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
    id: int = Field(description='店铺ID')
    remark: str | None = Field(None, description='审核备注')
    status: int = Field(description='1:审核通过， 2：审核不通过')


class UpdateStoreParam(StoreSchema):
    """
    更店铺信息
    """
    id: int = Field(description='店铺ID')
    province_id: int = Field(description='省份ID')
    city_id: int = Field(description='城市ID')
    area_id: int = Field(description='区县ID')
    address: str | None = Field(None, description='详细地址')
    logo: str | None = Field(None, description='店铺LOGO')

