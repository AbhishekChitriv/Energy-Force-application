import numpy as np
import pickle
import os
import random
import string
import sys
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this' # Simple secret key for dev
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Helpers ---
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# --- Context Processor ---
@app.context_processor
def inject_user():
    return dict(user=current_user)

# --- Routes ---

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('register'))
            
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # OTP Logic
        otp = generate_otp()
        session['otp'] = otp
        session['pending_user_id'] = new_user.id
        
        # OTP Logic
        otp = generate_otp()
        session['otp'] = otp
        session['pending_user_id'] = new_user.id
        
        # MOCK SEND EMAIL
        print(f"\n{'='*30}\nOTP for {email}: {otp}\n{'='*30}\n", file=sys.stderr)
        flash(f'OTP sent to {email} (Check Terminal)', 'info')
        
        return redirect(url_for('verify_otp'))
        
    return render_template('register.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'pending_user_id' not in session:
        return redirect(url_for('register'))
        
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        generated_otp = session.get('otp')
        
        if user_otp == generated_otp:
            user = User.query.get(session['pending_user_id'])
            user.is_verified = True
            db.session.commit()
            
            login_user(user)
            session.pop('otp', None)
            session.pop('pending_user_id', None)
            return redirect(url_for('home'))
        else:
            flash('Invalid OTP', 'error')
            
    return render_template('otp.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Prediction Route (Unchanged Logic, added auth) ---
@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        # Load models if not loaded (or keep global)
        # For simplicity, assuming globals exist or reloading here
        # But we need to make sure imports are correct at top
        
        data = request.json
        
        building_type = float(data['building_type'])
        square_footage = float(data['square_footage'])
        number_of_occupants = float(data['number_of_occupants'])
        appliances_used = float(data['appliances_used'])
        average_temperature = float(data['average_temperature'])
        day_of_week = data['day_of_week']
        
        day_encoded = encoder.transform([day_of_week])[0]
        
        features = np.array([[
            building_type,
            square_footage,
            number_of_occupants,
            appliances_used,
            average_temperature,
            day_encoded
        ]])
        
        scaled_features = scaler.transform(features)
        prediction = model.predict(scaled_features)
        
        return jsonify({
            'prediction': float(prediction[0]),
            'status': 'success'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

# --- Init & Run ---
with app.app_context():
    db.create_all()

# Load models globally
try:
    with open('encoder.pkl', 'rb') as f:
        encoder = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
except Exception as e:
    print(f"Error loading model files: {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
