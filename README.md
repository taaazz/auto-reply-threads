# AI agent auto reply threads!

Profil [Hermes Agent](https://hermes-agent.nousresearch.com/docs) untuk otomasi
engagement Threads: penemuan lead di niche HKI/merek/paten, penyaringan
relevansi, dan pengiriman balasan otomatis dengan persona Gen Z yang ringkas dan
tidak berorientasi jualan.

Repositori ini adalah *distribution* profil — dapat dipasang di mesin lain
melalui `hermes profile install`. Cakupan sengaja dibatasi pada dua kebutuhan
produksi: **scraping Threads** dan **auto-reply**.

- Versi: `0.2.1`
- Kebutuhan minimum: Hermes Agent `>= 0.12.0`, Python `3.10+`
- Lisensi: MIT

## Daftar Isi

1. [Instalasi](#1-instalasi)
2. [Konfigurasi](#2-konfigurasi)
3. [Penggunaan](#3-penggunaan)
4. [Arsitektur](#4-arsitektur)
5. [Cakupan Skill](#5-cakupan-skill)
6. [Catatan Operasional](#6-catatan-operasional)
7. [Batasan dan Risiko](#7-batasan-dan-risiko)
8. [Keamanan](#8-keamanan)
9. [Pembaruan](#9-pembaruan)

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

## 2. Konfigurasi

Salin template dan isi nilainya:

```bash
cp ~/.hermes/profiles/promo-in/.env.template ~/.hermes/profiles/promo-in/.env
$EDITOR ~/.hermes/profiles/promo-in/.env
```

| Variabel | Keterangan | Wajib |
|---|---|---|
| `ZERNIO_API_KEY` | Posting dan pembacaan Threads melalui Zernio | Tidak |
| `SERPAPI_API_KEY` | Fallback pencarian | Tidak |
| `FIRECRAWL_API_KEY` | Fallback scraping halaman | Tidak |
| `HERMES_CUSTOM_API_COMMANDCODE_AI_API_KEY` | Kredensial provider LLM (OpenAI-compatible) | Tidak |

`config.yaml` hanya berisi referensi `${ENV_VAR}` dan tidak pernah memuat
kredensial literal. Sesi login Threads bukan variabel lingkungan: simpan berkas
`storage_state.json` di luar repositori (sudah tercakup `.gitignore`).

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

## 4. Arsitektur

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

## 5. Cakupan Skill

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
├── distribution.yaml          manifest profil (versi, allowlist, env_requires)
├── config.yaml                pengaturan Hermes — hanya referensi env
├── SOUL.md, soul.md           persona dan identitas agen
├── README.md                  dokumen ini
├── .env.template              template variabel lingkungan
├── .gitignore                 daftar berkas yang tidak pernah di-commit
├── memories/                  mirror memori pengguna (tidak ikut terpasang)
└── skills/social-media/       lima skill Threads
```

## 6. Catatan Operasional

Tahap *write* (komentar, like, posting) sebaiknya dijalankan dari jaringan
residential, bukan dari VPS cloud. Alamat IP datacenter terdaftar pada basis data
Meta dan aktivitas penulisan darinya jauh lebih sering memicu pembatasan. Tahap
scraping dapat dijalankan di VPS; tahap pengiriman balasan sebaiknya dijalankan
dari jaringan lokal atau melalui residential proxy.

## 7. Batasan dan Risiko

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

## 8. Keamanan

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

Perintah tersebut harus tidak menghasilkan output. Catatan: `!.env.template`
ditempatkan pada baris terakhir `.gitignore` karena Git menerapkan aturan
pencocokan terakhir yang menang.

## 9. Pembaruan

```bash
hermes profile update promo-in
hermes profile info promo-in
```

`update` hanya menimpa path yang tercantum pada `distribution_owned`. Untuk
penyesuaian khusus mesin, gunakan direktori `local/` — direktori tersebut
milik pengguna dan tidak akan ditimpa.
