# Keyword & Intent Guide for Threads Lead Capture

## Intent Keywords (message shows user asks for help/asks for recommendation)
- "cari jasa"
- "butuh jasa"
- "rekomendasi"
- "spill"
- "ada yang tau"
- "ada yang tahu"
- "pertemukan"
- "info dong"
- "info daftar"
- "cara daftar"
- "mau daftar"
- "bantu proses"
- "urus hak"
- "daftar trademark"
- "bisa bantu"

## Topic Keywords (HKI & related)
- "merek"
- "hki"
- "hak cipta"
- "paten"
- "trademark"
- "brand registration"

## Negative Keywords (exclude)
- "dm saya" | "dm kakk" | "dm kami"
- "terima jasa" | "promo" | "harga murah"
- "hubungi wa" | "konsultan hki" | "jasa pendaftaran"
- "buka sesi" | "gratis biaya pendampingan"
- "open order" | "ready stock"

## Username Exclusions (case-insensitive)
- `legal`, `law`, `konsultan`, `jasa`, `advokat`, `notaris`, `kemenkum`, `official`, `patenindo`

## Regex Pattern
```
(?i)(?:merek|paten|hki|hak cipta|trademark|brand registration)
```

## Filter Logic
1. Post caption must match **Topic Keywords** AND at least one **Intent Keyword**.
2. Post must NOT contain any **Negative Keywords**.
3. Username must NOT be in **Exclusion List**.