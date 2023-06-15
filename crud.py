"""CRUD operations."""
from model import db, User, connect_to_db, Painting

def create_user(email, password):
    """Create and return a new user."""

    user = User(email=email, password=password)
    return user

def get_all_users():
    users = User.query.all()
    return users
    
def get_user_by_id(user_id):
    user = User.query.get(user_id)
    return user

def get_user_by_email(email):
    user = User.query.filter(User.email==email).first()
    return user

def create_painting(dalle_img, vectorized_img, final_img, user_id):
    """Create and return a new painting"""

    painting = Painting(dalle_img = dalle_img, vectorized_img= vectorized_img, final_img=final_img, user_id=user_id)

    return painting
