from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.recommendation import Recommendation, UserRecommendation
from app.schemas.product import Product
from app.crud import recommendation as crud_recommendation
from app.core.auth import get_current_user, get_optional_user
from app.ml.recommender import get_personalized_recommendations, get_similar_products
from app.models.user import User

router = APIRouter()

@router.get("/user/", response_model=List[UserRecommendation])
def get_user_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    algorithm: Optional[str] = None
):
    """
    Get personalized recommendations for the current logged-in user
    """
    return crud_recommendation.get_user_recommendations(
        db, 
        user_id=current_user.id, 
        limit=limit,
        algorithm=algorithm
    )

@router.get("/anonymous/", response_model=List[Product])
def get_anonymous_recommendations(
    session_id: str,
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Get recommendations for anonymous users based on session data
    """
    return crud_recommendation.get_anonymous_recommendations(
        db,
        session_id=session_id,
        limit=limit
    )

@router.get("/similar/{product_id}", response_model=List[Product])
def get_similar_product_recommendations(
    product_id: int,
    db: Session = Depends(get_db),
    limit: int = 5,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get similar products to the one specified
    """
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    user_id = current_user.id if current_user else None
    return get_similar_products(db, product_id=product_id, user_id=user_id, limit=limit)

@router.post("/event/")
def record_user_event(
    event: UserEvent,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Record a user event for recommendation system training
    """
    # If user is logged in, use their ID
    if current_user:
        event.user_id = current_user.id
    
    crud_recommendation.record_user_event(db, event)
    return {"detail": "Event recorded successfully"}