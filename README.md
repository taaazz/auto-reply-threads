# AI agent auto reply threads!

Profil [Hermes Agent](https://hermes-agent.nousresearch.com/docs) untuk otomasi
engagement Threads: penemuan lead di niche HKI/merek/paten, penyaringan
relevansi, dan pengiriman balasan otomatis dengan persona Gen Z yang ringkas dan
tidak berorientasi jualan.

Repositori ini adalah *distribution* profil — dipasang di mesin lain melalui
`hermes profile install`.

- Versi: `0.3.0`
- Kebutuhan minimum: Hermes Agent `>= 0.12.0`, Python `3.10+`
- Lisensi: MIT

ai agent berhasil reply di akun orang lain

<img width="340" height="400" alt="image" src="https://github.com/user-attachments/assets/96a56333-5f4d-43e4-bd47-9e2a7b23c568" />

## Daftar Isi

1. [Ringkasan](#1-ringkasan)
2. [Instalasi](#2-instalasi)
3. [Penyiapan Playwright](#3-penyiapan-playwright)
4. [Konfigurasi](#4-konfigurasi)
5. [Menjalankan Agen](#5-menjalankan-agen)
6. [Batasan dan Catatan Operasional](#6-batasan-dan-catatan-operasional)
7. [Keamanan](#7-keamanan)
8. [Referensi](#8-referensi)

## 1. Ringkasan

Dua kebutuhan produksi: **scraping Threads** dan **auto-reply**. Keduanya
berjalan lewat browser automation dengan Playwright, bukan API resmi Meta.

Alur kerja, empat tahap:

1. **Discovery** — cari postingan dengan kata kunci berintensi tinggi (`HAKI`,
   `daftar merek`, `paten`, `merek ditolak`).
2. **Filtering** — buang akun jasa, penjual, agensi, dan kompetitor; sisakan
   postingan yang benar-benar mencari bantuan.
3. **Composition** — susun balasan sesuai persona, dengan rujukan `example.com`
   dan mention `@yourbrand`.
4. **Delivery** — kirim balasan lewat Playwright dengan jeda yang wajar.

Sebelum dipakai, runtime Playwright dan sesi login harus disiapkan lebih dulu —
lihat [§3](#3-penyiapan-playwright).

## 2. Instalasi

```bash
hermes profile install github.com/taaazz/auto-reply-threads --alias -y
```

Sematkan ref tertentu (tag, branch, atau SHA):

```bash
hermes profile install github.com/taaazz/auto-reply-threads#main
```

Yang terpasang hanya path yang tercantum pada `distribution_owned`: `SOUL.md`,
`soul.md`, `config.yaml`, dan lima skill Threads. Direktori `memories/` **tidak**
terpasang — Hermes memperlakukannya sebagai milik pengguna dan tidak pernah
menimpanya; di repositori ini `memories/` hanya disimpan sebagai mirror yang
dapat dibaca.

### 2.1 Memperbarui

```bash
hermes profile update promo-in
hermes profile info promo-in
```

`update` hanya menimpa path pada `distribution_owned`. Penyesuaian khusus mesin
diletakkan di direktori `local/` — direktori itu milik pengguna dan tidak pernah
ditimpa. Runtime Playwright di luar profil (venv dan binary browser) juga tidak
tersentuh `update`; saat pindah ke mesin baru, ulangi
[§3](#3-penyiapan-playwright).

## 3. Penyiapan Playwright

Dijalankan sekali saja. Setiap langkah ditandai **di mana** dijalankan dan apa
**tanda berhasil**-nya. Nomor versi di bawah adalah hasil verifikasi di mesin ini.

### 3.1 Di VPS: pasang Playwright

| # | Perintah | Fungsi | Tanda berhasil |
|---|---|---|---|
| 1 | `python3 -V` | pastikan Python tersedia | `Python 3.12.3` |
| 2 | `apt update && apt install -y python3 python3-venv python3-pip` | hanya bila Python/pip belum ada | `dpkg -l` menampilkan `ii python3-venv` |
| 3 | `python3 -m venv /root/threads-venv` | buat virtualenv terpisah | `/root/threads-venv/bin/pip` ada |
| 4 | `/root/threads-venv/bin/pip install playwright` | pasang paket Playwright ke venv | `Successfully installed playwright-1.63.0` |
| 5 | `/root/threads-venv/bin/playwright install chromium` | unduh Chromium (±114 MiB) | `Chromium 1243 downloaded to .../ms-playwright/chromium-1243` |
| 6 | `/root/threads-venv/bin/playwright --version` | verifikasi instalasi | `Version 1.63.0` |

Langkah 3 tidak boleh dilewati. `pip install playwright` tanpa venv langsung gagal
dengan `error: externally-managed-environment` (PEP 668).

Bila launch gagal dengan `error while loading shared libraries: libgbm.so.1` atau
`libnss3`:

```bash
/root/threads-venv/bin/playwright install-deps chromium
```

Seluruh skrip di VPS dijalankan dengan `/root/threads-venv/bin/python`, bukan
`python3`. `python3` sistem tidak memuat paket Playwright dan berakhir dengan
`ModuleNotFoundError: No module named 'playwright'`.

### 3.2 Di laptop: ekspor sesi login

| # | Perintah | Fungsi | Tanda berhasil |
|---|---|---|---|
| 1 | `python -m pip install playwright` | pasang paket Playwright | `Successfully installed playwright-...` |
| 2 | `python -m playwright install chromium` | unduh Chromium | `Chromium 1243 downloaded ...` |
| 3 | `python save_state_local.py` | login manual, lalu simpan sesi | `storage_state.json` muncul di folder kerja |
| 4 | buka `storage_state.json` | pastikan sesi tersimpan | isinya memuat `"cookies"` dan `"sessionid"` |

Isi `save_state_local.py`:

```python
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

Alurnya: jendela Chromium terbuka ke threads.net -> login manual (selesaikan 2FA
bila ada) -> kembali ke terminal dan tekan Enter -> berkas tersimpan. Bila isinya
tidak memuat `"sessionid"`, login belum berhasil — ulangi langkah 3.

Tahap ini tidak bisa dijalankan di VPS: `headless=False` butuh X server dan gagal
dengan `TargetClosedError` / `Missing X server or $DISPLAY`.

### 3.3 Kirim sesi ke VPS

| # | Perintah | Dijalankan di | Tanda berhasil |
|---|---|---|---|
| 1 | `scp storage_state.json root@<IP_VPS>:/root/storage_state.json` | laptop | tanpa galat, ditanya password VPS |
| 2 | `ls -l /root/storage_state.json` | VPS | berkas ada, ukuran ±11 KB |

Sesi mati bila logout, ganti password, atau diputus Meta. Bila muncul halaman
`Continue with Instagram`, ulangi 3.2 lalu 3.3.

### 3.4 Salin-tempel sekali jalan

```bash
# 1. VPS baru, dari nol
ssh root@<IP_VPS>
apt update && apt install -y python3 python3-venv python3-pip
python3 -m venv /root/threads-venv
/root/threads-venv/bin/pip install playwright
/root/threads-venv/bin/playwright install chromium
/root/threads-venv/bin/playwright --version        # harus: Version 1.63.0
```

```bash
# 2. Laptop: ekspor sesi
python -m pip install playwright && python -m playwright install chromium
python save_state_local.py                         # login manual, lalu tekan Enter
scp storage_state.json root@<IP_VPS>:/root/storage_state.json
```

```bash
# 3. VPS: jalankan
ls -l /root/storage_state.json                     # ±11 KB
/root/threads-venv/bin/python /root/auto_reply_test.py
```

## 4. Konfigurasi

Distribusi ini tidak memerlukan variabel lingkungan apa pun. Yang perlu
disesuaikan hanya dua hal.

**Model LLM** — spesifik per mesin, jadi tidak ikut di-ship:

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

`config.yaml` bawaan hanya berisi komentar dan `_config_version` — tidak ada
kredensial literal. Bila perlu menyimpan secret, gunakan
`~/.hermes/profiles/promo-in/.env` yang tidak pernah di-commit.

**Identitas brand** — repositori ini tidak memuat nama merek, domain, maupun
handle resmi apa pun. Semua rujukan memakai placeholder berikut; ganti sebelum
menjalankan agen:

| Placeholder | Ganti dengan |
|---|---|
| `example.com` | domain resmi Anda |
| `@yourbrand` | handle Threads resmi Anda |

Nilai tersebut dipakai di `SOUL.md`, `soul.md`, dan berkas `SKILL.md` pada
`skills/social-media/`. Persona di `soul.md` masih generik dan dapat disesuaikan.

## 5. Menjalankan Agen

```bash
hermes -p promo-in chat
```

Skill Threads dipilih otomatis berdasarkan konteks tugas. Semua perintah
Playwright dijalankan dengan `/root/threads-venv/bin/python` — lihat catatan di
[§3.1](#31-di-vps-pasang-playwright).

### 5.1 Discovery: mencari postingan

Buka `https://www.threads.net/search?q=<kata kunci>&serp_type=default` per kata
kunci, tunggu render, scroll dua kali, lalu ekstrak post dari payload JSON
(`script[type="application/json"]`). Ekstraksi dari JSON dipakai, bukan dari DOM,
karena nama class Threads sering berubah.

| # | Perintah | Fungsi | Tanda berhasil |
|---|---|---|---|
| 1 | `/root/threads-venv/bin/python skills/social-media/threads-lead-generation/scripts/threads-scrape-playwright.py` | cari lead untuk semua kata kunci bawaan | satu baris `<kata kunci>: N lead` per kata kunci |
| 2 | `... --keywords "daftar merek" "paten" --limit 5` | batasi kata kunci dan jumlah lead | JSON berisi `post_id`, `username`, `url`, `caption` |
| 3 | `... --self-accounts <handle_anda>` | kecualikan postingan akun sendiri | postingan akun sendiri tidak muncul di hasil |
| 4 | `... --out leads.json` | simpan hasil ke berkas | `N lead ditulis ke leads.json` |

Urutan penyaringan: caption harus memuat kata kunci topik **dan** kata kunci niat,
lalu dibuang bila memuat kata jualan/promo, memuat pola akun jasa, atau username-nya
mengandung `legal`, `konsultan`, `advokat`, `official`. Daftar lengkap ada di
`references/threads-lead-keywords.yml`.

Contoh keluaran (handle disamarkan):

```json
[
  {
    "post_id": "AbCdEfGhIjK",
    "username": "@example_user",
    "url": "https://www.threads.net/@example_user/post/AbCdEfGhIjK",
    "keyword": "daftar merek",
    "caption": "Ada yang bisa bantu daftar merek? Sudah coba sendiri tapi bingung isinya"
  }
]
```

Scraping bersifat baca saja: hasilnya tetap keluar walau sesi sudah kedaluwarsa,
dan lebih banyak bila sesi masih hidup. Karena itu lolosnya scraping bukan bukti
sesi masih valid — hanya jalur balasan yang membuktikan itu.

### 5.2 Balas satu postingan

Skrip balasan memuat sesi dari berkas `storage_state.json`:

```python
browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
context = await browser.new_context(storage_state="/root/storage_state.json")
page = await context.new_page()
```

1. Buka permalink postingan lalu tunggu render:

```python
await page.goto("https://www.threads.net/@{username}/post/{post_id}", wait_until="networkidle")
await page.wait_for_timeout(4000)
```

2. Pastikan tidak ada ajakan `Continue with Instagram`. Bila ada, sesi mati —
   ulangi [§3.2](#32-di-laptop-ekspor-sesi-login) dan [§3.3](#33-kirim-sesi-ke-vps).
3. Isi kolom balasan dan kirim:

```python
box = page.locator("div[role='textbox']").first
await box.click()
await box.fill(REPLY)
await box.press("Enter")
await page.wait_for_timeout(5000)
```

4. Tunggu sampai overlay `Posting...` hilang, lalu pastikan teks balasan
   benar-benar ter-render di dalam thread sebelum melaporkan sukses. Simpan bukti:

```python
await page.screenshot(path="/root/reply_success.png")
```

5. Jeda 10–30 detik antar balasan dan variasikan kalimatnya.

Isi balasan: 1–3 kalimat berisi fakta produk, tanpa ajakan DM dan tanpa tawaran
konsultasi; arahkan ke `example.com` atau sebut `@yourbrand`.

Bila login wall tetap muncul padahal `storage_state.json` masih ada, tambahkan
tiga penyetelan stealth sebelum `new_page()` — User-Agent desktop, `viewport`
1280x800, dan `navigator.webdriver = undefined`. Polanya ada di
`skills/social-media/threads-automation/references/session-and-auth.md`.

### 5.3 Kalau bermasalah

| Gejala | Tindakan |
|---|---|
| `Looks like you launched a headed browser without having a XServer running` | jangan pakai `headless=False` di VPS; ekspor sesi di laptop |
| `Executable doesn't exist at .../ms-playwright/chromium-...` | `playwright install chromium` belum dijalankan |
| `error while loading shared libraries` | `playwright install-deps chromium` sebagai root |
| `Timeout ... waiting for div[role='textbox']` | sesi kedaluwarsa (cek penanda `Continue with Instagram`) atau selector berubah |
| `Strict mode violation` pada `fill()` | lebih dari satu elemen cocok — pakai `.first` atau filter `aria-placeholder` |
| `TargetClosedError: Target page, context or browser has been closed` | browser kehabisan memori, atau launch headed tanpa display |
| `ModuleNotFoundError: No module named 'playwright'` | skrip dijalankan dengan `python3` sistem — pakai `/root/threads-venv/bin/python` |

Bila selector perlu diperiksa ulang:

```python
await page.screenshot(path="/root/debug.png", full_page=True)   # kondisi halaman saat gagal
await page.locator("div[role='textbox']").count()                # jumlah elemen yang cocok
```

Selector terverifikasi ada di
`skills/social-media/threads-automation/references/playwright_selectors.md`.

## 6. Batasan dan Catatan Operasional

**Jaringan.** Tahap tulis (komentar, like, posting) sebaiknya dijalankan dari
jaringan residential, bukan VPS cloud: alamat IP datacenter terdaftar di basis
data Meta dan aktivitas penulisan darinya jauh lebih sering memicu pembatasan.
Tahap scraping aman dijalankan dari VPS; tahap pengiriman balasan sebaiknya dari
jaringan lokal atau melalui residential proxy.

**Risiko.**

1. **Pemblokiran akun.** Tanpa jeda yang menyerupai perilaku manusia, akun
   berpotensi kena checkpoint, pembatasan fitur, atau pemblokiran permanen.
2. **Kerapuhan terhadap perubahan UI.** Perubahan struktur HTML atau React pada
   antarmuka Threads dapat mematahkan selector Playwright.
3. **Konsumsi sumber daya.** Instance Chromium memakai memori dan CPU jauh lebih
   besar dibanding pemanggilan HTTP biasa.
4. **Ketergantungan pada sesi manusia.** Cookie pada `storage_state.json` dapat
   kedaluwarsa tanpa peringatan sehingga perlu login manual ulang.
5. **Throughput rendah secara desain.** Kombinasi IP lokal dan jeda manusiawi
   membatasi jumlah balasan per satuan waktu — konsekuensi langsung dari menjaga
   keamanan akun.

Automasi browser tidak sejalan dengan Terms of Service Meta. Penggunaan
sepenuhnya menjadi tanggung jawab pengguna.

## 7. Keamanan

Berkas berikut tidak pernah di-commit dan telah dicakup `.gitignore`: `.env`,
`auth.json`, `state.db*`, `sessions/`, `logs/`, `cache/`, `bin/`, `skills/.hub/`,
`storage_state*.json`, `threads_auth*.json`, `cookies*.json`, `*.pem`, `*.key`,
serta setiap berkas yang memuat `token` atau `secret` pada namanya.

Sebelum setiap commit, verifikasi daftar staged:

```bash
git add -A
git diff --cached --name-only | grep -E '\.env$|auth\.json|state\.db|storage_state|cookie|token|secret'
```

Perintah tersebut harus tidak menghasilkan output. Catatan: aturan pengecualian
pada `.gitignore` (mis. `!.env.template`) harus diletakkan di baris terakhir
karena Git menerapkan aturan pencocokan terakhir yang menang — pola seperti
`*.env.*` akan meniadakan pengecualian yang ditulis sebelumnya.

## 8. Referensi

### 8.1 Cakupan skill

| Skill | Fungsi | Berkas pendukung |
|---|---|---|
| `threads-automation` | Alur kerja scraping dan engagement end-to-end | `references/keyword-guide.md`, `references/playwright_selectors.md`, `references/session-and-auth.md`, `references/json-pathing.md` |
| `threads-lead-generation` | Ekstraksi lead berintensi tinggi | `references/threads-lead-keywords.yml`, `templates/threads-lead-template.md`, `scripts/threads-scrape-playwright.py`, `scripts/threads-scrape-verify.js` |
| `threads-lead-engagement` | Riset dan pembalasan lead | — |
| `threads-engagement-automation` | Orkestrasi discovery dan reply | — |
| `threads-reply-agent` | Auto-reply khusus postingan merek/HKI | — |

### 8.2 Struktur repositori

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

### 8.3 Catatan desain

**Kenapa browser automation, bukan API resmi.** Endpoint Threads
(`POST /{thread-user-id}/threads` + `threads_publish`) hanya menerima postingan
milik akun pemilik token, sehingga tidak bisa membalas postingan akun lain.
Pembahasan lengkap ada di
`skills/social-media/threads-automation/references/session-and-auth.md`.

**Sesi tidak pernah dibuat otomatis.** Login otomatis rentan CAPTCHA dan
verifikasi dua faktor, jadi sesi selalu berasal dari login manual yang diekspor
ke `storage_state.json` ([§3.2](#32-di-laptop-ekspor-sesi-login)).

**Evasi deteksi otomatis.** Tiga penyesuaian pada konteks Chromium: menghapus
flag `navigator.webdriver` lewat `add_init_script`, memakai User-Agent browser
desktop standar, dan menjalankan dengan
`--disable-blink-features=AutomationControlled`.

**Ambil data dari JSON, bukan DOM.** Payload Relay server-side
(`script[type="application/json"]`) lebih stabil daripada selector HTML.
Jalur pathnya ada di `references/json-pathing.md`; validasi ekstraksi bisa
dilakukan offline dengan `scripts/threads-scrape-verify.js`.
