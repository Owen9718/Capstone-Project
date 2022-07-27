from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()
def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    username = db.Column(db.Text,nullable=False,unique=True)
    password = db.Column(db.Text,nullable=False)

    @classmethod
    def register(cls, username, password):
        """Register user w/hashed password & return user."""
        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")
        user = User(username = username, password=hashed_utf8)
        db.session.add(user)
        # return instance of user w/username and hashed pwd
        return user


    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            # return user instance
            return u
        else:
            return False


class Saved_Recipe(db.Model):

    __tablename__="saved_recipes"

    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, nullable=False,unique=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id', ondelete='CASCADE'),)
    recipe_title = db.Column(db.Text,nullable=False)