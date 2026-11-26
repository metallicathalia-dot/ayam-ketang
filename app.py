import json
import os
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.utils import secure_filename

app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))
app.secret_key = "sapabatin_secret_key_remajasehat"

# ==========================================
# KONFIGURASI UPLOAD BUKTI FOTO
# ==========================================
UPLOAD_FOLDER = os.path.join(app.root_path, "uploads", "bukti")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Maksimal 16 MB per request


def is_allowed_image(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS


# ==========================================
# DATABASE MEMORI SEMENTARA (OWNER PANEL)
# ==========================================
DATABASE_OWNER = {
    "riwayat_mood": [],
    "riwayat_chat": [],
    "laporan_darurat": [],
    "laporan_cyberbullying": [],
    "pesan_owner": [],
    "balasan_owner": [],  # Pesan keluar dari Owner ke pengguna saat ada masalah serius
}


DANGER_KEYWORDS = [
    "mati",
    "ingin mati",
    "bunuh diri",
    "kill myself",
    "akhiri hidup",
    "ingin hilang",
    "lukai diri",
    "menyakiti diri",
    "suicide",
    "mati",
  "ingin mati",
  "pengen mati",
  "mau mati",
  "mending mati",
  "bunuh diri",
  "bundir",
  "kill myself",
  "kms",
  "want to die",
  "wanna die",
  "end my life",
  "akhiri hidup",
  "mengakhiri hidup",
  "akhiri semuanya",
  "sudahi hidup",
  "gantung diri",
  "loncat dari",
  "minum racun",
  "overdosis",
  "ingin hilang",
  "menghilang selamanya",
  "pergi selamanya",
  "tidur selamanya",
  "istirahat selamanya",
  "pamit selamanya",
  "selamat tinggal semuanya",
  "capek hidup",
  "lelah hidup",
  "bosan hidup",
  "tidak kuat lagi",
  "gak kuat lagi",
  "udah gak kuat",
  "menyerah hidup",
  "hidup gak berguna",
  "tidak ada gunanya hidup",
  "dunia lebih baik tanpaku",
  "jadi beban",

  "lukai diri",
  "melukai diri",
  "menyakiti diri",
  "siksa diri",
  "menyiksa diri",
  "self harm",
  "self-harm",
  "selfharm",
  "hurt myself",
  "harm myself",
  "sayat tangan",
  "nyayat",
  "cutting",
  "gores tangan",
  "mau dibunuh",
  "diancam dibunuh",
  "takut dibunuh",
  "dipukuli",
  "kdrt",
  "kekerasan fisik",
  "disiksa",
  "dilecehkan",
  "pelecehan",
  "diperkosa",
  "dalam bahaya"
  "un-alive",
  "unalive",
  "mokad",
  "koit",
  "modar",
  "b*ndir",
  "b.u.n.d.i.r",
  "m4ti",
  "s*icide",
  "suicidal",
  "saya ingin mati",
  "aku ingin mati",
  "gw pengen mati",
  "gue pengen mati",


  "surat wasiat",
  "pesan terakhir",
  "titip orang tua",
  "titip adik",
  "titip kakak",
  "titip keluarga",
  "maafin aku semua",
  "maafkan aku semua",
  "terima kasih untuk semuanya",
  "selamat tinggal dunia",
  "goodbye world",
  "nyebur",
  "tabrakin diri",
  "menabrakkan diri",
  "minum baygon",
  "minum obat banyak",
  "tenggak obat",
  "iris nadi",
  "potong nadi",
  "gorok",
  "lompat gedung",
  "loncat jembatan",


  "gak ada jalan keluar",
  "tidak ada jalan keluar",
  "buntu banget",
  "hampa banget",
  "kosong banget",
  "gak pantas hidup",
  "tidak pantas hidup",
  "sampah masyarakat",
  "gagal total",
  "hopeless",
  "worthless",
  "cant take it anymore",
  "can't take it anymore",
  "give up on life",
  "tired of living",
  "better off dead",
  "no reason to live",

 
  "ancaman sebar",
  "sebar foto",
  "sebar video",
  "diancam sebar",
  "pemerasan",
  "diperas",
  "dirudapaksa",
  "penculikan",
  "diculik",
  "disekap",
  "penyekapan",
  "ancaman pembunuhan",
  "bawa senjata",
  "ditodong",
  "dianiaya",
  "penganiayaan",
  "babak belur",
  "berdarah-darah",

 
  "dibully habis-habisan",
  "gak punya siapa-siapa",
  "tidak punya siapa-siapa",
  "sendirian di dunia",
  "semua orang benci aku",
  "semua benci gw"
]


def has_danger_keyword(text: str) -> bool:
    lowered = (text or "").lower()
    return any(kw in lowered for kw in DANGER_KEYWORDS)


def kirim_notifikasi_owner(kategori: str, pesan: str):
    """Fungsi otomatis untuk mencatat alarm darurat ke Dashboard Owner"""
    notif = {
        "waktu": datetime.now().strftime("%d %B %Y - %H:%M:%S"),
        "kategori": kategori,
        "pesan": pesan,
    }
    DATABASE_OWNER["laporan_darurat"].insert(0, notif)
    print(f"\n[ALARM OWNER PANEL] 🚨 {kategori}: {pesan}\n")


# ==========================================
# ROUTING HALAMAN UTAMA (FRONTEND)
# ==========================================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/mood")
def mood_tracker():
    return render_template("mood.html")


@app.route("/diari-ai")
def diari_ai():
    return render_template("diari.html")


@app.route("/literasi")
def literasi():
    return render_template("literasi.html")


@app.route("/uploads/bukti/<filename>")
def lihat_bukti_foto(filename):
    safe_name = secure_filename(filename)
    return send_from_directory(UPLOAD_FOLDER, safe_name)


# ==========================================
# API PENGATURAN MOOD TRACKER
# ==========================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

# Menyimpan timestamp alarm tren mood terakhir per pengguna agar tidak spam
LAST_MOOD_ALERT_TIME = {}


def panggil_groq_singkat(system_prompt: str, user_prompt: str, max_tokens: int = 220):
    try:
        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.4,
            "max_tokens": max_tokens,
        }
        req = urllib.request.Request(
            GROQ_CHAT_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "SapaBatin-Flask/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            choices = body.get("choices") or []
            if choices:
                teks = (((choices[0].get("message") or {}).get("content")) or "").strip()
                if teks:
                    return teks
    except Exception as exc:
        print(f"[INFO AI MOOD] Fallback dipakai karena: {repr(exc)}")
    return None


def evaluasi_tren_mood_buruk(nama_user: str):
    """
    Mengecek apakah dalam beberapa hari terakhir mood pengguna konsisten buruk
    (bukan rekap harian biasa). Mengembalikan dict info jika perlu lapor ke Owner,
    atau None jika belum memenuhi pola beberapa hari buruk.
    """
    user_key = nama_user.lower()
    riwayat_user = [
        m for m in DATABASE_OWNER["riwayat_mood"]
        if (m.get("user") or "").strip().lower() == user_key
    ]

    if len(riwayat_user) < 2:
        return None

    cuplikan = riwayat_user[:5]
    skor_list = [int(m.get("skor", 3)) for m in cuplikan]

    jumlah_buruk = sum(1 for s in skor_list if s <= 2)
    rata_rata = sum(skor_list) / len(skor_list)

    if not (jumlah_buruk >= 2 and rata_rata <= 2.3):
        return None

    sekarang = datetime.now()
    terakhir_alarm = LAST_MOOD_ALERT_TIME.get(user_key)
    if terakhir_alarm and (sekarang - terakhir_alarm).total_seconds() < 86400:
        return None

    ringkasan_riwayat = "\n".join([
        f"- [{m.get('waktu')}] Skor {m.get('skor')}/5 | Catatan: {m.get('catatan')}"
        for m in reversed(cuplikan)
    ])

    ai_ringkasan = panggil_groq_singkat(
        system_prompt=(
            "Kamu adalah asisten analitik SapaBatin untuk Owner. Tugasmu menganalisis pola "
            "mood pengguna selama beberapa hari terakhir yang cenderung buruk dan sulit. "
            "Tulis ringkasan singkat (maksimal 3 kalimat) dalam bahasa Indonesia yang objektif, "
            "empatik, dan fokus pada pola kesulitan serta saran perhatian Owner."
        ),
        user_prompt=(
            f"Pengguna: {nama_user}\n"
            f"Rata-rata skor beberapa entri terakhir: {rata_rata:.1f}/5\n"
            f"Riwayat mood:\n{ringkasan_riwayat}"
        ),
        max_tokens=200,
    )

    if not ai_ringkasan:
        ai_ringkasan = (
            f"Pengguna '{nama_user}' mencatat mood rendah ({jumlah_buruk} dari {len(cuplikan)} entri "
            f"terakhir berskor <= 2, rata-rata {rata_rata:.1f}/5). Perlu perhatian dan pendampingan lanjutan dari Owner."
        )
    if not ai_ringkasan:
        ai_ringkasan = (
            f"Pengguna '{nama_user}' mencatat mood rendah ({jumlah_buruk} dari {len(cuplikan)} entri "
            f"terakhir berskor <= 2, rata-rata {rata_rata:.1f}/5). Perlu perhatian dan pendampingan lanjutan dari Owner."
        )

    LAST_MOOD_ALERT_TIME[user_key] = sekarang
    return {
        "perlu_perhatian": True,
        "ringkasan": ai_ringkasan,
        "jumlah_buruk": jumlah_buruk,
        "rata_rata": round(rata_rata, 2),
    }

    LAST_MOOD_ALERT_TIME[user_key] = sekarang
    return {
        "rata_rata": round(rata_rata, 1),
        "jumlah_buruk": jumlah_buruk,
        "total_dicek": len(cuplikan),
        "analisis_ai": ai_ringkasan,
        
        "riwayat_teks": ringkasan_riwayat,
    }


@app.route("/api/mood", methods=["POST"])
def save_mood():
    data = request.json or {}
    nama = (data.get("user") or "Remaja SapaBatin").strip()
    kontak = (data.get("kontak") or "-").strip()
    skor = int(data.get("skor", 3))
    catatan = (data.get("catatan") or "-").strip()

    entry = {
        "waktu": datetime.now().strftime("%d %B %Y - %H:%M"),
        "user": nama,
        "kontak": kontak,
        "skor": skor,
        "catatan": catatan,
    }
    DATABASE_OWNER["riwayat_mood"].insert(0, entry)

    alert_owner = False
    evaluasi = evaluasi_tren_mood_buruk(nama)
    if not isinstance(evaluasi, dict):
        evaluasi = {}

    if evaluasi.get("perlu_perhatian"):
        alert_owner = True
        DATABASE_OWNER["laporan_darurat"].insert(0, {
            "waktu": entry["waktu"],
            "user": nama,
            "kontak": kontak,
            "sumber": "Mood Tracker (Tren Negatif Berulang)",
            "pesan": f"Skor terbaru {skor}/5 — Catatan: {catatan} | {evaluasi.get('ringkasan', '')}",
            "tingkat": "TREN MOOD SULIT",
        })

    return jsonify({
        "status": "success",
        "alert_owner": alert_owner,
        "evaluasi": evaluasi,
        "data": entry,
    })
    data = request.json or {}
    skor = data.get("skor", 3)
    catatan = data.get("catatan", "-")
    nama = (data.get("user") or "Pengguna Anonim").strip()

    entry = {
        "waktu": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "user": nama,
        "skor": skor,
        "catatan": catatan,
    }
    DATABASE_OWNER["riwayat_mood"].insert(0, entry)

    if int(skor) <= 2:
        kirim_notifikasi_owner(
            "TREN MOOD BURUK (1 MINGGU / SKOR RENDAH)",
            f"Pengguna '{nama}' melaporkan skor mood rendah ({skor}/5) dengan catatan: \"{catatan}\".",
        )

    return jsonify({"status": "success", "message": "Mood berhasil disimpan."})


# ==========================================
# API CHATBOT, PENGALIHAN KE OWNER & GROQ AI
# ==========================================
@app.route("/api/chat", methods=["POST"])
def chat_ai():
    try:
        data = request.json or {}
        user_message = (data.get("message") or "").strip()
        nama_pengguna = (data.get("user") or "Pengguna Anonim").strip()

        if not user_message:
            return jsonify({
                "reply": "Silakan tuliskan pesanmu terlebih dahulu ya.",
                "emergency": False,
                "handover_to_owner": bool(session.get("owner_handover", False)),
            })

        DATABASE_OWNER["riwayat_chat"].insert(0, {"user": nama_pengguna, "pesan": user_message})

        # 1. Cek apakah ada keyword yang membahayakan nyawa
        if has_danger_keyword(user_message):
            session["owner_handover"] = True
            session.modified = True

            kirim_notifikasi_owner(
                "KRISIS / KATA KUNCI BAHAYA NYAWA (SELF-HARM)",
                f"Pengguna '{nama_pengguna}' menuliskan pesan berisiko tinggi:\n\"{user_message}\"\nPercakapan dialihkan ke Owner.",
            )

            DATABASE_OWNER["pesan_owner"].insert(0, {
                "waktu": datetime.now().strftime("%d %B %Y - %H:%M:%S"),
                "user": nama_pengguna,
                "kontak": "Dialihkan otomatis dari Ruang Chat Krisis",
                "pesan": user_message,
                "status": "DARURAT - PERLU SEGERA DIHUBUNGI",
            })

            handover_reply = (
                "Aku menangkap pesan yang menunjukkan kamu sedang berada dalam kondisi sangat berat dan berisiko. "
                "Mulai saat ini percakapanmu langsung dialihkan untuk terhubung dengan Owner SapaBatin agar kamu bisa didampingi langsung. "
                "Silakan gunakan Ruang Hubungi Owner di bawah ini atau hubungi layanan darurat terdekat jika kamu sedang dalam bahaya segera."
            )

            return jsonify({
                "reply": handover_reply,
                "emergency": True,
                "handover_to_owner": True,
            })

        # 2. Jika sesi sebelumnya sudah dialihkan ke Owner, arahkan pesan ke jalur Owner
        if session.get("owner_handover"):
            DATABASE_OWNER["pesan_owner"].insert(0, {
                "waktu": datetime.now().strftime("%d %B %Y - %H:%M:%S"),
                "user": nama_pengguna,
                "kontak": "Sesi Terhubung dengan Owner",
                "pesan": user_message,
                "status": "TERUSKAN KE OWNER",
            })
            return jsonify({
                "reply": (
                    "Percakapanmu sedang berada dalam mode pendampingan Owner. "
                    "Pesanmu sudah diteruskan ke Owner SapaBatin—kamu juga bisa menulis detail kontak/cerita tambahan di Ruang Hubungi Owner."
                ),
                "emergency": True,
                "handover_to_owner": True,
            })

        # 3. Percakapan normal dengan Groq API (multi-turn di session)
        
        raw_history = session.get("chat_history")
        history = [
            msg for msg in (raw_history if isinstance(raw_history, list) else [])
            if isinstance(msg, dict) and msg.get("role") in ("user", "assistant") and "content" in msg
        ]

        history.append({
            "role": "user",
            "content": user_message,
        })
        recent_history = history[-10:]

        groq_api_key = os.environ.get("GROQ_API_KEY", "")
        groq_url = "https://api.groq.com/openai/v1/chat/completions"

        system_prompt = (
            "Kamu adalah SapaBatin, AI pendamping kesehatan mental remaja yang hangat, "
            "empatik, responsif, dan suportif. Tanggapilah langsung apa yang baru saja "
            "dikatakan pengguna dengan nyambung pada konteks percakapan, gunakan bahasa "
            "Indonesia yang natural (maksimal 3 kalimat), dan hindari jawaban klise yang berulang."
        )

        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": system_prompt},
                *recent_history,
            ],
            "temperature": 0.7,
        }

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            groq_url,
            data=req_data,
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json",
                "User-Agent": "SapaBatin-Flask/1.0",
            },
            method="POST",
        )

        ai_reply = None
        last_error_info = None

        try:
            with urllib.request.urlopen(req, timeout=25) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)

                choices = res_json.get("choices") or []
                if choices:
                    content_text = (((choices[0].get("message") or {}).get("content")) or "").strip()
                    if content_text:
                        ai_reply = content_text

                if not ai_reply:
                    last_error_info = f"Respons kosong: {res_json}"
                    print(last_error_info)

        except urllib.error.HTTPError as http_err:
            err_detail = http_err.read().decode("utf-8", errors="ignore")
            last_error_info = f"HTTP {http_err.code}: {err_detail}"
            print(last_error_info)
        except Exception as api_err:
            last_error_info = f"Exception: {repr(api_err)}"
            print(last_error_info)

        if not ai_reply:
            ai_reply = (
                f"Maaf, balasan langsung dari AI belum bisa diambil saat ini ({last_error_info or 'kendala koneksi'}). "
                "Coba kirim ulang pesannya atau gunakan tab Ruang Hubungi Owner jika kamu ingin langsung terhubung dengan Owner."
            )
        else:
            history.append({
                "role": "assistant",
                "content": ai_reply,
            })
            session["chat_history"] = history[-12:]
            session.modified = True

        return jsonify({
            "reply": ai_reply,
            "emergency": False,
            "handover_to_owner": False,
        })

    except Exception as e:
        print(f"Error fatal pada /api/chat: {repr(e)}")
        return jsonify({
            "reply": f"Terjadi error di server Flask: {repr(e)}",
            "emergency": False,
            "handover_to_owner": bool(session.get("owner_handover", False)),
        })


