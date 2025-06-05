from app.db.session import engine
from app.models.user import User
from app.models.product import Product, Category
from app.models.recommendation import Recommendation
from app.models.user_event import UserEvent
from app.db.session import Base

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
