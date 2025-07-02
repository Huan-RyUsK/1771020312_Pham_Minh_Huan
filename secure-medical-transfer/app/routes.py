from flask import (
    render_template, redirect, url_for, request, flash,
    Blueprint, jsonify, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from . import db, bcrypt
from .models import User, MedicalRecord
from .crypto_logic import seal_package, unseal_package
from datetime import datetime

bp = Blueprint('main', __name__)

# --- AUTHENTICATION ROUTES ---

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'doctor')

        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại.', 'danger')
            return redirect(url_for('main.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password_hash=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('Tài khoản đã được tạo.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and bcrypt.check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user, remember=True)
            return redirect(request.args.get('next') or url_for('main.dashboard'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu.', 'danger')

    return render_template('login.html')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# --- DASHBOARD ---

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# --- GỬI HỒ SƠ Y TẾ ---

@bp.route('/send_record', methods=['POST'])
@login_required
def send_record():
    if current_user.role != 'doctor':
        return jsonify({"status": "error", "message": "Không có quyền."}), 403

    if 'medicalRecordFile' not in request.files or not request.form.get('patientId'):
        return jsonify({"status": "error", "message": "Vui lòng nhập đủ thông tin và chọn file."}), 400

    file = request.files['medicalRecordFile']
    patient_id = request.form.get('patientId')

    try:
        file_content = file.read()
        package = seal_package(file_content, file.filename, patient_id)

        new_record = MedicalRecord(
            patient_id=patient_id,
            file_name=file.filename,
            sent_by_user_id=current_user.id,
            encrypted_file_path=package['encrypted_file_path'],
            signature=package['signature_b64'],
            encrypted_session_key=package['encrypted_session_key_b64'],
            iv=package['iv_b64'],
            integrity_hash=package['integrity_hash_b64'],  # Bổ sung
            metadata_str=package['metadata_str'],
            status='PENDING_DECRYPTION'
        )
        db.session.add(new_record)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Hồ sơ của bệnh nhân {patient_id} đã được gửi thành công."
        })
    except Exception as e:
        current_app.logger.error(f"Lỗi khi niêm phong: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Lỗi hệ thống khi niêm phong hồ sơ."}), 500

# --- GIẢI MÃ HỒ SƠ ---

@bp.route('/api/decrypt_record/<int:record_id>', methods=['POST'])
@login_required
def decrypt_record(record_id):
    if current_user.role not in ['clerk', 'admin']:
        return jsonify({"status": "error", "message": "Không có quyền."}), 403

    password = request.json.get('password')
    if not password:
        return jsonify({"status": "error", "message": "Vui lòng nhập mật khẩu."}), 400

    record = MedicalRecord.query.get_or_404(record_id)
    if record.status != 'PENDING_DECRYPTION':
        return jsonify({"status": "error", "message": "Hồ sơ này đã được xử lý."}), 400

    try:
        decrypted_content = unseal_package(record, password)

        record.status = 'DECRYPTED'
        record.decrypted_at = datetime.utcnow()
        record.decrypted_by_user_id = current_user.id
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Giải mã thành công.",
            "fileName": record.file_name,
            "content": decrypted_content.decode('utf-8', errors='ignore')
        })

    except ValueError as e:
        record.status = 'DECRYPTION_FAILED'
        record.failure_reason = str(e)
        db.session.commit()
        return jsonify({"status": "error", "message": str(e)}), 401

    except Exception as e:
        record.status = 'DECRYPTION_FAILED'
        record.failure_reason = "Lỗi hệ thống không xác định."
        db.session.commit()
        current_app.logger.error(f"Lỗi hệ thống khi giải mã: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Lỗi hệ thống trong quá trình giải mã."}), 500

# --- API CUNG CẤP DỮ LIỆU CHO DATATABLE ---
@bp.route('/api/records')
@login_required
def get_records():
    """Cung cấp danh sách hồ sơ dưới dạng JSON cho DataTable."""
    # Bác sĩ chỉ thấy hồ sơ mình gửi
    if current_user.role == 'doctor':
        records = MedicalRecord.query.filter_by(
            sent_by_user_id=current_user.id
        ).order_by(MedicalRecord.created_at.desc()).all()
    else:
        # Nhân viên lưu trữ và admin thấy toàn bộ
        records = MedicalRecord.query.order_by(
            MedicalRecord.created_at.desc()
        ).all()

    # Trả về JSON có thêm trường 'failure_reason'
    data = [
        {
            "id": r.id,
            "patient_id": r.patient_id,
            "file_name": r.file_name,
            "sent_by": r.sender.username,
            "sent_at": r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "status": r.status,
            "failure_reason": r.failure_reason  # ✅ Thêm trường này để dùng tooltip
        } for r in records
    ]

    return jsonify({"data": data})
