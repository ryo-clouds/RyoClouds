# Catatan Sistem (Changlog Build)

Semua keputusan & perubahan teknis dicatat di sini, terbaru di atas.

## 2026-08-07 — Fondasi Reiko dibangun

- **Struktur dibuat**: `core/`, `config/`, `employees/reiko/`, `docs/`, `plans/`.
- **core/settings.py**: baca rahasia dari `config/secret.env`.
- **core/log.py**: logger append ke `logs/<nama>.jsonl`.
- **core/send.py**: pengirim tunggu Discord, mode `latihan`/`kirim`, retry 3x.
- **employees/reiko/run.py**: pengumpul tren nyata.
  - Google Trends RSS (US, JP) → jalan.
  - Hacker News front page (Algolia) → jalan.
  - Reddit (.json) → **diblokir 403** (Reddit blokir IP cloud). Ditangguhkan.
- **employees/reiko/head.py**: penyusun laporan (latihan OK).

## 2026-08-07 — Refactor: 2 niche TERPISAH (koreksi user)

- User mau 2 niche berdiri sendiri: **AI** dan **Budaya Jepang**, bukan digabung "AI x Jepang".
- **run.py**: klasifikasi kembalikan ke 2 bucket terpisah (`niches={"ai":[], "japan":[]}`), top 5 masing.
  - Word-boundary utk "ai" (`\bai\b`) — fix bug "raiders"/"taiwan" yang salah match substring "ai".
  - Keyword Jepang ditambah form kanji/kana (Google Trends JP isinya kanji: 富士, 日本, アニメ...).
  - Keyword AI ditambah istilah model real (qwen, gemini, claude, inference, nvidia, gpu, agent...).
- **head.py**: kirim SATU laporan terpisah per niche (2 pemanggilan send.report).
- **cron**: prompt diperbarui → buat 2 pesan terpisah, mode `kirim` (fallback Telegram).

## 2026-08-07 — Blocker: Discord menolak IP cloud

- Discord menjawab **error 1010** ("blocked by cloud") pada webhook.
- Penyebab: mesin ini di **AWS datacenter** (IP `13.220.100.239` Ashburn,
  `AS14618 Amazon`). Discord (via Cloudflare-like gate) memblokir traffic
  dari datacenter cloud.
- Webhook user **valid** (Discord menjawab 1010 blokir, bukan 404/401 soal webhook).
- **Keputusan:** eksekusi mode **latihan** dulu (kerja lancar). Discord live
  ditunda sampai pakai mesin non-AWS (rumah/VPS residensial).

## Next (kepala)

- **Hermes cron AKTIF** — job "Reiko - riset & kirim konten (2 jam)"
  (`08f9cb3eb6be`), tiap 120 menit, mode **latihan**. Pipeline end-to-end
  terverifikasi: run.py → latest.json → susun konten → send.report(latihan) OK.
- **Tinggal:** pindahkan ke mesin NON-AWS (rumah/VPS residensial) biar Discord
  terima (error 1010 hilang), lalu ubah cron ke mode `kirim`.

Lihat juga: [[index]] · [[fondasi]] · [[karyawan-reiko]]