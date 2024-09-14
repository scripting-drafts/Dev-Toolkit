from sqlalchemy.orm import Session
import models, schemas


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session, skip: int = 0):
    return db.query(models.User).offset(skip).all()

def get_item(db: Session, item_id: str):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def get_items(db: Session, skip: int = 0):
    return db.query(models.Item).offset(skip).all()

def get_invalid_items(db: Session, skip: int = 0):
    return db.query(models.Invalid_Item).offset(skip).all()

def create_valid_item(db: Session, item: schemas.Incident, user_id: str):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_invalid_item(db: Session, item: schemas.Invalid_Incident, user_id: str):
    db_item = models.Invalid_Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
