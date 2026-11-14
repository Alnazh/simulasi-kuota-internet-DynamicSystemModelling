"""Pengisian dan Pemakaian Kuota Internet
Mata kuliah Pemodelan dan Simulasi
Nama: Aulia Nazwa Huriah | NIM 301240010 | Kelas 4B

Persamaan: dK/dt = ci*ui - co*uo
"""
import matplotlib
matplotlib.use("Agg")
import os
os.makedirs("hasil", exist_ok=True)

# ===== Import library =====
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from gekko import GEKKO

# ===== Parameter dan sinyal input =====
ci = 0.02     # koefisien pengisian paket (GB/jam per %)
co = 0.01     # koefisien pemakaian data  (GB/jam per %)
K0 = 6.0      # kuota awal (GB)

jadwal = [
    (0,  6,   0,   0),
    (6,  8,   0,  10),
    (8,  12,  0,  40),
    (12, 13, 100, 10),
    (13, 17,  0,  30),
    (17, 19,  0,  10),
    (19, 20, 50,  80),
    (20, 22,  0,  80),
    (22, 24,  0,  20),
]

def input_fungsi(t):
    for mulai, selesai, ui_n, uo_n in jadwal:
        if mulai <= t < selesai:
            return ui_n, uo_n
    return jadwal[-1][2], jadwal[-1][3]

n  = 241
dt = 0.1
ts = np.linspace(0, 24, n)

ui = np.zeros(n)
uo = np.zeros(n)
ui[0], uo[0] = input_fungsi(0)
for i in range(1, n):
    ui[i], uo[i] = input_fungsi(ts[i] - dt/2)

print("Jumlah titik waktu:", n)
print("Nilai ui maksimum :", ui.max(), "%")
print("Nilai uo maksimum :", uo.max(), "%")

# ===== Perhitungan manual (tabel) =====
baris = []
K_awal = K0
for mulai, selesai, ui_n, uo_n in jadwal:
    durasi  = selesai - mulai
    masuk   = ci * ui_n * durasi      # GB
    keluar  = co * uo_n * durasi      # GB
    K_akhir = K_awal + masuk - keluar
    baris.append([f"{mulai:02d}.00 - {selesai:02d}.00", ui_n, uo_n, durasi,
                  round(masuk, 3), round(keluar, 3), round(masuk - keluar, 3),
                  round(K_awal, 3), round(K_akhir, 3)])
    K_awal = K_akhir

tabel = pd.DataFrame(baris, columns=[
    "Rentang Jam", "ui (%)", "uo (%)", "Durasi (jam)",
    "Masuk (GB)", "Keluar (GB)", "Perubahan (GB)", "K awal (GB)", "K akhir (GB)"])

print(tabel.to_string(index=False))
print("Total kuota masuk      :", round(tabel["Masuk (GB)"].sum(), 3), "GB")
print("Total pemakaian sehari :", round(tabel["Keluar (GB)"].sum(), 3), "GB")
print("Sisa kuota akhir hari  :", round(tabel["K akhir (GB)"].iloc[-1], 3), "GB")

# ===== Simulasi ODEINT =====
# model sistem dinamik: dK/dt = ci*ui - co*uo
def kuota(K, t, ci, co, valve1, valve2):
    dK_dt = ci * valve1 - co * valve2
    return dK_dt

Kn = K0
K_odeint = np.zeros(n)
K_odeint[0] = K0

for i in range(1, n):
    y = odeint(kuota, Kn, [ts[i-1], ts[i]], args=(ci, co, ui[i], uo[i]))
    Kn = y[-1][0]
    K_odeint[i] = Kn

print("Sisa kuota akhir (ODEINT):", round(K_odeint[-1], 3), "GB")

# ===== Simulasi GEKKO =====
m = GEKKO(remote=False)
m.time = ts

ui_g = m.Param(value=ui)     # sinyal inlet (pengisian paket)
uo_g = m.Param(value=uo)     # sinyal outlet (pemakaian data)
K_g  = m.Var(value=K0)       # variabel state: sisa kuota

m.Equation(K_g.dt() == ci * ui_g - co * uo_g)

m.options.IMODE = 4
m.solve(disp=False)

K_gekko = np.array(K_g.value).flatten()
print("Sisa kuota akhir (GEKKO) :", round(K_gekko[-1], 3), "GB")

