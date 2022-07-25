import os

from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from functools import wraps
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, Login, Register, CreateCommentForm

# from flask_gravatar import Gravatar

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY')
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = u"A logged-in access is required."


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    all_comments = db.relationship('Comments', backref="parent_blog")

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

    def format_date(self):
        return self.date.split()[0]

    def get_comments(self):
        return db.session.query(Comments).filter_by(blog_post_id=self.id).order_by(Comments.date.desc()).all()


class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime)
    blog_post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def format_date(self):
        return self.date.date()


# CONFIGURE USER TABLE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    all_blog_posts = db.relationship('BlogPost', backref="post_author")
    all_comments = db.relationship('Comments', backref="comment_author")


#
# db.drop_all()
# db.create_all()


@app.route('/register', methods=['POST', 'GET'])
def register():
    register_form = Register()
    if register_form.is_submitted() and register_form.check_email(User):
        new_user = User(**register_form.get_data())
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Thank you for registering!')
        return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=register_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    login_form = Login()
    if login_form.validate_on_submit():
        data = login_form.get_data()
        # get user password from db
        user = db.session.query(User).filter_by(email=data['email']).first()
        if not user:
            error = "your email is incorrect or doesn't exit."
            flash(error)
        else:
            if check_password_hash(user.password, data['password']):
                login_user(user)
                flash('You were successfully logged in')
                return redirect(url_for('get_all_posts'))
            error = "Invalid password"
    return render_template("login.html", form=login_form, error=error)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    comment_form = CreateCommentForm()
    requested_post = BlogPost.query.get(post_id)
    comments = db.session.query(Comments).filter_by(blog_post_id=post_id).order_by(Comments.date.desc()).all()
    if comment_form.validate_on_submit():
        # create new comment
        comment = Comments(**comment_form.get_data(current_user, post_id))
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    return render_template("post.html", post=requested_post, form=comment_form, comments=comments)


@app.route("/edit-post/<int:post_id>", methods=['GET', 'POST'])
@login_required
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_post_form = CreatePostForm(**post.to_dict())
    if edit_post_form.validate_on_submit():
        current_user_data = edit_post_form.get_data(current_user)
        for key, value in current_user_data.items():
            setattr(post, key, value)
        db.session.commit()
        post.update_post(**current_user_data)
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_post_form)


@app.route("/new-post", methods=['GET', 'POST'])
@login_required
@admin_only
def add_new_post():
    add_new_form = CreatePostForm()
    if add_new_form.validate_on_submit():
        new_post = BlogPost(**add_new_form.get_data(current_user))
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=add_new_form)


@app.route("/delete/<int:post_id>")
@login_required
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)
