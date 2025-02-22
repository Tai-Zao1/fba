from backend.common.schema import SchemaBase


class AddressSchemaBase(SchemaBase):
    name: str


class GetAddressDetail(AddressSchemaBase):
    id: int
    adcode: int
    pcode: int
