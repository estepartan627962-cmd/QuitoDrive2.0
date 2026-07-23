import hashlib
import os
import secrets
import sqlite3
import string
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote

import requests
import streamlit as st

DB = "quitodrive.db"
BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="QuitoDrive",
    page_icon="🚗",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');

    :root {
        color-scheme: dark;
        --qd-bg: #07090f;
        --qd-panel: rgba(18, 22, 34, .78);
        --qd-panel-strong: #121622;
        --qd-line: rgba(255, 255, 255, .10);
        --qd-text: #f7f8fc;
        --qd-muted: #a8afc3;
        --qd-cyan: #21d4fd;
        --qd-violet: #8b5cf6;
        --qd-pink: #f472b6;
        --qd-success: #39e58c;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        color: var(--qd-text);
        background:
            radial-gradient(circle at 12% 5%, rgba(33, 212, 253, .15), transparent 25%),
            radial-gradient(circle at 88% 12%, rgba(139, 92, 246, .18), transparent 28%),
            radial-gradient(circle at 55% 95%, rgba(244, 114, 182, .08), transparent 24%),
            linear-gradient(145deg, #05070c 0%, #0a0e18 55%, #090b12 100%);
        background-attachment: fixed;
    }

    .block-container {
        max-width: 1440px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    [data-testid="stHeader"] {
        background: rgba(7, 9, 15, .72);
        backdrop-filter: blur(18px);
        border-bottom: 1px solid rgba(255, 255, 255, .06);
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(15, 19, 31, .98), rgba(7, 9, 15, .98));
        border-right: 1px solid var(--qd-line);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.1rem;
    }

    [data-testid="stSidebar"] * {
        color: var(--qd-text);
    }

    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--qd-text);
        letter-spacing: -.025em;
    }

    p, label, span, div {
        color: inherit;
    }

    .qd-brand {
        padding: 1rem 1rem 1.1rem;
        margin-bottom: 1rem;
        border: 1px solid var(--qd-line);
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(33,212,253,.12), rgba(139,92,246,.12));
        box-shadow: 0 18px 45px rgba(0,0,0,.25);
    }

    .qd-brand-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.45rem;
        font-weight: 800;
        margin: 0;
    }

    .qd-brand-subtitle {
        color: var(--qd-muted);
        font-size: .78rem;
        margin-top: .22rem;
        letter-spacing: .08em;
        text-transform: uppercase;
    }

    .qd-hero {
        position: relative;
        overflow: hidden;
        min-height: 330px;
        padding: 3.2rem 3rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--qd-line);
        border-radius: 30px;
        background:
            linear-gradient(105deg, rgba(9,12,20,.96) 5%, rgba(9,12,20,.72) 55%, rgba(9,12,20,.25) 100%),
            url('https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1800&q=85') center/cover;
        box-shadow: 0 28px 80px rgba(0,0,0,.38);
    }

    .qd-hero::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(130deg, transparent 45%, rgba(33,212,253,.10), rgba(139,92,246,.14));
        pointer-events: none;
    }

    .qd-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        padding: .48rem .8rem;
        border: 1px solid rgba(255,255,255,.14);
        border-radius: 999px;
        background: rgba(255,255,255,.07);
        backdrop-filter: blur(12px);
        color: #dce5ff;
        font-size: .76rem;
        font-weight: 700;
        letter-spacing: .08em;
        text-transform: uppercase;
    }

    .qd-hero h1 {
        position: relative;
        z-index: 1;
        max-width: 720px;
        margin: 1rem 0 .75rem;
        font-size: clamp(2.5rem, 5vw, 4.9rem);
        line-height: .96;
        font-weight: 800;
    }

    .qd-gradient-text {
        background: linear-gradient(90deg, var(--qd-cyan), #c4b5fd 55%, var(--qd-pink));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .qd-hero p {
        position: relative;
        z-index: 1;
        max-width: 620px;
        margin: 0;
        color: #cbd2e3;
        font-size: 1.05rem;
        line-height: 1.7;
    }

    .qd-section-head {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 1rem;
        margin: 1.5rem 0 .8rem;
    }

    .qd-section-head h2 {
        margin: 0;
        font-size: 2rem;
    }

    .qd-section-head p {
        margin: .25rem 0 0;
        color: var(--qd-muted);
    }

    .qd-anchor-button {
        display: block;
        width: 100%;
        padding: .85rem 1rem;
        margin-top: .75rem;
        border: 1px solid rgba(33,212,253,.36);
        border-radius: 14px;
        background: linear-gradient(90deg, rgba(33,212,253,.18), rgba(139,92,246,.22));
        color: #ffffff !important;
        font-weight: 800;
        text-align: center;
        text-decoration: none !important;
        transition: transform .2s ease, border-color .2s ease;
    }

    .qd-anchor-button:hover {
        transform: translateY(-2px);
        border-color: rgba(33,212,253,.7);
    }

    .qd-scroll-nav a {
        display: block;
        padding: .68rem .8rem;
        margin: .35rem 0;
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 12px;
        background: rgba(255,255,255,.035);
        color: #dce5ff !important;
        text-decoration: none !important;
        font-weight: 700;
    }

    .qd-scroll-nav a:hover {
        background: rgba(33,212,253,.09);
        border-color: rgba(33,212,253,.28);
    }

    .qd-pill {
        display: inline-flex;
        padding: .42rem .72rem;
        border: 1px solid rgba(33,212,253,.28);
        border-radius: 999px;
        background: rgba(33,212,253,.08);
        color: #9aeaff;
        font-size: .74rem;
        font-weight: 700;
        white-space: nowrap;
    }

    [data-testid="stMetric"] {
        min-height: 118px;
        padding: 1.15rem 1.2rem;
        border: 1px solid var(--qd-line);
        border-radius: 22px;
        background: linear-gradient(145deg, rgba(20,25,39,.88), rgba(11,14,23,.88));
        box-shadow: 0 14px 35px rgba(0,0,0,.20);
        transition: transform .2s ease, border-color .2s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: rgba(33,212,253,.28);
    }

    [data-testid="stMetricLabel"] {
        color: var(--qd-muted);
        font-size: .82rem;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: var(--qd-text);
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        overflow: hidden;
        border: 1px solid var(--qd-line);
        border-radius: 24px;
        background: linear-gradient(150deg, rgba(19,24,37,.86), rgba(10,13,21,.92));
        box-shadow: 0 16px 42px rgba(0,0,0,.22);
        transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-3px);
        border-color: rgba(139,92,246,.32);
        box-shadow: 0 22px 55px rgba(0,0,0,.30);
    }

    [data-testid="stImage"] img {
        border-radius: 18px;
        object-fit: cover;
        max-height: 255px;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    [data-testid="stNumberInput"] > div > div {
        min-height: 48px;
        border: 1px solid var(--qd-line) !important;
        border-radius: 14px !important;
        background: rgba(15,19,30,.88) !important;
        color: var(--qd-text) !important;
        box-shadow: none !important;
    }

    input, textarea {
        color: var(--qd-text) !important;
        background: transparent !important;
    }

    input::placeholder, textarea::placeholder {
        color: #737b91 !important;
    }

    [data-testid="stForm"] {
        padding: 1.45rem;
        border: 1px solid var(--qd-line);
        border-radius: 24px;
        background: rgba(13,17,27,.78);
        box-shadow: 0 18px 50px rgba(0,0,0,.22);
    }

    .stButton > button,
    .stFormSubmitButton > button {
        min-height: 46px;
        border-radius: 14px;
        font-weight: 800;
        letter-spacing: .01em;
        transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        transform: translateY(-2px);
    }

    button[kind="primary"] {
        border: 0;
        color: #050711;
        background: linear-gradient(90deg, var(--qd-cyan), #a78bfa 52%, var(--qd-pink));
        box-shadow: 0 12px 28px rgba(98, 120, 255, .22);
    }

    button[kind="secondary"] {
        border: 1px solid var(--qd-line);
        color: var(--qd-text);
        background: rgba(255,255,255,.045);
    }

    button[kind="secondary"]:hover {
        border-color: rgba(33,212,253,.35);
        background: rgba(33,212,253,.07);
    }

    [role="radiogroup"] {
        gap: .45rem;
    }

    [role="radiogroup"] label {
        padding: .62rem .72rem;
        border: 1px solid transparent;
        border-radius: 12px;
    }

    [role="radiogroup"] label:hover {
        border-color: var(--qd-line);
        background: rgba(255,255,255,.045);
    }

    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: .45rem;
        padding: .35rem;
        border: 1px solid var(--qd-line);
        border-radius: 16px;
        background: rgba(11,14,22,.72);
    }

    [data-testid="stTabs"] button[role="tab"] {
        border-radius: 12px;
        padding: .7rem 1rem;
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
        background: linear-gradient(90deg, rgba(33,212,253,.14), rgba(139,92,246,.16));
    }

    [data-testid="stAlert"] {
        border: 1px solid var(--qd-line);
        border-radius: 16px;
        background: rgba(16,20,31,.88);
    }

    [data-testid="stDataFrame"] {
        overflow: hidden;
        border: 1px solid var(--qd-line);
        border-radius: 16px;
    }

    details {
        border: 1px solid var(--qd-line) !important;
        border-radius: 18px !important;
        background: rgba(13,17,27,.72) !important;
    }

    hr {
        border-color: rgba(255,255,255,.08);
    }

    .qd-step {
        min-height: 148px;
        padding: 1.25rem;
    }

    .qd-step-number {
        width: 42px;
        height: 42px;
        display: grid;
        place-items: center;
        margin-bottom: .8rem;
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(33,212,253,.18), rgba(139,92,246,.22));
        color: #dff8ff;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 800;
    }

    .qd-step-title {
        margin-bottom: .25rem;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.08rem;
        font-weight: 700;
    }

    .qd-step-text {
        color: var(--qd-muted);
        line-height: 1.55;
    }

    .qd-login-note {
        padding: 1rem 1.1rem;
        border: 1px solid rgba(33,212,253,.16);
        border-radius: 16px;
        background: rgba(33,212,253,.055);
        color: #cdefff;
        font-size: .9rem;
    }

    @media (max-width: 800px) {
        .block-container { padding: 1rem .9rem 3rem; }
        .qd-hero { min-height: 300px; padding: 2.2rem 1.35rem; border-radius: 22px; }
        .qd-hero h1 { font-size: 2.65rem; }
        .qd-section-head { align-items: flex-start; flex-direction: column; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

CATEGORIES = {
    "Automóvil": ("🚗", "Económico y práctico para Quito.",
                  "Chevrolet Sail, Kia Picanto, Hyundai Grand i10 y Toyota Yaris"),
    "SUV": ("🚙", "Espacioso para ciudad y carretera.",
            "Chevrolet Tracker, Hyundai Creta, Kia Seltos y Renault Duster"),
    "Camioneta": ("🛻", "Útil para trabajo, carga y viajes.",
                  "Chevrolet D-Max, Toyota Hilux y Nissan Frontier"),
    "4x4": ("⛰️", "Preparado para caminos difíciles.",
            "Suzuki Jimny, Toyota Fortuner y Mitsubishi Montero Sport"),
    "Alta gama": ("✨", "Confort, tecnología y presentación ejecutiva.",
                  "BMW X3, Mercedes-Benz GLC y Audi Q5"),
    "Deportivo": ("🏎️", "Diseño deportivo y alto desempeño.",
                  "Ford Mustang, Chevrolet Camaro y Toyota GR86"),
}

# Placas y precios ficticios.
CARS = [
    ("Chevrolet", "Sail", "QDA-1001", "Blanco", "Automóvil", 2000, 38.0),
    ("Kia", "Picanto", "QDA-1002", "Rojo", "Automóvil", 2024, 36.0),
    ("Hyundai", "Grand i10", "QDA-1003", "Plata", "Automóvil", 2023, 37.0),
    ("Toyota", "Yaris", "QDA-1004", "Azul", "Automóvil", 2024, 47.0),
    ("Chevrolet", "Tracker", "QSU-2001", "Rojo", "SUV", 2024, 64.0),
    ("Hyundai", "Creta", "QSU-2002", "Negro", "SUV", 2023, 60.0),
    ("Kia", "Seltos", "QSU-2003", "Blanco", "SUV", 2024, 63.0),
    ("Renault", "Duster", "QSU-2004", "Gris", "SUV", 2023, 58.0),
    ("Chevrolet", "D-Max", "QCM-3001", "Plata", "Camioneta", 2023, 78.0),
    ("Toyota", "Hilux", "QCM-3002", "Blanco", "Camioneta", 2024, 85.0),
    ("Nissan", "Frontier", "QCM-3003", "Negro", "Camioneta", 2023, 82.0),
    ("Suzuki", "Jimny", "Q4X-4001", "Verde", "4x4", 2024, 76.0),
    ("Toyota", "Fortuner", "Q4X-4002", "Blanco", "4x4", 2024, 110.0),
    ("Mitsubishi", "Montero Sport", "Q4X-4003", "Gris", "4x4", 2023, 105.0),
    ("BMW", "X3", "QAG-5001", "Negro", "Alta gama", 2024, 165.0),
    ("Mercedes-Benz", "GLC", "QAG-5002", "Blanco", "Alta gama", 2024, 180.0),
    ("Audi", "Q5", "QAG-5003", "Azul", "Alta gama", 2023, 170.0),
    ("Ford", "Mustang", "QDP-6001", "Rojo", "Deportivo", 2023, 220.0),
    ("Chevrolet", "Camaro", "QDP-6002", "Negro", "Deportivo", 2022, 215.0),
    ("Toyota", "GR86", "QDP-6003", "Azul", "Deportivo", 2024, 195.0),
]

DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def connect():
    con = sqlite3.connect(DB, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con


def init_db():
    con = connect()
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS usuarios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            telefono TEXT NOT NULL,
            edad INTEGER NOT NULL CHECK(edad>=18),
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS autos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            placa TEXT UNIQUE NOT NULL,
            color TEXT NOT NULL,
            tipo TEXT NOT NULL,
            anio INTEGER NOT NULL,
            precio_dia REAL NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Disponible'
        );

        CREATE TABLE IF NOT EXISTS reservaciones(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            usuario_id INTEGER NOT NULL,
            auto_id INTEGER NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            dias INTEGER NOT NULL,
            total REAL NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Confirmada',
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY(auto_id) REFERENCES autos(id)
        );
        """
    )
    con.executemany(
        """
        INSERT OR IGNORE INTO autos
        (marca,modelo,placa,color,tipo,anio,precio_dia)
        VALUES(?,?,?,?,?,?,?)
        """,
        CARS,
    )
    con.commit()
    con.close()


def password_hash(password, salt=None):
    salt = salt or os.urandom(16)
    result = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return salt.hex(), result.hex()


def register_user(nombre, cedula, correo, telefono, edad, password):
    salt, saved_hash = password_hash(password)
    con = connect()
    try:
        con.execute(
            """
            INSERT INTO usuarios(nombre,cedula,correo,telefono,edad,salt,password_hash)
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                nombre.strip(),
                cedula.strip(),
                correo.strip().lower(),
                telefono.strip(),
                int(edad),
                salt,
                saved_hash,
            ),
        )
        con.commit()
        return True, "Usuario registrado correctamente."
    except sqlite3.IntegrityError:
        return False, "La cédula o el correo ya están registrados."
    finally:
        con.close()


