import flet as ft
import sqlite3
from datetime import datetime

def main(page: ft.Page):
    # --- Konfigurasi Tampilan Halaman ---
    page.title = "Dompetku Offline"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 16
    page.scroll = ft.ScrollMode.AUTO

    # --- 1. Inisialisasi Database SQLite Lokal ---
    conn = sqlite3.connect("uang_offline.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            jenis TEXT,
            kategori TEXT,
            nominal INTEGER,
            keterangan TEXT
        )
    """)
    conn.commit()

    # --- 2. Elemen UI Form Input ---
    txt_kategori = ft.TextField(label="Kategori", placeholder="Misal: Makan, Gaji", expand=True)
    txt_nominal = ft.TextField(label="Nominal (Rp)", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    txt_keterangan = ft.TextField(label="Keterangan (Opsional)", expand=True)
    dd_jenis = ft.Dropdown(
        label="Jenis",
        options=[
            ft.dropdown.Option("Pemasukan"),
            ft.dropdown.Option("Pengeluaran"),
        ],
        value="Pengeluaran",
        width=150
    )

    # Card Ringkasan Saldo
    lbl_saldo = ft.Text("Rp 0", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
    lbl_pemasukan = ft.Text("Rp 0", color=ft.Colors.GREEN_600, weight=ft.FontWeight.BOLD)
    lbl_pengeluaran = ft.Text("Rp 0", color=ft.Colors.RED_600, weight=ft.FontWeight.BOLD)

    list_transaksi = ft.Column(spacing=10)

    # --- 3. Fungsi Refresh & Hitung Ulang ---
    def muat_data():
        list_transaksi.controls.clear()
        
        cursor.execute("SELECT id, tanggal, jenis, kategori, nominal, keterangan FROM transaksi ORDER BY id DESC")
        rows = cursor.fetchall()

        total_in = 0
        total_out = 0

        for row in rows:
            t_id, tanggal, jenis, kategori, nominal, keterangan = row
            
            if jenis == "Pemasukan":
                total_in += nominal
                warna_nominal = ft.Colors.GREEN_600
                prefix = "+ "
            else:
                total_out += nominal
                warna_nominal = ft.Colors.RED_600
                prefix = "- "

            # Buat Item List Card
            card_item = ft.Card(
                content=ft.Container(
                    padding=12,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.BETWEEN,
                        controls=[
                            ft.Column([
                                ft.Text(f"{kategori}", weight=ft.FontWeight.BOLD, size=15),
                                ft.Text(f"{tanggal} • {keterangan}", size=12, color=ft.Colors.GREY_600),
                            ]),
                            ft.Text(
                                f"{prefix}Rp {nominal:,}".replace(",", "."),
                                color=warna_nominal,
                                weight=ft.FontWeight.BOLD,
                                size=15
                            )
                        ]
                    )
                )
            )
            list_transaksi.controls.append(card_item)

        # Update Teks Saldo
        saldo = total_in - total_out
        lbl_saldo.value = f"Rp {saldo:,}".replace(",", ".")
        lbl_pemasukan.value = f"Rp {total_in:,}".replace(",", ".")
        lbl_pengeluaran.value = f"Rp {total_out:,}".replace(",", ".")
        page.update()

    # --- 4. Fungsi Tambah Transaksi ---
    def tambah_transaksi(e):
        if not txt_nominal.value or not txt_kategori.value:
            page.snack_bar = ft.SnackBar(ft.Text("Harap isi Kategori dan Nominal!"))
            page.snack_bar.open = True
            page.update()
            return

        try:
            nominal = int(txt_nominal.value)
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Nominal harus berupa angka!"))
            page.snack_bar.open = True
            page.update()
            return

        tanggal_sekarang = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute(
            "INSERT INTO transaksi (tanggal, jenis, kategori, nominal, keterangan) VALUES (?, ?, ?, ?, ?)",
            (tanggal_sekarang, dd_jenis.value, txt_kategori.value, nominal, txt_keterangan.value)
        )
        conn.commit()

        # Reset Form
        txt_kategori.value = ""
        txt_nominal.value = ""
        txt_keterangan.value = ""
        
        page.snack_bar = ft.SnackBar(ft.Text("✅ Transaksi tersimpan offline!"))
        page.snack_bar.open = True
        
        muat_data()

    # --- 5. Tata Letak UI (Layout) ---
    page.add(
        # Header / Dashboard Saldo
        ft.Card(
            content=ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Text("Total Saldo Saya", size=12, color=ft.Colors.GREY_700),
                    lbl_saldo,
                    ft.Divider(),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        controls=[
                            ft.Column([ft.Text("Pemasukan", size=11), lbl_pemasukan]),
                            ft.Column([ft.Text("Pengeluaran", size=11), lbl_pengeluaran]),
                        ]
                    )
                ])
            )
        ),
        
        ft.Text("Tambah Transaksi Baru", size=16, weight=ft.FontWeight.BOLD),
        
        # Form Input
        ft.Row([dd_jenis, txt_kategori]),
        ft.Row([txt_nominal, txt_keterangan]),
        ft.ElevatedButton(
            "Simpan Transaksi",
            icon=ft.Icons.SAVE,
            on_click=tambah_transaksi,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            width=400
        ),
        
        ft.Divider(),
        ft.Text("Riwayat Transaksi", size=16, weight=ft.FontWeight.BOLD),
        list_transaksi
    )

    # Panggil muat_data saat aplikasi pertama kali terbuka
    muat_data()

# Jalankan Aplikasi
ft.app(target=main)