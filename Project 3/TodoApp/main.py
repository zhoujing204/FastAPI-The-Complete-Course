from fastapi import FastAPI, Depends, status, Path, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from models import Todos, Users
from routers import auth, todos, admin, users

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
async def read_all(db : db_dependency):
    return db.query(Todos).all()

@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()


# app.include_router(auth.router)
# app.include_router(todos.router)
# app.include_router(admin.router)
# app.include_router(users.router)