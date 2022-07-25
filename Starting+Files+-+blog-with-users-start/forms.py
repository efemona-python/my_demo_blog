from datetime import datetime
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL, Email, Length, InputRequired, ValidationError
from wtforms.widgets import PasswordInput


# WTForm


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

    def get_data(self,current_user):
        dictionary = {'title': self.title.data,
                      'subtitle': self.subtitle.data,
                      'user_id': current_user.id,
                      'img_url': self.img_url.data,
                      'body': self.body.data,
                      'date': datetime.today()
                      }
        return dictionary


class CreateCommentForm(FlaskForm):
    content = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")

    def get_data(self, current_user,post_id):
        dictionary = {'user_id': current_user.id,
                      'blog_post_id': post_id,
                      'content': self.content.data,
                      'date': datetime.today()
                      }
        return dictionary


# CREATE LOGIN FORM
class Login(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', widget=PasswordInput(hide_value=False),
                             validators=[DataRequired(), Length(min=8, max=32)])
    submit = SubmitField(label="login")

    def get_data(self):
        dictionary = {'email': self.email.data,
                      'password': self.password.data,
                      }
        return dictionary

    # validate login here
    # def validate_email(self, email):
    #     try:
    #         if not User.check_username_exist(email):
    #             raise ValueError()
    #     except ValueError:
    #         raise validators.ValidationError('username or password does not exist')
    #
    # def validate_password(self, password):
    #     self.validate_username(self.username)
    #     try:
    #         if not User.check_password(password, self.username):
    #             raise ValueError()
    #     except ValueError:
    #         raise validators.ValidationError('incorrect password')


# CREATE REGISTER FORM
class Register(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', widget=PasswordInput(hide_value=False),
                             validators=[DataRequired(), Length(min=8, max=32)])
    confirm = PasswordField(label='repeat password',
                            widget=PasswordInput(hide_value=False),
                            validators=[DataRequired(), Length(min=8, max=32)])
    terms = BooleanField(label="terms & conditions", validators=[DataRequired()])
    submit = SubmitField(label="Register")

    def validate_password(self, password):
        if password.data != self.confirm.data:
            raise ValidationError('Password mismatch')

    def check_email(self, user):
        email = user.query.filter_by(email=self.email.data).first()
        if email:
            raise ValidationError('email address already registered')
        return True

    def get_data(self):
        dictionary = {'name': self.name.data,
                      'email': self.email.data,
                      'password': generate_password_hash(self.password.data,
                                                         method='pbkdf2:sha256',
                                                         salt_length=8)
                      }
        return dictionary

    # password hashing here
