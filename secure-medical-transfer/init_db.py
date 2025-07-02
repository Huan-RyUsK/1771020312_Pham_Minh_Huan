from app import create_app, db, bcrypt
from app.models import User

app = create_app()

with app.app_context():
    print("--- Bắt đầu khởi tạo cơ sở dữ liệu ---")
    print("Xóa các bảng cũ (nếu có)...")
    db.drop_all()
    print("Tạo các bảng mới theo model đã cập nhật...")
    db.create_all()
    print("Tạo các người dùng mặc định...")

    admin_pass = bcrypt.generate_password_hash('admin123').decode('utf-8')
    admin = User(username='admin', password_hash=admin_pass, role='admin')
    db.session.add(admin)

    doctor_pass = bcrypt.generate_password_hash('doctor123').decode('utf-8')
    doctor = User(username='doctor', password_hash=doctor_pass, role='doctor')
    db.session.add(doctor)

    clerk_pass = bcrypt.generate_password_hash('clerk123').decode('utf-8')
    clerk = User(username='clerk', password_hash=clerk_pass, role='clerk')
    db.session.add(clerk)

    db.session.commit()
    print(">>> Hoàn tất! Cơ sở dữ liệu đã được khởi tạo.")
    print("\n--- Thông tin đăng nhập ---")
    print("1. Admin:   admin / admin123")
    print("2. Bác sĩ:  doctor / doctor123")
    print("3. Nhân viên: clerk / clerk123")
    print("4. Nhập mật khẩu: 123123")