def login_user(correo, password):
    con = connect()
    user = con.execute(
        "SELECT * FROM usuarios WHERE correo=?",
        (correo.strip().lower(),),
    ).fetchone()
    con.close()

    if not user:
        return None

    _, current_hash = password_hash(password, bytes.fromhex(user["salt"]))
    if secrets.compare_digest(current_hash, user["password_hash"]):
        return dict(user)
    return None


@st.cache_data(ttl=86400, show_spinner=False)
def car_image(marca, modelo, placa=None):
    # Prioriza las fotografías originales entregadas para QuitoDrive.
    if placa:
        for extension in (".jpg", ".jpeg", ".png", ".webp"):
            filename = f"{placa}{extension}"
            possible_paths = (
                BASE_DIR / "imagenes_autos" / filename,
                BASE_DIR / filename,
            )
            for image_path in possible_paths:
                if image_path.exists():
                    return str(image_path)

    # Se conserva la conexión externa original únicamente como respaldo.
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"{marca} {modelo} automobile",
        "gsrnamespace": 6,
        "gsrlimit": 5,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 900,
        "origin": "*",
    }
    try:
        response = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "QuitoDrive-Demo/1.0"},
            timeout=10,
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [])
            if info:
                return info[0].get("thumburl") or info[0].get("url")
    except requests.RequestException:
        pass

    name = quote(f"{marca} {modelo}")
    return f"https://placehold.co/900x550/171717/ffffff?text={name}"


