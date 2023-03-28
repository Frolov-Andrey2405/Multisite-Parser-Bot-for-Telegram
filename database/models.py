from typing import Annotated, Optional
from datetime import datetime
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import registry
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy import func
import environ
from pathlib import Path

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
env_file = Path(__file__).parent.resolve() / '.env'
environ.Env.read_env(env_file)

ENGINE = create_engine(env('DATABASE_CONNECT'))

str_400 = Annotated[str, 400]
str_700 = Annotated[str, 700]

class Base(DeclarativeBase):
    registry = registry(
        type_annotation_map={
            str_400: String(400),
            str_700: String(700),
        }
    )

class Vfx(Base):
    __tablename__ = "vfx"

    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str_400] = mapped_column(unique=True)
    download_link: Mapped[str_400] = mapped_column(unique=True)
    data_created: Mapped[datetime] = mapped_column(server_default=func.CURRENT_TIMESTAMP())


class Blend(Base):
    __tablename__ = "blend"

    id: Mapped[int] = mapped_column(primary_key=True)
    off_link: Mapped[str_400] = mapped_column(unique=True)
    url_on_image: Mapped[Optional[str_700]]
    data_created: Mapped[datetime] = mapped_column(server_default=func.CURRENT_TIMESTAMP())


class Version(Base):

    __tablename__ = "version"
    __table_args__  = (
        UniqueConstraint("vfx_id", "blend_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str_400]
    vfx_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vfx.id", ondelete='CASCADE'))
    blend_id: Mapped[Optional[int]] = mapped_column(ForeignKey("blend.id", ondelete='SET NULL'))
    addon_version: Mapped[Optional[str_400]]
    data_created: Mapped[datetime] = mapped_column(server_default=func.CURRENT_TIMESTAMP())

if __name__ == '__main__':
    Base.metadata.create_all(ENGINE)


