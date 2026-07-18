import cv2

# Tentukan indeks kamera yang mau dites.
# Mulai dari 0 (biasanya webcam laptop). Jika layarnya gelap atau salah kamera, ganti ke 1.
indeks_kamera = 0 

# Membuka koneksi ke kamera. Kita tambahkan cv2.CAP_DSHOW khusus untuk Windows 
# agar proses pembukaan kamera lebih cepat dan minim error.
cap = cv2.VideoCapture(indeks_kamera, cv2.CAP_DSHOW)

# Pengecekan apakah kamera berhasil diakses atau tidak
if not cap.isOpened():
    print(f"❌ Gagal membuka kamera pada indeks {indeks_kamera}.")
    print("Saran: Pastikan kamera tercolok dengan benar dan tidak sedang digunakan oleh aplikasi lain.")
    exit()

print(f"✅ Kamera {indeks_kamera} berhasil dibuka! Pastikan Anda mengklik jendela videonya, lalu tekan tombol 'q' di keyboard untuk keluar.")

while True:
    # Membaca gambar (frame) dari kamera secara terus-menerus
    ret, frame = cap.read()

    # Jika tiba-tiba gambar tidak terbaca (misal kabel tersenggol)
    if not ret:
        print("❌ Gagal mengambil gambar dari kamera. Menghentikan program...")
        break

    # Menampilkan gambar ke layar dalam jendela bernama "Test Kamera"
    cv2.imshow("Test Kamera", frame)

    # Sistem menunggu selama 1 milidetik. Jika tombol 'q' ditekan, hentikan loop.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Menutup kamera...")
        break

# Melepaskan akses kamera agar bisa digunakan oleh aplikasi lain
cap.release()
# Menutup jendela pop-up OpenCV
cv2.destroyAllWindows()