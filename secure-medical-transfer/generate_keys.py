from Crypto.PublicKey import RSA

print("Bắt đầu tạo các cặp khóa RSA 2048-bit...")

sender_key = RSA.generate(2048)
with open("sender_private_key.pem", "wb") as f:
    f.write(sender_key.export_key())
print("Đã tạo: sender_private_key.pem")

with open("sender_public_key.pem", "wb") as f:
    f.write(sender_key.publickey().export_key())
print("Đã tạo: sender_public_key.pem")

receiver_key = RSA.generate(2048)
with open("receiver_private_key.pem", "wb") as f:
    f.write(receiver_key.export_key())
print("Đã tạo: receiver_private_key.pem")

with open("receiver_public_key.pem", "wb") as f:
    f.write(receiver_key.publickey().export_key())
print("Đã tạo: receiver_public_key.pem")

print("\nHoàn tất! 4 file khóa đã được tạo.")