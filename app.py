import os
import sqlite3

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)

##########################################################
# Flask
##########################################################

app = Flask(__name__)

app.secret_key = "indic2deutsch_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, "users.db")

##########################################################
# NLLB MODEL
##########################################################

print("Loading NLLB Model...")

MODEL_NAME = "facebook/nllb-200-distilled-600M"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

device = "cuda" if torch.cuda.is_available() else "cpu"

model.to(device)
print("Using device:", device)

print("Model Loaded Successfully!")

##########################################################
# Indian Languages
##########################################################

LANGUAGES = {

    "English":"eng_Latn",

    "Hindi":"hin_Deva",

    "Telugu":"tel_Telu",

    "Tamil":"tam_Taml",

    "Kannada":"kan_Knda",

    "Malayalam":"mal_Mlym",

    "Marathi":"mar_Deva",

    "Gujarati":"guj_Gujr",

    "Bengali":"ben_Beng",

    "Punjabi":"pan_Guru",

    "Urdu":"urd_Arab",

    "Odia":"ory_Orya",

    "Assamese":"asm_Beng",

    "Nepali":"npi_Deva",

    "Kashmiri":"kas_Arab",

    "Sindhi":"snd_Arab",

    "Sanskrit":"san_Deva",

    "Maithili":"mai_Deva"

}
TARGET_LANGUAGES = {

    "English":"eng_Latn",
    "German":"deu_Latn",
    "French":"fra_Latn",
    "Spanish":"spa_Latn",
    "Italian":"ita_Latn",
    "Portuguese":"por_Latn",
    "Russian":"rus_Cyrl",
    "Japanese":"jpn_Jpan",
    "Korean":"kor_Hang",
    "Chinese":"zho_Hans",
    "Arabic":"arb_Arab",

    "Hindi":"hin_Deva",
    "Telugu":"tel_Telu",
    "Tamil":"tam_Taml",
    "Kannada":"kan_Knda",
    "Malayalam":"mal_Mlym",
    "Marathi":"mar_Deva",
    "Gujarati":"guj_Gujr",
    "Bengali":"ben_Beng",
    "Punjabi":"pan_Guru",
    "Urdu":"urd_Arab",
    "Odia":"ory_Orya",
    "Assamese":"asm_Beng",
    "Nepali":"npi_Deva",
    "Kashmiri":"kas_Arab",
    "Sindhi":"snd_Arab",
    "Sanskrit":"san_Deva",
    "Maithili":"mai_Deva"

}
##########################################################
# Database
##########################################################