def list_cars(vehicle_type="Todos", search=""):
    con = connect()
    sql = "SELECT * FROM autos WHERE 1=1"
    params = []

    if vehicle_type != "Todos":
        sql += " AND tipo=?"
        params.append(vehicle_type)

    if search.strip():
        value = f"%{search.strip().lower()}%"
        sql += """
            AND(
                lower(marca) LIKE ? OR lower(modelo) LIKE ?
                OR lower(placa) LIKE ? OR lower(color) LIKE ?
            )
        """
        params.extend([value, value, value, value])

    sql += " ORDER BY tipo,precio_dia"
    rows = con.execute(sql, params).fetchall()
    con.close()
    return [dict(row) for row in rows]


def get_car(car_id):
    if car_id is None:
        return None
    con = connect()
    row = con.execute("SELECT * FROM autos WHERE id=?", (car_id,)).fetchone()
    con.close()
    return dict(row) if row else None


def reserved_periods(car_id):
    con = connect()
    rows = con.execute(
        """
        SELECT fecha_inicio,fecha_fin
        FROM reservaciones
        WHERE auto_id=?
          AND estado IN('Confirmada','Pendiente')
          AND date(fecha_fin)>=date(?)
        ORDER BY date(fecha_inicio)
        """,
        (car_id, date.today().isoformat()),
    ).fetchall()
    con.close()
    return [dict(row) for row in rows]


