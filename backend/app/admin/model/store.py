from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class Store(Base):
    __tablename__ = "store"

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(String(20), nullable=False, comment='名称')
    code: Mapped[str] = mapped_column(String, nullable=False, comment='营业执照')
    province_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='省份ID')
    city_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='城市ID')
    area_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='区县ID')
    address: Mapped[str] = mapped_column(String, nullable=False, comment='详细地址')
    logo: Mapped[str] = mapped_column(String, nullable=False, comment='logo')
    status: Mapped[int] = mapped_column(default=1, comment='状态（0正常 1停用 2审核中')
