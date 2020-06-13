from flask import Flask, render_template, redirect,request,url_for,flash
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,validators
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import login_user,login_required,logout_user,current_user,LoginManager,UserMixin

app = Flask(__name__)
app.config['SECRET_KEY']='fbfcba0ab308bfd68656b2409bf1fb8b'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt= Bcrypt(app)
login_manage = LoginManager()
login_manage.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True,nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    notes = db.relationship('Note', backref='author', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(60),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class AddNote(FlaskForm):
    field = StringField("Add a Note . . .", description="Add a Note . . .")
    submit = SubmitField("add-note")

@login_manage.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        user = User.query.filter_by(email=request.form["mail"]).first()
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('create'))
        else:
            flash('Unsuccessful Login ! incorrect username or password', 'danger')
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        us = User.query.filter_by(username=request.form["username"]).first()
        em = User.query.filter_by(email=request.form["emaill"]).first()
        if us :
            flash("username already taken",'warning')
            return redirect(url_for('register'))
        if em :
            flash("email already registered ", 'warning')
            return redirect(url_for('register'))
        hashed_pass = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user = User(username=request.form['username'], email=request.form['emaill'], password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        flash('Your account is created ', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/create')
def create():
    form = AddNote()
    user_id  = current_user.id
    todo = Note.query.filter_by(user_id=current_user.id)
    return render_template("create.html", form=form, todo=todo,user_id=user_id)




@app.route('/logout')
def logout():
    logout_user()
    return redirect((url_for('home')))



@app.route('/Add',methods=['POST'])
def Add():
    form = AddNote()
    if request.method=='POST':
        note = Note(text=form.field.data, author=current_user)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('create'))
    return redirect(url_for('create'))

@app.route('/update/<id>')
def update(id):
    return redirect(url_for('create'))

@app.route('/delete/<id>')
def delete(id):
    a = Note.query.filter_by(id=int(id)).first()
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for('create'))