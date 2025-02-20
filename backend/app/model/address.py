from typing import Optional

from sqlalchemy import Integer, String, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base


class Address(Base):
    __tablename__ = "base_address"  # 表名
    __table_args__ = {"comment": "地址库"}  # 表注释

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="地址id"
    )
    adcode: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="区域编码"
    )
    pcode: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="上一级编码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="区名称"
    )
    first_pinyin: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="拼音首字母"
    )
    full_pinyin: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="全拼音"
    )
    longitude: Mapped[Optional[float]] = mapped_column(
        DECIMAL(18, 10), nullable=True, comment="经度"
    )
    latitude: Mapped[Optional[float]] = mapped_column(
        DECIMAL(18, 10), nullable=True, comment="纬度"
    )
    center: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="高德地图城市中心点"
    )
    level: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="区级别"
    )
    hot: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="热门城市"
    )
