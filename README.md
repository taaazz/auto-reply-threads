# AI agent auto reply threads!

Profil [Hermes Agent](https://hermes-agent.nousresearch.com/docs) untuk otomasi
engagement Threads: penemuan lead di niche HKI/merek/paten, penyaringan
relevansi, dan pengiriman balasan otomatis dengan persona Gen Z yang ringkas dan
tidak berorientasi jualan.

Repositori ini adalah *distribution* profil — dapat dipasang di mesin lain
melalui `hermes profile install`. Cakupan sengaja dibatasi pada dua kebutuhan
produksi: **scraping Threads** dan **auto-reply**.

- Versi: `0.3.0`
- Kebutuhan minimum: Hermes Agent `>= 0.12.0`, Python `3.10+`
- Lisensi: MIT

## Daftar Isi

1. [Instalasi](#1-instalasi)
2. [Konfigurasi](#2-konfigurasi)
3. [Penggunaan](#3-penggunaan)
4. [Penyiapan Playwright](#4-penyiapan-playwright)
5. [Alur Penggunaan Playwright](#5-alur-penggunaan-playwright)
6. [Arsitektur](#6-arsitektur)
7. [Cakupan Skill](#7-cakupan-skill)
8. [Dokumentasi](#8-dokumentasi)
9. [Catatan Operasional](#9-catatan-operasional)
10. [Batasan dan Risiko](#10-batasan-dan-risiko)
11. [Keamanan](#11-keamanan)
12. [Pembaruan](#12-pembaruan)

## 1. Instalasi

```bash
hermes profile install github.com/taaazz/auto-reply-threads --alias -y
```

Sematkan ref tertentu (tag, branch, atau SHA):

```bash
hermes profile install github.com/taaazz/auto-reply-threads#main
```

Yang terpasang hanya path yang tercantum di `distribution_owned`:
`SOUL.md`, `soul.md`, `config.yaml`, dan lima skill Threads. Direktori
`memories/` **tidak** terpasang — Hermes memperlakukannya sebagai milik pengguna
dan tidak pernah menimpanya; di repositori ini `memories/` hanya disimpan
sebagai mirror yang dapat dibaca.

Playwright **tidak** ikut terpasang oleh perintah di atas; penyiapan runtime
browser dilakukan terpisah pada bagian [§4](#4-penyiapan-playwright).

## 2. Konfigurasi

Distribusi ini **tidak memerlukan variabel lingkungan apa pun**. Alur kerja hanya
butuh dua hal:

1. **Sesi Threads** — berkas `storage_state.json`, dibuat dengan mengekspor sesi
   login browser (lihat [§4.2](#42-ekspor-sesi-login-di-laptop)).
   Simpan di luar repositori; berkas ini sudah tercakup `.gitignore`.
2. **Model LLM** — spesifik per mesin, jadi tidak ikut di-ship. Konfigurasikan
   sekali di mesin tujuan:

```bash
hermes -p promo-in setup
hermes -p promo-in config set model.default <model-id>
hermes -p promo-in config set model.provider <provider>
```

Untuk endpoint OpenAI-compatible, tambahkan custom provider yang merujuk nama
variabel lingkungan, bukan key literal:

```yaml
custom_providers:
  - name: my-provider
    base_url: https://api.example.com/v1
    key_env: MY_PROVIDER_API_KEY
    model: <model-id>
```

`config.yaml` bawaan sengaja hanya berisi komentar dan `_config_version`. Tidak
ada kredensial literal di dalamnya; bila perlu menyimpan secret, gunakan
`~/.hermes/profiles/promo-in/.env` yang tidak pernah di-commit.

### Penyesuaian identitas brand

Repositori ini tidak memuat nama merek, domain, maupun handle resmi apa pun.
Semua rujukan memakai placeholder berikut — ganti sesuai kebutuhan sebelum
menjalankan agen:

| Placeholder | Ganti dengan |
|---|---|
| `example.com` | domain resmi Anda |
| `@yourbrand` | handle Threads resmi Anda |

Nilai tersebut dipakai di `SOUL.md`, `soul.md`, dan berkas `SKILL.md` pada
`skills/social-media/`. Persona di `soul.md` juga masih generik dan dapat
disesuaikan.

## 3. Penggunaan

Setelah `storage_state.json` tersedia, jalankan agen dan skill Threads akan
dipilih otomatis berdasarkan konteks tugas:

```bash
hermes -p promo-in chat
```

Alur kerja tipikal:

1. **Discovery** — pencarian postingan berdasarkan kata kunci berintensi tinggi
   (`HAKI`, `daftar merek`, `paten`, `merek ditolak`, dan sejenisnya).
2. **Filtering** — penolakan akun jasa, penjual, agensi, dan kompetitor untuk
   menjaga relevansi.
3. **Composition** — penyusunan balasan sesuai persona brand beserta tautan
   `example.com` dan mention `@yourbrand`.
4. **Delivery** — pengiriman balasan melalui Playwright dengan jeda yang wajar.

Contoh skrip pengiriman balasan tunggal:

```python
import asyncio
from playwright.async_api import async_playwright

REPLY = "Proses pendaftaran merek dapat dilakukan sepenuhnya online melalui example.com — pengecekan tersedia sebelum pengajuan untuk meminimalkan risiko penolakan."

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(storage_state="storage_state.json")
        page = await context.new_page()

        await page.goto("https://www.threads.net/@username/post/POST_ID", wait_until="networkidle")
        await page.wait_for_timeout(4000)

        box = page.locator("div[role='textbox']").first
        await box.click()
        await box.fill(REPLY)
        await box.press("Enter")

        await browser.close()

asyncio.run(main())
```

Versi lengkap dengan stealth context, verifikasi hasil kirim, dan prosedur
debug ada di [§5](#5-alur-penggunaan-playwright).

## 4. Penyiapan Playwright

Tiga tahap, dijalankan sekali: pasang di VPS (4.1), ekspor sesi di laptop (4.2),
kirim berkas sesi ke VPS (4.3).

### 4.1 Pasang Playwright di VPS

```bash
apt install -y python3 python3-venv python3-pip        # lewati bila sudah ada
python3 -m venv /root/threads-venv
/root/threads-venv/bin/pip install playwright
/root/threads-venv/bin/playwright install chromium
```

Terverifikasi: Python 3.12.3, Playwright `1.63.0`, Chromium `1243` di
`~/.cache/ms-playwright`. Bila launch gagal dengan
`error while loading shared libraries`:

```bash
/root/threads-venv/bin/playwright install-deps chromium
```

Selanjutnya seluruh skrip di VPS dijalankan dengan `/root/threads-venv/bin/python`.

### 4.2 Ekspor sesi login di laptop

```python
# save_state_local.py — jalankan di laptop
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.threads.net")
    input("Login manual di browser, lalu tekan Enter setelah feed Threads terlihat...")
    with open("storage_state.json", "w") as f:
        json.dump(context.storage_state(), f)
    browser.close()
```

```bash
python save_state_local.py
```

Tahap ini tidak bisa dijalankan di VPS: `headless=False` butuh X server dan gagal
dengan `TargetClosedError` / `Missing X server or $DISPLAY`.

### 4.3 Kirim sesi ke VPS

```bash
scp storage_state.json root@VPS:/root/storage_state.json
```

Sesi mati bila logout, ganti password, atau diputus Meta — bila muncul halaman
`Continue with Instagram`, ulangi 4.2 lalu 4.3.

## 5. Alur Penggunaan Playwright

Dengan venv dari [§4.1](#41-pasang-playwright-di-vps) dan sesi dari
[§4.3](#43-kirim-sesi-ke-vps), agen siap dipakai:

```bash
hermes -p promo-in chat
```

Skrip balasan memuat sesi dari berkas `storage_state.json`:

```python
browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
context = await browser.new_context(storage_state="/root/storage_state.json")
page = await context.new_page()
```

### Membalas satu postingan

1. Buka permalink postingan lalu tunggu render:

```python
await page.goto("https://www.threads.net/@{username}/post/{post_id}", wait_until="networkidle")
await page.wait_for_timeout(4000)
```

2. Pastikan tidak ada ajakan `Continue with Instagram`. Bila ada, sesi mati —
   ulangi [§4.2](#42-ekspor-sesi-login-di-laptop) dan [§4.3](#43-kirim-sesi-ke-vps).
3. Isi kolom balasan dan kirim:

```python
box = page.locator("div[role='textbox']").first
await box.click()
await box.fill(REPLY)
await box.press("Enter")
await page.wait_for_timeout(5000)
```

4. Simpan bukti kirim:

```python
await page.screenshot(path="/root/reply_success.png")
```

5. Jeda 10–30 detik antar balasan dan variasikan kalimatnya.

Isi balasan: 1–3 kalimat berisi fakta produk, tanpa ajakan DM dan tanpa tawaran
konsultasi; arahkan ke `example.com` atau sebut `@yourbrand`.

Bila login wall tetap muncul padahal `storage_state.json` masih ada, tambahkan
tiga penyetelan stealth sebelum `new_page()` — User-Agent desktop, `viewport`
1280x800, dan `navigator.webdriver = undefined`; polanya ada di
`skills/social-media/threads-automation/references/session-and-auth.md`.

### Kalau bermasalah

| Gejala | Tindakan |
|---|---|
| `Looks like you launched a headed browser without having a XServer running` | jangan pakai `headless=False` di VPS; ekspor sesi di laptop |
| `Executable doesn't exist at .../ms-playwright/chromium-...` | `playwright install chromium` belum dijalankan |
| `error while loading shared libraries` | `playwright install-deps chromium` sebagai root |
| `Timeout ... waiting for div[role='textbox']` | sesi kedaluwarsa (cek penanda `Continue with Instagram`) atau selector berubah |
| `Strict mode violation` pada `fill()` | lebih dari satu elemen cocok — pakai `.first` atau filter `aria-placeholder` |
| `TargetClosedError: Target page, context or browser has been closed` | browser kehabisan memori, atau launch headed tanpa display |

Bila selector perlu diperiksa ulang:

```python
await page.screenshot(path="/root/debug.png", full_page=True)   # kondisi halaman saat gagal
await page.locator("div[role='textbox']").count()                # jumlah elemen yang cocok
```

Selector terverifikasi ada di
`skills/social-media/threads-automation/references/playwright_selectors.md`.

## 6. Arsitektur

Sistem dibangun di atas **Playwright** dengan pendekatan browser automation, bukan
API resmi Meta.

**Persistensi sesi.** Skrip tidak melakukan login otomatis karena proses tersebut
rentan terhadap CAPTCHA dan verifikasi dua faktor. Sesi diambil dari browser yang
sudah terverifikasi manusia, lalu diekspor menjadi `storage_state.json`.

**Evasi deteksi otomatis.** Tiga penyesuaian diterapkan pada konteks Chromium:

- menghapus flag `navigator.webdriver` melalui `add_init_script`;
- menggunakan User-Agent browser desktop komersial standar;
- menonaktifkan flag otomatisasi melalui `--disable-blink-features=AutomationControlled`.

**Interaksi DOM.** Skrip membuka URL target, menunggu `networkidle`, mengisi
`div[role='textbox']` dengan draf balasan, lalu mengirim melalui tombol Post atau
tombol Enter.

## 7. Cakupan Skill

| Skill | Fungsi | Berkas pendukung |
|---|---|---|
| `threads-automation` | Alur kerja scraping dan engagement end-to-end | `references/keyword-guide.md`, `references/playwright_selectors.md`, `references/session-and-auth.md`, `references/json-pathing.md` |
| `threads-lead-generation` | Ekstraksi lead berintensi tinggi | `references/threads-lead-keywords.yml`, `templates/threads-lead-template.md`, `scripts/threads-scrape-verify.js` |
| `threads-lead-engagement` | Riset dan pembalasan lead | — |
| `threads-engagement-automation` | Orkestrasi discovery dan reply | — |
| `threads-reply-agent` | Auto-reply khusus postingan merek/HKI | — |

Struktur repositori:

```
.
├── distribution.yaml          manifest profil (versi, allowlist)
├── config.yaml                konfigurasi Hermes — minimal, tanpa kredensial
├── SOUL.md, soul.md           persona dan identitas agen
├── README.md                  dokumen ini
├── .gitignore                 daftar berkas yang tidak pernah di-commit
├── memories/                  mirror memori pengguna (tidak ikut terpasang)
└── skills/social-media/       lima skill Threads
```

## 8. Dokumentasi

ai agent berhasil reply di akun orang lain

<img width="340" height="400" alt="image" src="https://github.com/user-attachments/assets/96a56333-5f4d-43e4-bd47-9e2a7b23c568" />

## 9. Catatan Operasional

Tahap *write* (komentar, like, posting) sebaiknya dijalankan dari jaringan
residential, bukan dari VPS cloud. Alamat IP datacenter terdaftar pada basis data
Meta dan aktivitas penulisan darinya jauh lebih sering memicu pembatasan. Tahap
scraping dapat dijalankan di VPS; tahap pengiriman balasan sebaiknya dijalankan
dari jaringan lokal atau melalui residential proxy.

## 10. Batasan dan Risiko

1. **Risiko pemblokiran akun.** Tanpa jeda yang menyerupai perilaku manusia,
   akun berpotensi mengalami checkpoint, pembatasan fitur, atau pemblokiran permanen.
2. **Kerapuhan terhadap perubahan UI.** Perubahan struktur HTML atau React pada
   antarmuka Threads dapat mematahkan selector Playwright dan memerlukan
   penyesuaian berkala.
3. **Konsumsi sumber daya.** Instance Chromium memerlukan memori dan CPU jauh
   lebih besar dibanding pemanggilan HTTP biasa.
4. **Ketergantungan pada sesi manusia.** Cookie pada `storage_state.json` dapat
   kedaluwarsa tanpa peringatan sehingga memerlukan login manual ulang.
5. **Throughput rendah secara desain.** Kombinasi IP lokal dan jeda manusiawi
   membatasi volume balasan per satuan waktu; hal ini merupakan konsekuensi
   langsung dari menjaga keamanan akun.

Automasi browser tidak sejalan dengan Terms of Service Meta. Penggunaan
sepenuhnya menjadi tanggung jawab pengguna.

## 11. Keamanan

Berkas berikut tidak pernah di-commit dan telah dicakup `.gitignore`:
`.env`, `auth.json`, `state.db*`, `sessions/`, `logs/`, `cache/`, `bin/`,
`skills/.hub/`, `storage_state*.json`, `threads_auth*.json`, `cookies*.json`,
`*.pem`, `*.key`, serta setiap berkas yang memuat `token` atau `secret` pada
namanya.

Sebelum setiap commit, verifikasi daftar staged:

```bash
git add -A
git diff --cached --name-only | grep -E '\.env$|auth\.json|state\.db|storage_state|cookie|token|secret'
```

Perintah tersebut harus tidak menghasilkan output. Catatan: aturan pengecualian
pada `.gitignore` (mis. `!.env.template`) harus diletakkan di baris terakhir
karena Git menerapkan aturan pencocokan terakhir yang menang — pola seperti
`*.env.*` akan meniadakan pengecualian yang ditulis sebelumnya.

## 12. Pembaruan

```bash
hermes profile update promo-in
hermes profile info promo-in
```

`update` hanya menimpa path yang tercantum pada `distribution_owned`. Untuk
penyesuaian khusus mesin, gunakan direktori `local/` — direktori tersebut
milik pengguna dan tidak akan ditimpa. Runtime Playwright di luar profil
(venv dan binary browser) tidak tersentuh oleh `update`; ikuti [§4](#4-penyiapan-playwright)
saat memindahkan runner ke mesin baru.
