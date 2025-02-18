from pydantic import ConfigDict
from sqlalchemy.orm import session

from backend.app.admin.model.address import Address
from backend.common.schema import SchemaBase


class AddressSchemaBase(SchemaBase):
    name: str


class GetAddressDetail(AddressSchemaBase):

    id: int
    adcode: int
    pcode: int