def get_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        email TEXT UNIQUE,

        password TEXT

    )

    """)
    try:
        conn.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    except:
        pass

    try:
        conn.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    except:
        pass

    try:
        conn.execute("ALTER TABLE users ADD COLUMN designation TEXT")
    except:
        pass

    try:
        conn.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")
    except:
        pass

    try:
        conn.execute("ALTER TABLE users ADD COLUMN joined_date TEXT")
    except:
        pass

    cur.execute("""

    CREATE TABLE IF NOT EXISTS history(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        email TEXT,

        source_language TEXT,

        input_text TEXT,

        translated_text TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    conn.commit()

    conn.close()

init_db()

##########################################################
# Translation Function
##########################################################

def translate_text(text, source_language, target_language):

    src = LANGUAGES[source_language]

    tgt = TARGET_LANGUAGES[target_language]

    tokenizer.src_lang = src

    encoded = tokenizer(
        text,
        return_tensors="pt"
    ).to(device)

    generated = model.generate(

        **encoded,

        forced_bos_token_id=tokenizer.convert_tokens_to_ids(
            tgt
        ),

        max_length=512

    )

    result = tokenizer.batch_decode(
        generated,
        skip_special_tokens=True
    )[0]

    return result

##########################################################
# HOME
##########################################################

@app.route("/")

def home():

   return render_template(
    "index.html",
    languages=LANGUAGES.keys(),
    target_languages=TARGET_LANGUAGES.keys(),
    translated_text="",
    input_text=""
)

##########################################################
# REGISTER
##########################################################

@app.route("/register", methods=["GET","POST"])

def register():

    if request.method=="POST":

        username=request.form["username"]

        email=request.form["email"]

        password=generate_password_hash(

            request.form["password"]

        )

        conn=get_connection()

        cur=conn.cursor()

        try:

            cur.execute(

                """

                INSERT INTO users

                (username,email,password)

                VALUES(?,?,?)

                """,

                (username,email,password)

            )

            conn.commit()

            flash("Registration Successful")

            return redirect(url_for("login"))

        except:

            flash("Email Already Exists")

        finally:

            conn.close()

    return render_template("register.html")

##########################################################
# LOGIN
##########################################################

@app.route("/login", methods=["GET","POST"])

def login():

    if request.method=="POST":

        email=request.form["email"]

        password=request.form["password"]

        conn=get_connection()

        user=conn.execute(

            "SELECT * FROM users WHERE email=?",

            (email,)

        ).fetchone()

        conn.close()

        if user and check_password_hash(

            user["password"],

            password

        ):

            session["user"]=user["email"]

            session["username"]=user["username"]

            return redirect(url_for("home"))

        flash("Invalid Credentials")

    return render_template("login.html")
##########################################################
# TRANSLATE
##########################################################

@app.route("/translate", methods=["POST"])
def translate():

    if "user" not in session:
        return redirect(url_for("login"))

    source_language = request.form["source_language"]
    target_language = request.form["target_language"]
    input_text = request.form["input_text"]

    translated = translate_text(
        input_text,
        source_language,
        target_language
    )

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO history
        (
            email,
            source_language,
            input_text,
            translated_text
        )
        VALUES(?,?,?,?)
        """,
        (
            session["user"],
            source_language,
            input_text,
            translated
        )
    )

    conn.commit()
    conn.close()

    return render_template(
    "index.html",
    languages=LANGUAGES.keys(),
    target_languages=TARGET_LANGUAGES.keys(),
    input_text=input_text,
    translated_text=translated
)


##########################################################
# PROFILE
##########################################################

@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()

    total = conn.execute(
        """
        SELECT COUNT(*)
        FROM history
        WHERE email=?
        """,
        (session["user"],)
    ).fetchone()[0]

    voice_total = 0

    return render_template(
        "profile.html",
        username=session["username"],
        email=session["user"],
        total=total,
        voice_total=voice_total
    )
from werkzeug.utils import secure_filename
import os
from datetime import datetime

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/edit_profile", methods=["GET","POST"])
def edit_profile():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()

    if request.method == "POST":

        username = request.form["username"]
        full_name = request.form["full_name"]
        phone = request.form["phone"]
        designation = request.form["designation"]

        filename = None

        file = request.files.get("profile_pic")

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            conn.execute("""
            UPDATE users
            SET username=?,
                full_name=?,
                phone=?,
                designation=?,
                profile_pic=?
            WHERE email=?
            """,
            (
                username,
                full_name,
                phone,
                designation,
                filename,
                session["user"]
            ))

        else:

            conn.execute("""
            UPDATE users
            SET username=?,
                full_name=?,
                phone=?,
                designation=?
            WHERE email=?
            """,
            (
                username,
                full_name,
                phone,
                designation,
                session["user"]
            ))

        conn.commit()

        session["username"] = username

        conn.close()

        return redirect(url_for("profile"))

    user = conn.execute(
        "SELECT * FROM users WHERE email=?",
        (session["user"],)
    ).fetchone()

    conn.close()

    return render_template(
        "edit_profile.html",
        username=user["username"],
        full_name=user["full_name"],
        phone=user["phone"],
        designation=user["designation"],
        email=user["email"],
        profile_pic=user["profile_pic"]
    )

@app.route("/change_password", methods=["GET", "POST"])
def change_password():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # Save password changes
        return redirect(url_for("profile"))

    return render_template("change_password.html")

##########################################################
# HISTORY
##########################################################

@app.route("/history")
def history():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()

    rows = conn.execute(

        """
        SELECT *
        FROM history
        WHERE email=?
        ORDER BY id DESC
        """,

        (session["user"],)

    ).fetchall()

    conn.close()

    return render_template(

        "history.html",

        rows=rows

    )


##########################################################
# DELETE HISTORY
##########################################################

@app.route("/delete/<int:id>")
def delete(id):

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()

    conn.execute(

        """
        DELETE FROM history
        WHERE id=?
        """,

        (id,)

    )

    conn.commit()

    conn.close()

    flash("History Deleted")

    return redirect(url_for("history"))


##########################################################
# VOICE PAGE
##########################################################

@app.route("/voice")
def voice():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("voice.html")
from flask import jsonify

@app.route("/voice_translate", methods=["POST"])
def voice_translate():

    data = request.get_json()

    print(data)

    text = data["text"]
    target_language = data["target_language"]

    translated = translate_text(
        text,
        "English",
        target_language
    )

    print("Translation =", translated)

    return jsonify({
        "translation": translated
    })
##########################################################
# SETTINGS
##########################################################

@app.route("/settings")
def settings():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("settings.html")
##########################################################
# LOGOUT
##########################################################

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully")

    return redirect(url_for("login"))

##########################################################
# DOWNLOAD
##########################################################

@app.route("/download/<int:id>")
def download(id):

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()

    row = conn.execute(

        """
        SELECT *
        FROM history
        WHERE id=?
        """,

        (id,)

    ).fetchone()

    conn.close()

    if row is None:

        flash("Translation Not Found")

        return redirect(url_for("history"))

    filename = f"translation_{id}.txt"

    with open(filename, "w", encoding="utf-8") as f:

        f.write("Indic2Deutsch\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Language : {row['source_language']}\n\n")
        f.write("Input:\n")
        f.write(row["input_text"])
        f.write("\n\n")
        f.write("German Translation:\n")
        f.write(row["translated_text"])

    from flask import send_file

    return send_file(
        filename,
        as_attachment=True
    )


##########################################################
# MAIN
##########################################################

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )