from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class RawMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False, default='kg')
    material_type = db.Column(db.String(100), nullable=False, default='other')
    minimum_stock = db.Column(db.Float, nullable=False, default=10.0)
    supplier = db.Column(db.String(100), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def status(self):
        if self.quantity <= 0:
            return 'out_of_stock'
        elif self.quantity <= self.minimum_stock:
            return 'low_stock'
        else:
            return 'available'

class Production(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_number = db.Column(db.String(50), unique=True, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_type = db.Column(db.String(50), nullable=False)
    peels_used = db.Column(db.Float, nullable=False)
    quantity_produced = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='planned')
    progress = db.Column(db.Integer, nullable=False, default=0)
    supervisor = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True, unique=True)
    profile_pic = db.Column(db.String(200), nullable=True, default='default.png')
    date_joined = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"