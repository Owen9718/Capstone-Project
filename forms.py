
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired,Length

class LoginUser(FlaskForm):

    username = StringField('Username',validators=[InputRequired()])
    password = PasswordField('Password',validators=[InputRequired(),Length(min=5,max=25)])


class Search(FlaskForm):
    search = StringField('Search',render_kw={"placeholder": "Search For Recipe"})