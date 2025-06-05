import pandas as pd
import numpy as np
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
import pickle
import os
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.user_event import UserEvent
from app.models.product import Product
from app.models.user import User
from app.schemas.recommendation import RecommendationCreate

logger = logging.getLogger(__name__)

class CollaborativeFilteringModel:
    """Collaborative filtering recommendation model using matrix factorization"""
    
    def __init__(self, model_path=None):
        self.model_path = model_path or os.path.join(settings.MODEL_PATH, "cf_model.pkl")
        self.model = self._load_model()
    
    def _load_model(self):
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    return pickle.load(f)
            else:
                logger.warning(f"Model file not found at {self.model_path}. Using fallback model.")
                return self._create_fallback_model()
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return self._create_fallback_model()
    
    def _create_fallback_model(self):
        # Simple fallback model when the real model is not available
        return {
            'user_factors': {},
            'item_factors': {},
            'global_mean': 0.0
        }
    
    def predict(self, user_id: int, product_ids: List[int]) -> List[tuple]:
        """Predict scores for user-item pairs"""
        try:
            if user_id not in self.model['user_factors']:
                # Cold start - return default scores
                return [(product_id, self.model['global_mean']) for product_id in product_ids]
                
            user_vector = self.model['user_factors'][user_id]
            
            # Calculate scores for each product
            scores = []
            for product_id in product_ids:
                if product_id in self.model['item_factors']:
                    item_vector = self.model['item_factors'][product_id]
                    score = np.dot(user_vector, item_vector) + self.model['global_mean']
                    scores.append((product_id, float(score)))
                else:
                    scores.append((product_id, self.model['global_mean']))
            
            # Sort by score in descending order
            return sorted(scores, key=lambda x: x[1], reverse=True)
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            return [(product_id, 0.5) for product_id in product_ids]

class ContentBasedModel:
    """Content-based recommendation model using product features"""
    
    def __init__(self, model_path=None):
        self.model_path = model_path or os.path.join(settings.MODEL_PATH, "cb_model.pkl")
        self.model = self._load_model()
    
    def _load_model(self):
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    return pickle.load(f)
            else:
                logger.warning(f"Model file not found at {self.model_path}. Using fallback model.")
                return self._create_fallback_model()
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return self._create_fallback_model()
    
    def _create_fallback_model(self):
        # Simple fallback model when the real model is not available
        return {
            'product_vectors': {},
            'similarity_matrix': {}
        }
    
    def find_similar(self, product_id: int, limit: int = 5) -> List[tuple]:
        """Find products similar to the given product"""
        try:
            if product_id not in self.model['similarity_matrix']:
                # Product not in model, return random products
                product_ids = list(self.model['product_vectors'].keys())
                if not product_ids:
                    return []
                    
                # Take random products if available
                if len(product_ids) > limit:
                    selected_ids = np.random.choice(product_ids, size=limit, replace=False)
                else:
                    selected_ids = product_ids
                
                return [(pid, 0.5) for pid in selected_ids]
            
            # Get similarity scores
            similarities = self.model['similarity_matrix'][product_id]
            
            # Sort and return top products (excluding the input product)
            sorted_prods = sorted(
                [(pid, score) for pid, score in similarities.items() if pid != product_id],
                key=lambda x: x[1], 
                reverse=True
            )
            
            return sorted_prods[:limit]
        except Exception as e:
            logger.error(f"Error finding similar products: {str(e)}")
            return []

# Initialize recommendation models
cf_model = CollaborativeFilteringModel()
cb_model = ContentBasedModel()

def get_personalized_recommendations(db: Session, user_id: int, limit: int = 10, algorithm: Optional[str] = None):
    """Get personalized recommendations for a user"""
    try:
        # Get all available products
        products = db.query(Product).all()
        product_ids = [p.id for p in products]
        
        if not algorithm or algorithm.lower() == "collaborative":
            # Use collaborative filtering by default
            recommendations = cf_model.predict(user_id, product_ids)
        elif algorithm.lower() == "content":
            # Use content-based as fallback
            # Get user's recently viewed or purchased products
            recent_events = db.query(UserEvent).filter(
                UserEvent.user_id == user_id,
                UserEvent.event_type.in_(["view", "purchase"]),
                UserEvent.timestamp >= datetime.now() - timedelta(days=30)
            ).order_by(UserEvent.timestamp.desc()).limit(5).all()
            
            if not recent_events:
                # No recent activity, use trending products
                return db.query(Product).order_by(Product.id.desc()).limit(limit).all()
            
            # Get similar products to those the user interacted with
            similar_products = []
            for event in recent_events:
                if event.product_id:
                    similar = cb_model.find_similar(event.product_id, limit=3)
                    similar_products.extend(similar)
            
            # Sort by similarity score and take top ones
            recommendations = sorted(similar_products, key=lambda x: x[1], reverse=True)
        else:
            # Invalid algorithm
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        # Get the actual product objects for the recommended IDs
        recommended_ids = [rec[0] for rec in recommendations[:limit]]
        recommended_products = db.query(Product).filter(Product.id.in_(recommended_ids)).all()
        
        # Sort products in the same order as recommendations
        id_to_position = {rec[0]: i for i, rec in enumerate(recommendations[:limit])}
        sorted_products = sorted(recommended_products, key=lambda p: id_to_position.get(p.id, 9999))
        
        return sorted_products
    except Exception as e:
        logger.error(f"Error generating personalized recommendations: {str(e)}")
        # Fallback to most popular products
        return db.query(Product).order_by(Product.id.desc()).limit(limit).all()

def get_similar_products(db: Session, product_id: int, user_id: Optional[int] = None, limit: int = 5):
    """Get products similar to the specified product"""
    try:
        # Get similar product IDs
        similar_ids = cb_model.find_similar(product_id, limit=limit)
        
        if not similar_ids:
            # If no similar products found, return random products
            return db.query(Product).filter(Product.id != product_id).order_by(func.random()).limit(limit).all()
        
        # Get the actual product objects
        product_ids = [pid for pid, _ in similar_ids]
        products = db.query(Product).filter(Product.id.in_(product_ids)).all()
        
        # Sort products by similarity score
        id_to_score = {pid: score for pid, score in similar_ids}
        sorted_products = sorted(products, key=lambda p: id_to_score.get(p.id, 0), reverse=True)
        
        return sorted_products
    except Exception as e:
        logger.error(f"Error finding similar products: {str(e)}")
        # Fallback to random products
        return db.query(Product).filter(Product.id != product_id).order_by(func.random()).limit(limit).all()