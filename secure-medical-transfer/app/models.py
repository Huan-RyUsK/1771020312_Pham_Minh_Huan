from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='doctor')
    records_sent = db.relationship('MedicalRecord', foreign_keys='MedicalRecord.sent_by_user_id', backref='sender', lazy=True)

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(100), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Gửi bởi ai
    sent_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Mã hóa và chữ ký
    encrypted_file_path = db.Column(db.String(255), nullable=False, unique=True)
    signature = db.Column(db.Text, nullable=False)
    encrypted_session_key = db.Column(db.Text, nullable=False)
    iv = db.Column(db.Text, nullable=False)
    metadata_str = db.Column(db.Text, nullable=False)

    # Trạng thái và giải mã
    status = db.Column(db.String(50), nullable=False, default='PENDING_DECRYPTION')
    decrypted_at = db.Column(db.DateTime, nullable=True)
    decrypted_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    decrypted_by = db.relationship('User', foreign_keys=[decrypted_by_user_id])

    # --- Trường bổ sung ---
    integrity_hash = db.Column(db.Text, nullable=False)  # Hash toàn vẹn (IV + ciphertext)
    failure_reason = db.Column(db.Text, nullable=True)    # Lý do giải mã thất bại (nếu có)
