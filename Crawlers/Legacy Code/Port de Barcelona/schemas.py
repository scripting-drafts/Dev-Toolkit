from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class Incident(BaseModel):
    id:str
    inc_type:str
    inc_detail:str
    pic:str
    lat:float
    lon:float
    url:str
    is_active:bool
    timestamp:datetime = datetime.now()

class Item(Incident):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class Invalid_Incident(BaseModel):
    id:str
    data:str
    timestamp:datetime = datetime.now()

class Invalid_Item(Invalid_Incident):
    id: str
    owner_id: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    id: str

class User(UserBase):
    id: str
    items: List[Item] = []

    class Config:
        orm_mode = True
