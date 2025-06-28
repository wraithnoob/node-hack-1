from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to pet
    pet = db.relationship('Pet', backref='owner', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Basic pet info (Blobby the Moody Blob)
    current_mood = db.Column(db.String(20), default='normal')
    message = db.Column(db.String(200), default="How are you feeling today?")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Daily bonds system (streak counter)
    daily_bonds = db.Column(db.Integer, default=0)
    last_visit_date = db.Column(db.Date, default=datetime.utcnow().date)
    bond_display_name = db.Column(db.String(50), default="Daily Bonds")
    
    # Timer system (for 6-minute mood changes)
    last_logout_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def update_daily_bonds(self):
        """Update daily bonds when user logs in"""
        today = datetime.utcnow().date()
        
        # If already visited today, don't update
        if self.last_visit_date == today:
            return
        
        # Check if consecutive day
        yesterday = today - timedelta(days=1)
        if self.last_visit_date == yesterday:
            # Consecutive day - increment bonds
            self.daily_bonds += 1
        else:
            # Missed days - reset bonds and change display name
            self.daily_bonds = 1
            bond_names = [
                "Daily Bonds", "Care Days", "Visit Counter", "Friendship Days",
                "Pet Connection", "Together Time", "Love Days", "Bonding Chain"
            ]
            self.bond_display_name = random.choice(bond_names)
        
        # Update last visit date
        self.last_visit_date = today
        db.session.commit()
    
    def get_minutes_offline(self):
        """Calculate how many minutes user was offline"""
        if not self.last_logout_time or not self.last_login_time:
            return 0
        
        # Minutes between logout and login
        offline_seconds = (self.last_login_time - self.last_logout_time).total_seconds()
        return max(0, offline_seconds / 60)
    
    def get_minutes_online(self):
        """Calculate how many minutes user has been online since login"""
        if not self.last_login_time:
            return 0
        
        # Minutes since login
        online_seconds = (datetime.utcnow() - self.last_login_time).total_seconds()
        return online_seconds / 60
    
    def get_timer_info(self):
        """Get timer information for display"""
        offline_mins = self.get_minutes_offline()
        online_mins = self.get_minutes_online()
        
        return {
            'offline_minutes': round(offline_mins, 1),
            'online_minutes': round(online_mins, 1),
            'total_deterioration': round(offline_mins, 1),
            'recovery_progress': round(online_mins, 1)
        }
