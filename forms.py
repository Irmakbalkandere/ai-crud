from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email, Length

class UserForm(FlaskForm):
    name = StringField(
        "name",
        validators=[
            DataRequired(message="İsim zorunlu"),
            Length(min=2, max=100, message="İsim 2-100 karakter olmalı"),
        ],
    )
    email = StringField(
        "email",
        validators=[
            DataRequired(message="Email zorunlu"),
            Email(message="Geçerli bir email gir"),
            Length(max=120, message="Email 120 karakterden kısa olmalı"),
        ],
    )
