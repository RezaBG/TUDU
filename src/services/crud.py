from sqlalchemy.orm import Session
from fastapi import HTTPException, status

# Fetch a single item by ID
def get_item_by_id(model, item_id: int, db: Session):
    item = db.query(model).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} with ID {item_id} not found"
        )
    return item

# Create a new item
def create_item(model, data, db: Session):
    try:
        new_item = model(**data)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create {model.__name__}: {str(e)}"
        )

# Delete an item by ID
def delete_item(model, item_id: int, db: Session):
    item = get_item_by_id(model, item_id, db)
    db.delete(item)
    db.commit()
    return {"message": f"{model.__name__} with ID {item_id} deleted successfully"}