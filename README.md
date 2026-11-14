# Pengisian dan Pemakaian Kuota Internet

Tugas Pemodelan dan Simulasi (Pertemuan 6: Dinamic System Modeling)

- Nama: Aulia Nazwa Huriah
- NIM: 301240010
- Kelas: 5B Teknik Informatika, Universitas Bale Bandung

## Deskripsi

Simulasi sistem dinamik sisa kuota internet seorang mahasiswa selama 24 jam.
Inlet adalah pengisian paket data (u_i) dan outlet adalah pemakaian data (u_o).

Persamaan: `dK/dt = ci * ui - co * uo`

Parameter: K(0) = 6 GB, ci = 0,02 dan co = 0,01 (GB/jam per 1%).
Persamaan diselesaikan dengan ODEINT (SciPy) dan GEKKO, lalu divalidasi dengan perhitungan manual.

## Isi

| Berkas | Keterangan |
|---|---|
| `kuota_internet.py` | Program Python lengkap |
| `notebook_kuota_internet.ipynb` | Versi Google Colab |
| `requirements.txt` | Daftar library |
| `hasil/` | Grafik hasil simulasi |

## Cara menjalankan

```bash
pip install -r requirements.txt
python kuota_internet.py
```

Grafik tersimpan di folder `hasil/`. Untuk Google Colab, buka `notebook_kuota_internet.ipynb` lalu jalankan semua sel.

## Hasil

Sisa kuota akhir hari 2,9 GB (masuk 3 GB, terpakai 6,1 GB). Hasil manual, ODEINT, dan GEKKO sama.