# ==========================================
# API RUANG KHUSUS HUBUNGI OWNER
# ==========================================
@app.route("/api/hubungi-owner", methods=["POST"])
def hubungi_owner():
    data = request.json or {}
    nama = (data.get("nama") or "Pengguna Anonim").strip()
    kontak = (data.get("kontak") or "Tidak dicantumkan").strip()
    pesan = (data.get("pesan") or "").strip()
    darurat = bool(data.get("darurat", False))

    if not pesan:
        return jsonify({"status": "error", "message": "Pesan untuk Owner tidak boleh kosong."}), 400

    entry = {
        "waktu": datetime.now().strftime("%d %B %Y - %H:%M:%S"),
        "user": nama,
        "kontak": kontak,
        "pesan": pesan,
        "status": "DARURAT" if darurat else "PERMINTAAN BANTUAN OWNER",
    }
    DATABASE_OWNER["pesan_owner"].insert(0, entry)

    kirim_notifikasi_owner(
        "PESAN LANGSUNG KE OWNER (DARURAT)" if darurat else "PESAN LANGSUNG KE OWNER",
        f"Dari: {nama} | Kontak: {kontak}\nPesan: \"{pesan}\"",
    )

    return jsonify({
        "status": "success",
        "message": "Pesanmu sudah terkirim ke ruang pantauan Owner SapaBatin. Jika kamu dalam bahaya mendesak, segera hubungi layanan darurat 119 / hotline terdekat.",
    })


