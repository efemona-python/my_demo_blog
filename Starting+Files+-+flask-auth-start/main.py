import werkzeug
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'black-sheep'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CREATE TABLE
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))



# Line below only required once, when creating DB.
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        password = request.form.get('password')
        hashed_and_salted_password = generate_password_hash(password=password,
                                                            method='pbkdf2:sha256',
                                                            salt_length=8)

        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hashed_and_salted_password
        )
        # alternatively
        # data = request.form.to_dict()
        # data['password'] = hashed_and_salted_password
        # new_user = User(**data)
        db.session.add(new_user)
        db.session.commit()
        # Log in and authenticate user after adding details to database.
        login_user(new_user)
        return redirect(url_for('secrets'))
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == "POST":
        # Find user by email entered.
        email = request.form.get("email")
        plain_password = request.form.get("password")
        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            error = 'Your email does not exist. Please try again'
        else:
            if check_password_hash(pwhash=user.password, password=plain_password):
                flash('You were successfully logged in')
                login_user(user)
                return redirect(url_for('secrets'))
            error = 'invalid password entered'
    return render_template("login.html", error=error)


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory('static/files', filename='cheat_sheet.pdf', as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
