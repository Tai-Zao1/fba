#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, Field

from backend.app.common.schema.data_rule import GetDataRuleDetail
from backend.app.common.schema.menu import GetMenuDetail
from backend.common.enums import StatusType
from backend.common.schema import SchemaBase


class RoleSchemaBase(SchemaBase):
    name: str
    status: StatusType = Field(default=StatusType.enable.value)
    store_id: int | None = None
    remark: str | None = None


class CreateRoleParam(RoleSchemaBase):
    pass


class UpdateRoleParam(RoleSchemaBase):
    pass


class UpdateRoleMenuParam(SchemaBase):
    menus: list[int]


class UpdateRoleRuleParam(SchemaBase):
    rules: list[int]


class GetRoleDetail(RoleSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

    created_time: datetime
    updated_time: datetime | None = None
    menus: list[GetMenuDetail | None] = []
    rules: list[GetDataRuleDetail | None] = []