@app.route("/api/reset-handover", methods=["POST"])
def reset_handover():
    session["owner_handover"] = False
    session["chat_history"] = []
    session.modified = True
    return jsonify({"status": "success", "handover_to_owner": False})


# ==========================================
# API LAPORAN CYBERBULLYING / HARASSER + FOTO BUKTI
# ==========================================
@app.route("/api/lapor", methods=["POST"])
def laporan_hukum():
    try:
        if request.content_type and "multipart/form-data" in request.content_type:
            kategori = (request.form.get("kategori") or "Cyberbullying").strip()
            kronologi = (request.form.get("kronologi") or "-").strip()
            bukti_teks = (request.form.get("bukti") or "Tidak ada").strip()
            uploaded_files = request.files.getlist("bukti_foto")
        else:
            data = request.json or {}
            kategori = (data.get("kategori") or "Cyberbullying").strip()
            kronologi = (data.get("kronologi") or "-").strip()
            bukti_teks = (data.get("bukti") or "Tidak ada").strip()
            uploaded_files = []

        saved_photos = []
        for file_storage in uploaded_files:
            if not file_storage or not file_storage.filename:
                continue
            original_name = secure_filename(file_storage.filename)
            if not is_allowed_image(original_name):
                return jsonify({
                    "status": "error",
                    "message": f"Format file '{file_storage.filename}' tidak didukung. Gunakan PNG, JPG, JPEG, WEBP, atau GIF.",
                }), 400

            ext = original_name.rsplit(".", 1)[1].lower()
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"
            save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file_storage.save(save_path)

            saved_photos.append({
                "nama_asli": file_storage.filename,
                "url": url_for("lihat_bukti_foto", filename=unique_filename),
            })

        laporan = {
            "waktu": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "kategori": kategori,
            "kronologi": kronologi,
            "bukti": bukti_teks,
            "foto_bukti": saved_photos,
        }
        DATABASE_OWNER["laporan_cyberbullying"].insert(0, laporan)

        info_foto = (
            f"{len(saved_photos)} file foto diunggah ({', '.join([f['nama_asli'] for f in saved_photos])})"
            if saved_photos
            else "Tidak ada foto diunggah"
        )
        kirim_notifikasi_owner(
            f"LAPORAN BARU: {kategori.upper()}",
            f"Kronologi: {kronologi}\nBukti Teks: {bukti_teks}\nFoto Bukti: {info_foto}",
        )

        return jsonify({
            "status": "success",
            "message": f"Laporan berhasil dikirimkan ke Owner SapaBatin ({len(saved_photos)} foto bukti terlampir).",
            "jumlah_foto": len(saved_photos),
        })

    except Exception as e:
        print(f"Error pada /api/lapor: {repr(e)}")
        return jsonify({"status": "error", "message": f"Gagal memproses laporan: {repr(e)}"}), 500


