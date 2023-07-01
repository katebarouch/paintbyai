"""CRUD operations."""
from model import db, User, connect_to_db, Painting, Paint

def create_user(email, password):
    """Create and return a new user."""

    user = User(email=email, password=password)
    db.session.add(user) 
    db.session.commit()

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

def create_painting(user_id, media, prompt, dalle_img=None, vectorized_img=None, final_img=None):
    """Create and return a new painting"""
    painting = Painting(dalle_img=dalle_img, vectorized_img=vectorized_img, final_img=final_img, user_id=user_id, media=media, prompt=prompt)
    db.session.add(painting)
    db.session.commit()

    return painting

def create_paint(painting_id, paint_id, hexcode, user_id):
    """Create and return a new paint"""

    paint = Paint(painting_id = painting_id, paint_id = paint_id, hexcode = hexcode, user_id = user_id)

    db.session.add(paint)
    db.session.commit()
    return paint