def car_available(car_id, start, end):
    con = connect()
    conflict = con.execute(
        """
        SELECT 1 FROM reservaciones
        WHERE auto_id=?
          AND estado IN('Confirmada','Pendiente')
          AND NOT(date(fecha_fin)<date(?) OR date(fecha_inicio)>date(?))
        LIMIT 1
        """,
        (car_id, start.isoformat(), end.isoformat()),
    ).fetchone()
    con.close()
    return conflict is None


def availability(car_id):
    periods = reserved_periods(car_id)
    result = []

    for offset in range(30):
        current = date.today() + timedelta(days=offset)
        occupied = any(
            date.fromisoformat(p["fecha_inicio"])
            <= current
            <= date.fromisoformat(p["fecha_fin"])
            for p in periods
        )
        result.append(
            {
                "Fecha": current.strftime("%d/%m/%Y"),
                "Día": DAYS[current.weekday()],
                "Estado": "Ocupado" if occupied else "Disponible",
            }
        )
    return result


def create_code():
    random_part = "".join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(6)
    )
    return f"QDR-{datetime.now().strftime('%Y%m%d')}-{random_part}"


def save_reservation(user_id, car_id, start, end, days, total):
    if not car_available(car_id, start, end):
        return False, "El vehículo ya está reservado para esas fechas."

    code = create_code()
    con = connect()
    try:
        con.execute(
            """
            INSERT INTO reservaciones(
                codigo,usuario_id,auto_id,fecha_inicio,fecha_fin,dias,total,estado
            )
            VALUES(?,?,?,?,?,?,?,'Confirmada')
            """,
            (
                code,
                user_id,
                car_id,
                start.isoformat(),
                end.isoformat(),
                days,
                total,
            ),
        )
        con.commit()
        return True, code
    finally:
        con.close()


