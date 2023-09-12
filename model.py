from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """A user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    paintings = db.relationship("Painting", back_populates="users")

    def __repr__(self):
        return f'<User user_id={self.user_id} email={self.email}>'
    

class Painting(db.Model):
    """A painting."""

    __tablename__ = "paintings"

    painting_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    dalle_img = db.Column(db.String)
    vectorized_img = db.Column(db.String)
    final_img = db.Column(db.String)
    prompt = db.Column(db.String)
    media = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    users = db.relationship("User", back_populates="paintings")
    paints = db.relationship ("Paint", back_populates="paintings")

class Paint(db.Model):
    """A paint color."""

    __tablename__ = "paints"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    paint_id = db.Column(db.Integer)
    hexcode = db.Column(db.String)
    painting_id = db.Column(db.Integer, db.ForeignKey("paintings.painting_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    paintings = db.relationship("Painting", back_populates="paints")

    
def connect_to_db(flask_app, db_uri="postgresql:///paintbynumbers", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!- yay")


if __name__ == "__main__":
    print("main is called")
    from server import app

    connect_to_db(app)

    with app.app_context():
        db.create_all()
        print("All tables created!")
        
