from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    items = relationship("Item", back_populates="owner")
    incomplete_items = relationship("Invalid_Item", back_populates="owner")

class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True, index=True)
    inc_type = Column(String, index=True)
    inc_detail = Column(String, index=True)
    pic = Column(String, index=True)
    lat = Column(Float, index=True)
    lon = Column(Float, index=True)
    url = Column(String, index=True)
    is_active = Column(Boolean, index=True)
    timestamp = Column(String, index=True)
    owner_id = Column(String, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")

class Invalid_Item(Base):
    __tablename__= "invalid_items"

    id = Column(String, primary_key=True, index=True)
    data = Column(String, primary_key=True, index=True)
    timestamp = Column(String, index=True)
    owner_id = Column(String, ForeignKey("users.id"))

    owner = relationship("User", back_populates="incomplete_items")