# ===== Validasi hasil =====
jam_cek = [0, 6, 8, 12, 13, 17, 19, 20, 22, 24]
K_manual_cek = [K0] + [row[8] for row in baris]

hasil = []
for jam, km in zip(jam_cek, K_manual_cek):
    idx = int(round(jam / dt))
    hasil.append([jam, round(km, 3), round(K_odeint[idx], 3), round(K_gekko[idx], 3),
                  abs(km - K_odeint[idx]), abs(km - K_gekko[idx])])

validasi = pd.DataFrame(hasil, columns=[
    "Jam", "Manual (GB)", "ODEINT (GB)", "GEKKO (GB)", "Selisih Manual-ODEINT", "Selisih Manual-GEKKO"])
print(validasi.to_string(index=False))
print("Selisih maksimum Manual-ODEINT:", validasi["Selisih Manual-ODEINT"].max())
print("Selisih maksimum Manual-GEKKO :", validasi["Selisih Manual-GEKKO"].max())

# ===== Grafik 1: sisa kuota dan sinyal input =====
plt.figure(figsize=(9, 6))

plt.subplot(2, 1, 1)
plt.plot(ts, K_odeint, 'b-', linewidth=2)
plt.ylabel(r'Sisa Kuota $K(t)$, (GB)')
plt.title('Simulasi Sisa Kuota Internet Mahasiswa dalam Satu Hari')
plt.xticks(range(0, 25, 2))
plt.grid(True, alpha=0.3)

plt.subplot(2, 1, 2)
plt.plot(ts, ui, 'r--', linewidth=2, label=r'$u_i$ (pengisian)')
plt.plot(ts, uo, 'g--', linewidth=2, label=r'$u_o$ (pemakaian)')
plt.ylabel(r'Kontrol $u(t)$, (%)')
plt.xlabel(r'$t$, (jam)')
plt.xticks(range(0, 25, 2))
plt.ylim(0, 110)
plt.legend(frameon=False)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("hasil/grafik1.png", dpi=150, bbox_inches="tight")
plt.close()

# ===== Grafik 2: perbandingan ODEINT dan GEKKO =====
plt.figure(figsize=(9, 4.5))
plt.plot(ts, K_odeint, 'b-', linewidth=3, label='ODEINT')
plt.plot(ts, K_gekko, 'r--', linewidth=2, label='GEKKO')
plt.xlabel(r'$t$, (jam)')
plt.ylabel(r'Sisa Kuota $K(t)$, (GB)')
plt.title('Perbandingan Hasil ODEINT dan GEKKO')
plt.xticks(range(0, 25, 2))
plt.grid(True, alpha=0.3)
plt.legend(frameon=False)
plt.savefig("hasil/grafik2.png", dpi=150, bbox_inches="tight")
plt.close()

# ===== Grafik 3: pengaruh koefisien pemakaian =====
def simulasi(co_nilai):
    Kx = np.zeros(n)
    Kx[0] = K0
    Kn = K0
    for i in range(1, n):
        y = odeint(kuota, Kn, [ts[i-1], ts[i]], args=(ci, co_nilai, ui[i], uo[i]))
        Kn = y[-1][0]
        Kx[i] = Kn
    return Kx

K1 = simulasi(0.008)
K2 = simulasi(0.010)
K3 = simulasi(0.012)

plt.figure(figsize=(9, 4.5))
plt.plot(ts, K1, 'g-',  linewidth=2, label=r'$c_o=0.008$ (hemat)')
plt.plot(ts, K2, 'b--', linewidth=2, label=r'$c_o=0.010$ (normal)')
plt.plot(ts, K3, 'r:',  linewidth=2.5, label=r'$c_o=0.012$ (boros)')
plt.xlabel(r'$t$, (jam)')
plt.ylabel(r'Sisa Kuota $K(t)$, (GB)')
plt.title('Pengaruh Koefisien Pemakaian terhadap Sisa Kuota')
plt.xticks(range(0, 25, 2))
plt.grid(True, alpha=0.3)
plt.legend(frameon=False)
plt.savefig("hasil/grafik3.png", dpi=150, bbox_inches="tight")
plt.close()

print("Sisa kuota akhir hari:")
print("co = 0.008 :", round(K1[-1], 3), "GB")
print("co = 0.010 :", round(K2[-1], 3), "GB")
print("co = 0.012 :", round(K3[-1], 3), "GB")
print("Sisa kuota minimum (co = 0.012):", round(K3.min(), 3), "GB")
