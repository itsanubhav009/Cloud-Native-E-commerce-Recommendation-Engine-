"""
Initialization script for loading sample data into the database
"""
import sys
import os
import logging
from sqlalchemy.orm import Session
import random
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.product import Product, Category
from app.models.recommendation import Recommendation
from app.models.user_event import UserEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data
USERS = [
    {"email": "admin@example.com", "username": "admin", "hashed_password": "password123hash", "is_admin": True},
    {"email": "user1@example.com", "username": "user1", "hashed_password": "password123hash"},
    {"email": "user2@example.com", "username": "user2", "hashed_password": "password123hash"},
    {"email": "user3@example.com", "username": "user3", "hashed_password": "password123hash"},
]

CATEGORIES = [
    {"name": "Electronics", "description": "Electronic devices and accessories"},
    {"name": "Clothing", "description": "Apparel and fashion items"},
    {"name": "Home & Kitchen", "description": "Products for home and kitchen"},
    {"name": "Books", "description": "Books and reading materials"},
]

PRODUCTS = [
    {"name": "Smartphone", "description": "Latest smartphone with advanced features", "price": 599.99, "image_url": "smartphone.jpg", "stock": 50, "category_id": 1},
    {"name": "Laptop", "description": "High-performance laptop for professionals", "price": 999.99, "image_url": "laptop.jpg", "stock": 30, "category_id": 1},
    {"name": "Headphones", "description": "Noise-cancelling wireless headphones", "price": 149.99, "image_url": "headphones.jpg", "stock": 100, "category_id": 1},
    {"name": "T-shirt", "description": "Comfortable cotton t-shirt", "price": 29.99, "image_url": "tshirt.jpg", "stock": 200, "category_id": 2},
    {"name": "Jeans", "description": "Classic blue jeans", "price": 59.99, "image_url": "jeans.jpg", "stock": 150, "category_id": 2},
    {"name": "Coffee Maker", "description": "Automatic coffee maker", "price": 89.99, "image_url": "coffeemaker.jpg", "stock": 40, "category_id": 3},
    {"name": "Blender", "description": "High-speed blender for smoothies", "price": 69.99, "image_url": "blender.jpg", "stock": 60, "category_id": 3},
    {"name": "Novel", "description": "Bestselling fiction novel", "price": 14.99, "image_url": "novel.jpg", "stock": 100, "category_id": 4},
    {"name": "Cookbook", "description": "Recipes from around the world", "price": 24.99, "image_url": "cookbook.jpg", "stock": 80, "category_id": 4},
]

def create_sample_data(db: Session):
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            logger.info("Database already contains data. Skipping initialization.")
            return
            
        # Create categories
        logger.info("Creating categories...")
        categories = []
        for cat_data in CATEGORIES:
            category = Category(**cat_data)
            db.add(category)
            categories.append(category)
        db.commit()
        
        # Create products
        logger.info("Creating products...")
        products = []
        for prod_data in PRODUCTS:
            category_id = prod_data.pop("category_id")
            product = Product(**prod_data)
            product.categories.append(categories[category_id-1])
            db.add(product)
            products.append(product)
        db.commit()
        
        # Create users
        logger.info("Creating users...")
        users = []
        for user_data in USERS:
            user = User(**user_data)
            db.add(user)
            users.append(user)
        db.commit()
        
        # Create user events
        logger.info("Creating user events...")
        event_types = ["view", "cart_add", "purchase"]
        
        for user in users:
            # Each user gets 5-15 random events
            num_events = random.randint(5, 15)
            for _ in range(num_events):
                product = random.choice(products)
                event_type = random.choice(event_types)
                
                # Random timestamp in the last 30 days
                days_ago = random.randint(0, 30)
                timestamp = datetime.now() - timedelta(days=days_ago)
                
                event = UserEvent(
                    user_id=user.id,
                    product_id=product.id,
                    event_type=event_type,
                    session_id=f"session-{random.randint(1000, 9999)}",
                    timestamp=timestamp,
                    metadata={"referrer": "search", "device": "mobile"}
                )
                db.add(event)
        db.commit()
        
        # Create recommendations
        logger.info("Creating sample recommendations...")
        algorithms = ["collaborative", "content-based"]
        
        for user in users:
            # Each user gets 3-5 recommendations
            num_recommendations = random.randint(3, 5)
            for _ in range(num_recommendations):
                product = random.choice(products)
                algorithm = random.choice(algorithms)
                
                recommendation = Recommendation(
                    user_id=user.id,
                    product_id=product.id,
                    score=random.uniform(0.5, 1.0),
                    algorithm=algorithm
                )
                db.add(recommendation)
        db.commit()
        
        logger.info("Sample data created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")
        db.rollback()
        raise

if __name__ == "__main__":
    logger.info("Initializing database with sample data...")
    db = SessionLocal()
    try:
        create_sample_data(db)
    finally:
        db.close()