# ==========================================
# ROUTING OWNER PANEL (DENGAN PIN: 11204)
# ==========================================
@app.route("/owner-login", methods=["GET", "POST"])
def owner_login():
    error = None
    if request.method == "POST":
        pin_input = request.form.get("pin")
        OWNER_PIN = os.environ.get("OWNER_PIN", "11204")
        if pin_input == OWNER_PIN:
            session["owner_logged"] = True
            return redirect(url_for("owner_dashboard"))
        else:
            error = "PIN Pendamping salah! Silakan coba lagi."
    return render_template("owner_login.html", error=error)


@app.route("/owner-dashboard")
def owner_dashboard():
    if not session.get("owner_logged"):
        return redirect(url_for("owner_login"))
    return render_template("owner.html", data=DATABASE_OWNER)


@app.route("/owner-logout")

def owner_logout():
    
    session.pop("owner_logged", None)
    return redirect(url_for("owner_login"))

# ==========================================
# API KOMUNIKASI OWNER -> PENGGUNA (MASALAH SERIUS)
# ==========================================
@app.route("/api/owner-kirim-pesan", methods=["POST"])
def owner_kirim_pesan():
    if not session.get("owner_logged"):
        return jsonify({"status": "error", "message": "Akses ditolak. Silakan login sebagai Owner."}), 403

    data = request.json or {}
    target_user = (data.get("target_user") or "Semua Pengguna / Darurat").strip()
    kontak_tujuan = (data.get("kontak_tujuan") or "-").strip()
    isi_pesan = (data.get("pesan") or "").strip()
    prioritas = (data.get("prioritas") or "PENDAMPINGAN SERIUS").strip()

    if not isi_pesan:
        return jsonify({"status": "error", "message": "Isi pesan ke pengguna tidak boleh kosong."}), 400

    entry = {
        "id": uuid.uuid4().hex[:8],
        "waktu": datetime.now().strftime("%d %B %Y - %H:%M:%S"),
        "target_user": target_user,
        "kontak_tujuan": kontak_tujuan,
        "prioritas": prioritas,
        "pesan": isi_pesan,
    }
    DATABASE_OWNER["balasan_owner"].insert(0, entry)

    return jsonify({
        "status": "success",
        "message": f"Pesan pendampingan Owner berhasil dikirimkan untuk '{target_user}'.",
        "data": entry,
    })


@app.route("/api/pesan-dari-owner", methods=["GET"])
def cek_pesan_dari_owner():
    nama_user = (request.args.get("user") or "").strip().lower()
    semua_balasan = DATABASE_OWNER.get("balasan_owner") or []

    if not nama_user or nama_user == "pengguna anonim":
        # Tampilkan pesan yang ditujukan ke pengguna anonim / semua pengguna
        cocok = [
            b for b in semua_balasan
            if b.get("target_user", "").lower() in ("pengguna anonim", "remaja sapabatin", "semua pengguna / darurat", "")
        ]
    else:
        cocok = [
            b for b in semua_balasan
            if b.get("target_user", "").lower() in (nama_user, "semua pengguna / darurat", "pengguna anonim")
        ]

    return jsonify({"status": "success", "pesan_owner": cocok})
# ==========================================
# MENJALANKAN SERVER FLASK
# ==========================================
if __name__ == "__main__":
    print("🚀 Server SapaBatin Berjalan di http://127.0.0.1:5000")
    app.run(debug=True, port=5000)