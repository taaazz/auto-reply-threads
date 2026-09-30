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
   login browser (lihat [§5.1](#51-langkah-1--ekspor-sesi-di-mesin-berdisplay)).
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

Seluruh otomasi berjalan di atas **Playwright** (Chromium). Bagian ini adalah
prosedur penyiapan di mesin baru. Nomor versi di bawah adalah versi yang
diverifikasi saat dokumen ini ditulis.

### 4.1 Prasyarat

| Komponen | Versi terverifikasi | Keterangan |
|---|---|---|
| Python | 3.10+ | runtime skrip Playwright |
| Playwright (Python) | `1.63.0` | paket `playwright` |
| Chromium (Playwright build) | `chromium-1243` | diunduh ke `~/.cache/ms-playwright` |
| Node.js | 22.x | hanya untuk skrip `threads-scrape-verify.js` |
| Display (X server) | — | hanya untuk tahap ekspor sesi (§5.1) |

Server tanpa layar dapat menjalankan seluruh tahap otomatis dengan
`headless=True`; yang tidak bisa dilakukan di sana hanyalah login manual.

### 4.2 Instalasi Python + Chromium

Gunakan virtual environment agar versi Playwright tidak berbenturan dengan paket
sistem.

```bash
python3 -m venv ~/threads-venv
~/threads-venv/bin/pip install --upgrade pip
~/threads-venv/bin/pip install playwright
~/threads-venv/bin/playwright install chromium
```

`playwright install chromium` mengunduh binary browser (~400 MB) ke
`~/.cache/ms-playwright`. Langkah ini **tidak** memasang pustaka sistem yang
dibutuhkan Chromium. Di container atau server minimal, jalankan sebagai root:

```bash
~/threads-venv/bin/playwright install-deps chromium
```

Tanpa langkah tersebut, launch gagal dengan
`error while loading shared libraries: libgbm.so.1` atau serupa
(`libnss3`, `libatk-1.0`, `libasound2`).

Untuk menempatkan binary browser di lokasi lain (mis. volume terpisah atau
image read-only), set sebelum instalasi:

```bash
export PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright
~/threads-venv/bin/playwright install chromium
```

### 4.3 Node.js opsional

Skrip verifikasi payload `skills/social-media/threads-lead-generation/scripts/threads-scrape-verify.js`
hanya memakai modul bawaan Node (`fs`, `path`) — tidak perlu memasang Playwright
versi Node:

```bash
node -v
node skills/social-media/threads-lead-generation/scripts/threads-scrape-verify.js hasil.html
```

Jika ingin Playwright versi Node untuk keperluan lain:

```bash
npm init -y && npm install --save-dev playwright
npx playwright install chromium
```

### 4.4 Verifikasi instalasi

Jalankan skrip berikut untuk memastikan browser bisa launch, context stealth
aktif, dan ekspor `storage_state` berfungsi. Skrip tidak membuka Threads dan
tidak butuh sesi.

```python
# pw_check.py
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
            viewport={"width": 1280, "height": 800},
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = await context.new_page()
        await page.goto("https://example.com", wait_until="domcontentloaded")
        print("navigator.webdriver =", await page.evaluate("navigator.webdriver"))
        print("userAgent           =", await page.evaluate("navigator.userAgent"))
        await context.storage_state(path="/tmp/pw_state.json")
        await browser.close()

asyncio.run(main())
```

```bash
~/threads-venv/bin/python pw_check.py
```

Keluaran yang diharapkan:

```
navigator.webdriver = None
userAgent           = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36
```

`None` berarti `add_init_script` berjalan dan flag otomatisasi berhasil
disembunyikan. Jika tercetak `True`, init script dipasang setelah navigasi
pertama — urutan pemanggilan harus diperbaiki sebelum lanjut.

### 4.5 Variabel lingkungan runtime

Tidak ada variabel yang wajib. Variabel berikut hanya untuk menyesuaikan runtime
Playwright:

| Variabel | Fungsi |
|---|---|
| `PLAYWRIGHT_BROWSERS_PATH` | lokasi binary browser selain `~/.cache/ms-playwright` |
| `PLAYWRIGHT_DOWNLOAD_HOST` | mirror unduhan untuk jaringan terbatas |
| `PWDEBUG=1` | membuka Playwright Inspector (butuh display; gunakan pada tahap debug) |
| `DEBUG=pw:api` | log detail seluruh pemanggilan API Playwright |

Pasang paket pada venv yang sama dengan yang dipakai agen, agar pemanggilan
`playwright` tidak jatuh ke instalasi sistem yang berbeda:

```bash
~/threads-venv/bin/python skrip.py
```

## 5. Alur Penggunaan Playwright

Bagian ini merinci pemakaian Playwright dari ekspor sesi sampai balasan
terverifikasi terkirim.

### 5.1 Langkah 1 — Ekspor sesi di mesin berdisplay

Login tidak pernah dilakukan otomatis karena memicu CAPTCHA dan verifikasi dua
faktor. Sesi diambil dari browser yang sudah diverifikasi manusia, lalu diekspor
menjadi berkas state.

```python
# export_session.py — jalankan di mesin yang punya layar (laptop operator)
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.threads.net/login")

        await asyncio.get_event_loop().run_in_executor(
            None, input, "Login manual di jendela browser, lalu tekan Enter di terminal..."
        )

        await context.storage_state(path="storage_state.json")
        print("state tersimpan")
        await browser.close()

asyncio.run(main())
```

Catatan penting:

- Tahap ini **wajib** dijalankan pada mesin berdisplay. Launch `headless=False`
  di server tanpa X server gagal sebelum ada halaman terbuka dengan pesan
  `Looks like you launched a headed browser without having a XServer running`.
- `xvfb-run` hanya menolong bila masih ada manusia yang dapat menyelesaikan login
  di jendela tak terlihat tersebut.
- Di Windows, mencetak emoji ke konsol cp1252 memunculkan `UnicodeEncodeError`
  **setelah** berkas tersimpan. Ekspornya sudah berhasil; jangan mengulang login.
- Periksa isi berkas sebelum dipindahkan: harus memuat cookie `sessionid` untuk
  domain `threads.net`.

### 5.2 Langkah 2 — Pindahkan state ke runner

```bash
scp storage_state.json user@runner:/root/storage_state.json
ssh user@runner 'chmod 600 /root/storage_state.json && ls -l /root/storage_state.json'
```

Simpan di luar repositori. Pola `storage_state*.json` sudah masuk `.gitignore`,
tetapi menempatkannya di direktori rumah tetap lebih aman.

### 5.3 Langkah 3 — Bangun context browser (stealth)

Semua skrip otomasi memakai context berikut. Tiga penyesuaian di dalamnya yang
membuat sesi tidak langsung ditolak: User-Agent desktop, `viewport` tetap, dan
penghapusan `navigator.webdriver`.

```python
browser = await p.chromium.launch(
    headless=True,
    args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
)
context = await browser.new_context(
    storage_state="/root/storage_state.json",
    user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    viewport={"width": 1280, "height": 800},
)
await context.add_init_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
)
page = await context.new_page()
```

`add_init_script` harus dipanggil **sebelum** `new_page()` pertama. Flag
`--no-sandbox` diperlukan saat berjalan sebagai root atau di dalam container.

### 5.4 Langkah 4 — Scraping (baca) postingan lead

1. Buka halaman pencarian atau permalink: `await page.goto(url, wait_until="networkidle")`.
2. Beri jeda render React: `await page.wait_for_timeout(3000)`.
3. Ambil HTML: `html = await page.content()`, simpan ke berkas.
4. Ekstrak payload: Threads mengirim data server-side pada `__NEXT_DATA__` /
   payload Relay. Verifikasi struktur dengan:

```bash
node skills/social-media/threads-lead-generation/scripts/threads-scrape-verify.js hasil.html
```

5. Saring kandidat memakai daftar kata kunci di
   `skills/social-media/threads-lead-generation/references/threads-lead-keywords.yml`
   dan panduan penyaringan di `skills/social-media/threads-automation/references/keyword-guide.md`.

Baca **tidak** membuktikan sesi masih hidup: pencarian dan permalink tetap
mengembalikan data walau cookie sudah mati, karena payload dikirim oleh server.
Hanya jalur tulis (§5.5) yang membuktikan validitas sesi.

### 5.5 Langkah 5 — Membalas (tulis)

Hanya otomasi browser yang dapat membalas postingan milik akun lain; Graph API
Meta tidak mendukungnya (lihat
`skills/social-media/threads-automation/references/session-and-auth.md`).

1. **Tuju URL postingan langsung:**
   `https://www.threads.net/@{username}/post/{post_id}`
2. **Tunggu halaman siap:**
   `await page.goto(url, wait_until="networkidle")` lalu `await page.wait_for_timeout(4000)`.
3. **Pastikan sudah login:** bila muncul ajakan `Continue with Instagram`, sesi
   tidak valid — hentikan proses dan ekspor ulang `storage_state.json`.
4. **Isi kolom balasan:**

```python
box = page.locator("div[role='textbox']").first      # atau div[contenteditable='true']
await box.click()
await box.fill(REPLY)
await box.press("Enter")                              # alternatif: klik tombol Post
```

   Alternatif tombol:
   `await page.locator("div[role='button']:has-text('Post')").first.click()`
5. **Tunggu overlay selesai:** `await page.wait_for_timeout(5000)` untuk memberi
   waktu overlay `Posting...` hilang.
6. **Verifikasi sebelum melaporkan sukses:** pastikan teks balasan benar-benar
   ter-render di dalam thread. Overlay hilang saja bukan bukti balasan terkirim.
7. **Jeda antar balasan:** 10–30 detik, dan variasikan kalimat antar balasan —
   teks identik pada banyak akun adalah sinyal spam paling jelas.
8. **Isi balasan:** 1–3 kalimat berisi fakta produk, tanpa ajakan DM dan tanpa
   tawaran konsultasi; arahkan ke `example.com` atau sebut `@yourbrand`.

### 5.6 Langkah 6 — Debugging dan verifikasi visual

Helper yang paling sering dipakai saat selector berubah:

```python
# screenshot penuh untuk melihat kondisi halaman saat gagal
await page.screenshot(path="debug.png", full_page=True)

# trace lengkap (DOM snapshot + network + console), dibuka dengan:
#   npx playwright show-trace trace.zip
await context.tracing.start(screenshots=True, snapshots=True)
# ... jalankan langkah yang bermasalah ...
await context.tracing.stop(path="trace.zip")
```

| Alat | Cara pakai |
|---|---|
| Inspector visual | `PWDEBUG=1 ~/threads-venv/bin/python skrip.py` (butuh display) |
| Log API | `DEBUG=pw:api ~/threads-venv/bin/python skrip.py` |
| Simpan HTML gagal | `await page.content()` lalu periksa secara offline |
| Cek elemen | `await page.locator("selector").count()` |

Selector yang sudah terverifikasi ada di
`skills/social-media/threads-automation/references/playwright_selectors.md`.

### 5.7 Troubleshooting

| Gejala | Penyebab | Tindakan |
|---|---|---|
| `Looks like you launched a headed browser without having a XServer running` | `headless=False` di server tanpa display | jalankan `headless=True`; ekspor sesi di laptop operator |
| `Executable doesn't exist at .../ms-playwright/chromium-.../chrome` | binary browser belum diunduh | `~/threads-venv/bin/playwright install chromium` |
| `error while loading shared libraries: libgbm.so.1` | pustaka sistem belum dipasang | `~/threads-venv/bin/playwright install-deps chromium` (root) |
| `Timeout 30000ms exceeded` pada `div[role='textbox']` | belum login atau selector berubah | cek penanda `Continue with Instagram`, ekspor ulang sesi, sesuaikan selector |
| `Strict mode violation` pada `fill()` | lebih dari satu elemen cocok | pakai `.first`, `.last`, atau filter `aria-placeholder` |
| `TargetClosedError: Target page, context or browser has been closed` | browser mati atau launch headed tanpa display | jalankan headless, pastikan memori cukup, cek ulang argumen launch |
| `navigator.webdriver` masih `True` | init script dipasang setelah navigasi | panggil `add_init_script` sebelum `new_page()` pertama |
| Login wall walau cookie sudah ada | fingerprint terdeteksi atau sesi kedaluwarsa | ekspor ulang `storage_state.json` |
| Overlay `Posting...` masih tampil | balasan belum selesai dikirim | tunggu ~5 detik dan verifikasi teks ter-render sebelum melaporkan sukses |
| Proses berhenti tanpa galat di server kecil | memori tidak cukup untuk Chromium | kurangi jumlah context paralel, jalankan satu browser per proses |

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