def my_reservations(user_id):
    con = connect()
    rows = con.execute(
        """
        SELECT r.*,a.marca,a.modelo,a.placa,a.color,a.tipo,a.anio
        FROM reservaciones r
        JOIN autos a ON a.id=r.auto_id
        WHERE r.usuario_id=?
        ORDER BY r.id DESC
        """,
        (user_id,),
    ).fetchall()
    con.close()
    return [dict(row) for row in rows]


def page_heading(title, subtitle, badge="QuitoDrive"):
    st.markdown(
        f"""
        <div class="qd-section-head">
            <div>
                <span class="qd-pill">{badge}</span>
                <h2>{title}</h2>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_anchor(anchor_id):
    st.markdown(
        f'<div id="{anchor_id}" style="scroll-margin-top:80px;"></div>',
        unsafe_allow_html=True,
    )


def show_car(car):
    st.image(
        car_image(car["marca"], car["modelo"], car["placa"]),
        caption=f"{car['marca']} {car['modelo']} — imagen referencial",
        use_container_width=True,
    )

    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;gap:.8rem;align-items:start;margin:.2rem 0 .7rem;">
            <div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:1.25rem;font-weight:800;line-height:1.15;">
                    {car['marca']} {car['modelo']}
                </div>
                <div style="color:#a8afc3;font-size:.86rem;margin-top:.25rem;">
                    {car['tipo']} · {car['anio']} · {car['color']}
                </div>
            </div>
            <span class="qd-pill">Disponible</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    c1.caption("PLACA")
    c1.markdown(f"**{car['placa']}**")
    c2.caption("PRECIO DIARIO")
    c2.markdown(f"**${car['precio_dia']:.2f}**")


def selected_car_panel(car):
    st.divider()
    page_heading(
        "Configura tu reservación",
        "Consulta disponibilidad, selecciona fechas y confirma en pocos pasos.",
        "Vehículo seleccionado",
    )

    photo, details = st.columns([1.3, 1], gap="large")

    with photo:
        st.image(
            car_image(car["marca"], car["modelo"], car["placa"]),
            caption=f"{car['marca']} {car['modelo']} — imagen referencial",
            use_container_width=True,
        )

    with details:
        with st.container(border=True):
            st.markdown(f"### {car['marca']} {car['modelo']}")
            st.caption(f"{car['tipo']} · Año {car['anio']}")

            d1, d2 = st.columns(2)
            d1.metric("Precio diario", f"${car['precio_dia']:.2f}")
            d2.metric("Estado", car["estado"])

            st.write(f"**Placa:** {car['placa']}")
            st.write(f"**Color:** {car['color']}")
            st.markdown(
                '<div class="qd-login-note">Reserva segura, confirmación inmediata y disponibilidad validada en tiempo real.</div>',
                unsafe_allow_html=True,
            )

    tab_dates, tab_reserve = st.tabs(
        ["📅 Fechas disponibles", "⚡ Realizar reservación"]
    )

    with tab_dates:
        st.caption("Disponibilidad proyectada para los próximos 30 días")
        st.dataframe(
            availability(car["id"]),
            use_container_width=True,
            hide_index=True,
        )

        periods = reserved_periods(car["id"])
        if periods:
            st.warning("Periodos actualmente ocupados")
            for period in periods:
                st.write(f"• {period['fecha_inicio']} al {period['fecha_fin']}")
        else:
            st.success("Este vehículo no tiene reservaciones futuras.")

    with tab_reserve:
        if not st.session_state.user:
            st.warning("Debes iniciar sesión para completar la reservación.")
            st.markdown(
                '<a class="qd-anchor-button" href="#acceso">Ir a iniciar sesión</a>',
                unsafe_allow_html=True,
            )
            return

        st.markdown("#### Selecciona el periodo")
        c1, c2 = st.columns(2)
        with c1:
            start = st.date_input(
                "Fecha de inicio",
                min_value=date.today(),
                value=date.today(),
                key=f"start_{car['id']}",
            )
        with c2:
            end = st.date_input(
                "Fecha de devolución",
                min_value=start,
                value=start,
                key=f"end_{car['id']}",
            )

        days = (end - start).days + 1
        total = days * car["precio_dia"]
        available_now = car_available(car["id"], start, end)

        if available_now:
            st.success("El vehículo está disponible en el periodo seleccionado.")
        else:
            st.error("El vehículo ya está ocupado en ese periodo.")

        m1, m2, m3 = st.columns(3)
        m1.metric("Días", days)
        m2.metric("Tarifa diaria", f"${car['precio_dia']:.2f}")
        m3.metric("Total", f"${total:.2f}")

        st.markdown("#### Requisitos")
        license_ok = st.checkbox(
            "Tengo licencia de conducir vigente.",
            key=f"license_{car['id']}",
        )
        documents_ok = st.checkbox(
            "Presentaré cédula y documentos requeridos.",
            key=f"documents_{car['id']}",
        )

        if st.button(
            "Confirmar reservación",
            type="primary",
            use_container_width=True,
            disabled=not available_now,
        ):
            if not license_ok or not documents_ok:
                st.error("Confirma los dos requisitos antes de continuar.")
            else:
                ok, result = save_reservation(
                    st.session_state.user["id"],
                    car["id"],
                    start,
                    end,
                    days,
                    total,
                )
                if ok:
                    st.success("Reservación confirmada correctamente.")
                    st.caption("Código de reservación")
                    st.code(result, language=None)
                    st.balloons()
                else:
                    st.error(result)


def home():
    section_anchor("inicio")
    st.markdown(
        """
        <section class="qd-hero">
            <span class="qd-eyebrow">● Movilidad premium en Quito</span>
            <h1>Tu próximo auto está a <span class="qd-gradient-text">un clic.</span></h1>
            <p>Explora vehículos, valida fechas y confirma tu reservación en una experiencia rápida, segura y completamente digital.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Flota disponible", len(list_cars()), "vehículos")
    m2.metric("Categorías", len(CATEGORIES), "opciones")
    m3.metric("Proceso", "100%", "en línea")
    m4.metric("Confirmación", "Inmediata", "sin llamadas")

    page_heading(
        "Reserva sin complicaciones",
        "Un flujo simple, transparente y diseñado para ahorrar tiempo.",
        "Cómo funciona",
    )

    steps = [
        ("01", "Crea tu cuenta", "Regístrate con tus datos y accede a todas las funciones."),
        ("02", "Elige tu vehículo", "Compara categorías, modelos, precios y disponibilidad."),
        ("03", "Selecciona fechas", "Consulta los próximos 30 días y evita cruces de reservas."),
        ("04", "Confirma", "Recibe inmediatamente tu código único de reservación."),
    ]
    cols = st.columns(4)
    for col, (number, title, description) in zip(cols, steps):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="qd-step">
                        <div class="qd-step-number">{number}</div>
                        <div class="qd-step-title">{title}</div>
                        <div class="qd-step-text">{description}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    page_heading(
        "Encuentra el vehículo ideal",
        "Desde opciones urbanas hasta modelos premium y todoterreno.",
        "Nuestra flota",
    )
    category_cols = st.columns(3)
    for index, (name, data) in enumerate(CATEGORIES.items()):
        icon, description, models = data
        with category_cols[index % 3]:
            with st.container(border=True):
                st.markdown(f"### {icon} {name}")
                st.write(description)
                st.caption(models)

    st.info("Servicio disponible para mayores de 18 años con licencia de conducir vigente.")


def catalog():
    section_anchor("catalogo")
    page_heading(
        "Catálogo de vehículos",
        "Filtra, compara y selecciona el auto que encaja con tu ruta.",
        "Explora la flota",
    )

    with st.expander("Ver guía de categorías"):
        cols = st.columns(3)
        for index, (name, data) in enumerate(CATEGORIES.items()):
            icon, description, models = data
            with cols[index % 3]:
                with st.container(border=True):
                    st.markdown(f"### {icon} {name}")
                    st.write(description)
                    st.caption(models)

    with st.container(border=True):
        st.markdown("#### Buscar vehículo")
        f1, f2 = st.columns([1, 1.7])
        with f1:
            vehicle_type = st.selectbox(
                "Tipo de vehículo",
                ["Todos", *CATEGORIES.keys()],
            )
        with f2:
            search = st.text_input(
                "Buscar",
                placeholder="Marca, modelo, placa o color...",
            )

    cars = list_cars(vehicle_type, search)
    st.markdown(
        f'<div style="margin:1rem 0;color:#a8afc3;"><strong style="color:#f7f8fc;">{len(cars)}</strong> vehículos encontrados</div>',
        unsafe_allow_html=True,
    )

    if not cars:
        st.warning("No encontramos vehículos con esos filtros.")
        return

    cols = st.columns(3)
    for index, car in enumerate(cars):
        with cols[index % 3]:
            with st.container(border=True):
                show_car(car)

                selected = st.session_state.selected_car_id == car["id"]
                if st.button(
                    "✓ Vehículo seleccionado" if selected else "Seleccionar vehículo",
                    key=f"select_{car['id']}",
                    type="primary" if selected else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.selected_car_id = car["id"]
                    st.rerun()

    car = get_car(st.session_state.selected_car_id)
    if car:
        selected_car_panel(car)


def register():
    section_anchor("registro")
    page_heading(
        "Crear cuenta",
        "Regístrate para reservar vehículos y administrar tus solicitudes.",
        "Nuevo usuario",
    )

    left, form_col, right = st.columns([.55, 1.4, .55])
    with form_col:
        with st.form("register_form"):
            st.markdown("### Datos personales")
            nombre = st.text_input("Nombre completo", placeholder="Ej. Juan Pérez")
            c1, c2 = st.columns(2)
            with c1:
                cedula = st.text_input("Cédula", placeholder="10 dígitos")
                telefono = st.text_input("Teléfono", placeholder="09XXXXXXXX")
                edad = st.number_input("Edad", 18, 100, 18)
            with c2:
                correo = st.text_input("Correo electrónico", placeholder="correo@ejemplo.com")
                password = st.text_input("Contraseña", type="password")
                confirm = st.text_input("Confirmar contraseña", type="password")

            terms = st.checkbox("Soy mayor de 18 años y acepto las condiciones.")
            submit = st.form_submit_button(
                "Crear mi cuenta",
                type="primary",
                use_container_width=True,
            )

        if submit:
            if not all([nombre, cedula, correo, telefono, password]):
                st.error("Completa todos los campos obligatorios.")
            elif "@" not in correo or "." not in correo:
                st.error("Ingresa un correo electrónico válido.")
            elif len(password) < 8:
                st.error("La contraseña debe tener al menos 8 caracteres.")
            elif password != confirm:
                st.error("Las contraseñas no coinciden.")
            elif not terms:
                st.error("Debes aceptar las condiciones.")
            else:
                ok, message = register_user(
                    nombre, cedula, correo, telefono, edad, password
                )
                st.success(message) if ok else st.error(message)


def login():
    section_anchor("acceso")
    page_heading(
        "Bienvenido de vuelta",
        "Inicia sesión para reservar y consultar tus solicitudes.",
        "Acceso seguro",
    )

    left, form_col, right = st.columns([.75, 1.1, .75])
    with form_col:
        with st.form("login_form"):
            st.markdown("### Iniciar sesión")
            correo = st.text_input(
                "Correo electrónico",
                placeholder="correo@ejemplo.com",
            )
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button(
                "Ingresar a QuitoDrive",
                type="primary",
                use_container_width=True,
            )

        st.markdown(
            '<div class="qd-login-note">Tus credenciales se validan de forma segura para proteger tu cuenta y tus reservaciones.</div>',
            unsafe_allow_html=True,
        )

        if submit:
            user = login_user(correo, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Correo o contraseña incorrectos.")


def reservations():
    section_anchor("reservaciones")
    page_heading(
        "Mis reservaciones",
        "Consulta el historial y los detalles de tus vehículos reservados.",
        "Panel personal",
    )
    rows = my_reservations(st.session_state.user["id"])

    if not rows:
        st.info("Todavía no tienes reservaciones. Visita el catálogo para comenzar.")
        st.markdown(
            '<a class="qd-anchor-button" href="#catalogo">Explorar vehículos</a>',
            unsafe_allow_html=True,
        )
        return

    total_value = sum(row["total"] for row in rows)
    m1, m2, m3 = st.columns(3)
    m1.metric("Reservaciones", len(rows))
    m2.metric("Valor acumulado", f"${total_value:.2f}")
    m3.metric("Último estado", rows[0]["estado"])

    for row in rows:
        with st.expander(
            f"{row['codigo']}  ·  {row['marca']} {row['modelo']}  ·  {row['estado']}"
        ):
            c1, c2 = st.columns([1, 1.3], gap="large")
            with c1:
                st.image(
                    car_image(row["marca"], row["modelo"], row["placa"]),
                    caption="Imagen referencial",
                    use_container_width=True,
                )
            with c2:
                st.markdown(f"### {row['marca']} {row['modelo']}")
                st.caption(f"{row['tipo']} · Año {row['anio']} · {row['color']}")
                r1, r2 = st.columns(2)
                r1.metric("Días", row["dias"])
                r2.metric("Total", f"${row['total']:.2f}")
                st.write(f"**Placa:** {row['placa']}")
                st.write(f"**Periodo:** {row['fecha_inicio']} al {row['fecha_fin']}")
                st.write(f"**Estado:** {row['estado']}")


def main():
    init_db()

    st.session_state.setdefault("user", None)
    st.session_state.setdefault("selected_car_id", None)

    with st.sidebar:
        st.markdown(
            """
            <div class="qd-brand">
                <div class="qd-brand-title">🚗 QuitoDrive</div>
                <div class="qd-brand-subtitle">Move smart. Drive free.</div>
            </div>
            <div class="qd-scroll-nav">
                <a href="#inicio">01 · Inicio</a>
                <a href="#catalogo">02 · Catálogo</a>
                <a href="#acceso">03 · Acceso</a>
                <a href="#registro">04 · Registro</a>
                <a href="#reservaciones">05 · Reservaciones</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        if st.session_state.user:
            st.success(f"Hola, {st.session_state.user['nombre']}")
            if st.button("Cerrar sesión", use_container_width=True):
                st.session_state.user = None
                st.rerun()
        else:
            st.info("Desplázate hacia abajo para iniciar sesión o registrarte.")

        st.caption("Reservaciones digitales · Atención en Quito")

    home()
    st.divider()
    catalog()
    st.divider()

    if st.session_state.user:
        section_anchor("acceso")
        st.success("Tu sesión está activa. Puedes reservar directamente desde el vehículo seleccionado.")
        section_anchor("registro")
        st.caption("El registro no se muestra porque ya tienes una sesión iniciada.")
    else:
        login()
        st.divider()
        register()

    st.divider()
    if st.session_state.user:
        reservations()
    else:
        section_anchor("reservaciones")
        page_heading(
            "Mis reservaciones",
            "Inicia sesión para consultar tu historial y los detalles de tus reservas.",
            "Panel personal",
        )
        st.info("Esta sección estará disponible cuando inicies sesión.")


if __name__ == "__main__":
    main()

