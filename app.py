from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Regexp
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kvr_brick_works.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Prakasam district pincodes (simplified list for validation)
PRAKASAM_PINCODES = ['523001', '523002', '523101', '523108', '523109']

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    password = db.Column(db.String(128), nullable=False)

class Brick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    ingredients = db.Column(db.String(200), nullable=False)
    quality = db.Column(db.String(100), nullable=False)
    price_per_lot = db.Column(db.Float, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    brick_id = db.Column(db.Integer, db.ForeignKey('brick.id'), nullable=False)
    lots = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    brick = db.relationship('Brick', backref=db.backref('orders', lazy=True))

# Forms
class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    address = StringField('Delivery Address', validators=[DataRequired()])
    pincode = StringField('Pincode', validators=[DataRequired(), Regexp(r'^\d{6}$', message="Pincode must be 6 digits")])
    phone = StringField('Phone Number', validators=[DataRequired(), Regexp(r'^\d{10}$', message="Phone number must be 10 digits")])
    email = StringField('Email (Optional)')
    password = StringField('Password', validators=[DataRequired(), Regexp(r'^.{6,}$', message="Password must be at least 6 characters")])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    phone = StringField('Phone Number', validators=[DataRequired(), Regexp(r'^\d{10}$', message="Phone number must be 10 digits")])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class OrderForm(FlaskForm):
    brick_id = SelectField('Brick Type', coerce=int, validators=[DataRequired()])
    lots = IntegerField('Number of Lots', validators=[DataRequired(), NumberRange(min=1, message="Minimum 1 lot required")])
    payment_method = SelectField('Payment Method', choices=[('COD', 'Cash on Delivery'), ('PhonePe', 'PhonePe')], validators=[DataRequired()])
    submit = SubmitField('Place Order')

# Routes
@app.route('/')
def home():
    bricks = Brick.query.all()
    return render_template('index.html', bricks=bricks)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.pincode.data not in PRAKASAM_PINCODES:
            flash('Delivery is only available in Prakasam district.', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            address=form.address.data,
            pincode=form.pincode.data,
            phone=form.phone.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(phone=form.phone.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        flash('Invalid phone number or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/order', methods=['GET', 'POST'])
def order():
    if 'user_id' not in session:
        flash('Please log in to place an order.', 'danger')
        return redirect(url_for('login'))
    form = OrderForm()
    form.brick_id.choices = [(brick.id, brick.name) for brick in Brick.query.all()]
    if form.validate_on_submit():
        order = Order(
            user_id=session['user_id'],
            brick_id=form.brick_id.data,
            lots=form.lots.data,
            payment_method=form.payment_method.data
        )
        db.session.add(order)
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order_history'))
    return render_template('order.html', form=form)

@app.route('/order_history')
def order_history():
    if 'user_id' not in session:
        flash('Please log in to view order history.', 'danger')
        return redirect(url_for('login'))
    orders = Order.query.filter_by(user_id=session['user_id']).all()
    return render_template('order_history.html', orders=orders)

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Initialize Database with Sample Data
def init_db():
    db.create_all()
    if not Brick.query.first():
        bricks = [
            Brick(name="Red Clay Brick", image="/static/images/red_brick.jpg", ingredients="Clay, Sand, Water", quality="High Strength", price_per_lot=5000),
            Brick(name="Fly Ash Brick", image="/static/images/fly_ash_brick.jpg", ingredients="Fly Ash, Cement, Sand", quality="Eco-Friendly", price_per_lot=4500),
            Brick(name="Concrete Brick", image="/static/images/concrete_brick.jpg", ingredients="Cement, Aggregate, Water", quality="Durable", price_per_lot=6000)
        ]
        db.session.bulk_save_objects(bricks)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', debug=True)
