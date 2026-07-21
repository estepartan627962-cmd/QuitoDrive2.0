import hashlib
import os
import secrets
import sqlite3
import string
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st


APP_VERSION = "QuitoDrive v6.0 · Botones funcionales"
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "quitodrive_funcional.db"

st.set_page_config(
    page_title="QuitoDrive",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# DISEÑO MODERNO
# =========================================================
st.markdown(
    """
<style>
:root {
    color-scheme: dark;
}

html {
    scroll-behavior: smooth;
}

.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(115,115,115,.18), transparent 28%),
        radial-gradient(circle at 92% 24%, rgba(82,82,82,.16), transparent 25%),
        linear-gradient(145deg, #030303 0%, #0d0d0d 48%, #171717 100%);
    color: #ffffff;
}

[data-testid="stHeader"] {
    background: rgba(3,3,3,.72);
    backdrop-filter: blur(16px);
}

[data-testid="stSidebar"] {
    display: none;
}

.block-container {
    max-width: 1380px;
    padding-top: 5.5rem;
    padding-bottom: 4rem;
}

#MainMenu,
footer {
    visibility: hidden;
}

h1, h2, h3, h4, p, label, span {
    color: #ffffff;
}

.modern-nav {
    position: fixed;
    z-index: 9999;
    top: .65rem;
    left: 50%;
    transform: translateX(-50%);
    width: min(1120px, calc(100% - 2rem));
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: .75rem 1rem;
    border: 1px solid rgba(255,255,255,.13);
    border-radius: 999px;
    background: rgba(12,12,12,.84);
    backdrop-filter: blur(18px);
    box-shadow: 0 16px 50px rgba(0,0,0,.45);
}

.modern-brand {
    color: #ffffff !important;
    font-weight: 850;
    text-decoration: none;
}

.modern-links {
    display: flex;
    flex-wrap: wrap;
    gap: .35rem;
}

.modern-links a {
    color: #e5e5e5 !important;
    text-decoration: none;
    padding: .45rem .75rem;
    border-radius: 999px;
    font-size: .9rem;
}

.modern-links a:hover {
    background: #2a2a2a;
}

.hero {
    min-height: 68vh;
    display: flex;
    align-items: center;
    border: 1px solid rgba(255,255,255,.11);
    border-radius: 34px;
    padding: clamp(2rem, 6vw, 5rem);
    background:
        linear-gradient(100deg, rgba(0,0,0,.94), rgba(0,0,0,.38)),
        url("https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=1800&q=85");
    background-size: cover;
    background-position: center;
    box-shadow: 0 28px 80px rgba(0,0,0,.52);
}

.hero-content {
    max-width: 720px;
}

.hero-kicker {
    display: inline-block;
    padding: .42rem .8rem;
    border-radius: 999px;
    background: rgba(255,255,255,.1);
    border: 1px solid rgba(255,255,255,.15);
    color: #ededed;
    font-size: .88rem;
    margin-bottom: 1rem;
}

.hero h1 {
    font-size: clamp(3rem, 7vw, 6rem);
    line-height: .98;
    margin: 0 0 1.2rem;
    letter-spacing: -3px;
}

.hero p {
    max-width: 640px;
    color: #d4d4d4;
    font-size: clamp(1rem, 2vw, 1.2rem);
    line-height: 1.65;
}

.hero-actions {
    display: flex;
    flex-wrap: wrap;
    gap: .75rem;
    margin-top: 1.6rem;
}

.hero-button {
    display: inline-block;
    padding: .8rem 1.15rem;
    border-radius: 999px;
    font-weight: 780;
    text-decoration: none;
}

.hero-primary {
    background: #ffffff;
    color: #090909 !important;
}

.hero-secondary {
    background: rgba(255,255,255,.08);
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,.18);
}

.section-anchor {
    height: 1px;
    margin-top: 5rem;
    scroll-margin-top: 6rem;
}

.section-heading {
    margin: 1rem 0 1.5rem;
}

.section-heading small {
    color: #a3a3a3;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 750;
}

.section-heading h2 {
    margin: .45rem 0 .3rem;
    font-size: clamp(2rem, 4vw, 3.3rem);
    letter-spacing: -1.5px;
}

.section-heading p {
    color: #bdbdbd;
    max-width: 760px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #3a3a3a;
    border-radius: 22px;
    background: linear-gradient(145deg, #101010, #1a1a1a);
    box-shadow: 0 16px 38px rgba(0,0,0,.28);
}

[data-testid="stMetric"] {
    background: #121212;
    border: 1px solid #353535;
    border-radius: 18px;
    padding: 1rem;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: #ffffff;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background: #151515;
    color: #ffffff;
    border-color: #444444;
}

input, textarea {
    color: #ffffff !important;
}

.stButton > button,
.stFormSubmitButton > button {
    min-height: 2.9rem;
    border-radius: 999px;
    font-weight: 780;
    border: 1px solid #555555;
}

button[kind="primary"] {
    background: #ffffff;
    color: #050505;
    border: 0;
}

button[kind="secondary"] {
    background: #202020;
    color: #ffffff;
}

[data-testid="stAlert"] {
    background: #151515;
    color: #ffffff;
    border: 1px solid #3f3f3f;
    border-radius: 16px;
}

[data-testid="stDataFrame"] {
    border: 1px solid #3f3f3f;
    border-radius: 16px;
    overflow: hidden;
}

hr {
    border-color: #3b3b3b;
}

@media (max-width: 760px) {
    .modern-nav {
        border-radius: 22px;
        align-items: flex-start;
        gap: .5rem;
    }

    .modern-links {
        justify-content: flex-end;
    }

    .modern-links a {
        font-size: .77rem;
        padding: .34rem .48rem;
    }

    .block-container {
        padding-top: 7rem;
    }

    .hero {
        min-height: 60vh;
        padding: 2rem;
        border-radius: 24px;
    }

    .hero h1 {
        letter-spacing: -1.5px;
    }
}
</style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# CATÁLOGO
# =========================================================
CATEGORIES = [
    "Todos",
    "Automóvil",
    "SUV",
    "Camioneta",
    "4x4",
    "Alta gama",
    "Deportivo",
]

CARS = [
    {
        "marca": "Chevrolet", "modelo": "Sail", "placa": "QDA-1001",
        "color": "Blanco", "tipo": "Automóvil", "anio": 2023,
        "precio_dia": 38.00, "cilindraje": "1.5 L", "airbags": 2,
        "transmision": "Manual", "combustible": "Gasolina",
        "pasajeros": 5, "traccion": "4x2",
    },
    {
        "marca": "Kia", "modelo": "Picanto", "placa": "QDA-1002",
        "color": "Rojo", "tipo": "Automóvil", "anio": 2024,
        "precio_dia": 36.00, "cilindraje": "1.0 L", "airbags": 2,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 5, "traccion": "4x2",
    },
    {
        "marca": "Hyundai", "modelo": "Grand i10", "placa": "QDA-1003",
        "color": "Plata", "tipo": "Automóvil", "anio": 2023,
        "precio_dia": 37.00, "cilindraje": "1.2 L", "airbags": 2,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 5, "traccion": "4x2",
    },
    {
        "marca": "Toyota", "modelo": "Yaris", "placa": "QDA-1004",
        "color": "Azul", "tipo": "Automóvil", "anio": 2024,
        "precio_dia": 47.00, "cilindraje": "1.5 L", "airbags": 7,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 5, "traccion": "4x2",
    },
    {
        "marca": "Chevrolet", "modelo": "Tracker", "placa": "QSU-2001",
        "color": "Rojo", "tipo": "SUV", "anio": 2024,
        "precio_dia": 64.00, "cilindraje": "1.2 L Turbo", "airbags": 6,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 5, "traccion": "4x2",
    },
    {
        "marca": "Hyundai", "modelo": "Creta", "placa": "QSU-2002",
        "color": "Negro", "tipo": "SUV", "anio": 2023,
        "precio_dia": 60.00, "cilindraje": "1.5 L", "airbags": 6,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 5, "traccion": "4x2",
    },
    {
        "marca": "Kia", "modelo": "Seltos", "placa": "QSU-2003",
        "color": "Blanco", "tipo": "SUV", "anio": 2024,
        "precio_dia": 63.00, "cilindraje": "1.5 L", "airbags": 6,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 5, "traccion": "4x2",
    },
    {
        "marca": "Renault", "modelo": "Duster", "placa": "QSU-2004",
        "color": "Gris", "tipo": "SUV", "anio": 2023,
        "precio_dia": 58.00, "cilindraje": "1.3 L Turbo", "airbags": 4,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 5, "traccion": "4x2",
    },
    {
        "marca": "Chevrolet", "modelo": "D-Max", "placa": "QCM-3001",
        "color": "Plata", "tipo": "Camioneta", "anio": 2023,
        "precio_dia": 78.00, "cilindraje": "3.0 L Turbo Diésel",
        "airbags": 7, "transmision": "Manual", "combustible": "Diésel",
        "pasajeros": 5, "traccion": "4x4",
    },
    {
        "marca": "Toyota", "modelo": "Hilux", "placa": "QCM-3002",
        "color": "Blanco", "tipo": "Camioneta", "anio": 2024,
        "precio_dia": 85.00, "cilindraje": "2.8 L Turbo Diésel",
        "airbags": 7, "transmision": "Automática", "combustible": "Diésel",
        "pasajeros": 5, "traccion": "4x4",
    },
    {
        "marca": "Nissan", "modelo": "Frontier", "placa": "QCM-3003",
        "color": "Negro", "tipo": "Camioneta", "anio": 2023,
        "precio_dia": 82.00, "cilindraje": "2.5 L Turbo Diésel",
        "airbags": 6, "transmision": "Automática", "combustible": "Diésel",
        "pasajeros": 5, "traccion": "4x4",
    },
    {
        "marca": "Suzuki", "modelo": "Jimny", "placa": "Q4X-4001",
        "color": "Verde", "tipo": "4x4", "anio": 2024,
        "precio_dia": 76.00, "cilindraje": "1.5 L", "airbags": 6,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 4, "traccion": "4x4",
    },
    {
        "marca": "Toyota", "modelo": "Fortuner", "placa": "Q4X-4002",
        "color": "Blanco", "tipo": "4x4", "anio": 2024,
        "precio_dia": 110.00, "cilindraje": "2.7 L", "airbags": 7,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 7, "traccion": "4x4",
    },
    {
        "marca": "Mitsubishi", "modelo": "Montero Sport", "placa": "Q4X-4003",
        "color": "Gris", "tipo": "4x4", "anio": 2023,
        "precio_dia": 105.00, "cilindraje": "2.4 L Turbo Diésel",
        "airbags": 7, "transmision": "Automática", "combustible": "Diésel",
        "pasajeros": 7, "traccion": "4x4",
    },
    {
        "marca": "BMW", "modelo": "X3", "placa": "QAG-5001",
        "color": "Negro", "tipo": "Alta gama", "anio": 2024,
        "precio_dia": 165.00, "cilindraje": "2.0 L Turbo", "airbags": 6,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 5, "traccion": "AWD",
    },
    {
        "marca": "Mercedes-Benz", "modelo": "GLC", "placa": "QAG-5002",
        "color": "Blanco", "tipo": "Alta gama", "anio": 2024,
        "precio_dia": 180.00, "cilindraje": "2.0 L Turbo", "airbags": 7,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 5, "traccion": "AWD",
    },
    {
        "marca": "Audi", "modelo": "Q5", "placa": "QAG-5003",
        "color": "Azul", "tipo": "Alta gama", "anio": 2023,
        "precio_dia": 170.00, "cilindraje": "2.0 L Turbo", "airbags": 6,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 5, "traccion": "AWD",
    },
    {
        "marca": "Ford", "modelo": "Mustang", "placa": "QDP-6001",
        "color": "Rojo", "tipo": "Deportivo", "anio": 2023,
        "precio_dia": 220.00, "cilindraje": "2.3 L Turbo", "airbags": 8,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 4, "traccion": "Posterior",
    },
    {
        "marca": "Chevrolet", "modelo": "Camaro", "placa": "QDP-6002",
        "color": "Negro", "tipo": "Deportivo", "anio": 2022,
        "precio_dia": 215.00, "cilindraje": "2.0 L Turbo", "airbags": 8,
        "transmision": "Automática", "combustible": "Gasolina",
        "pasajeros": 4, "traccion": "Posterior",
    },
    {
        "marca": "Toyota", "modelo": "GR86", "placa": "QDP-6003",
        "color": "Azul", "tipo": "Deportivo", "anio": 2024,
        "precio_dia": 195.00, "cilindraje": "2.4 L", "airbags": 7,
        "transmision": "Manual", "combustible": "Gasolina",
        "pasajeros": 4, "traccion": "Posterior",
    },
]


# =========================================================
# BASE DE DATOS
# =========================================================
def connect():
    connection = sqlite3.connect(
        str(DB_PATH),
        timeout=30,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def init_db():
    connection = connect()
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            telefono TEXT NOT NULL,
            edad INTEGER NOT NULL CHECK (edad >= 18),
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            fecha_registro TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS autos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            placa TEXT UNIQUE NOT NULL,
            color TEXT NOT NULL,
            tipo TEXT NOT NULL,
            anio INTEGER NOT NULL,
            precio_dia REAL NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Disponible',
            cilindraje TEXT NOT NULL,
            airbags INTEGER NOT NULL,
            transmision TEXT NOT NULL,
            combustible TEXT NOT NULL,
            pasajeros INTEGER NOT NULL,
            traccion TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reservaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            usuario_id INTEGER NOT NULL,
            auto_id INTEGER NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            dias INTEGER NOT NULL,
            total REAL NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Confirmada',
            fecha_creacion TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (auto_id) REFERENCES autos(id)
        );
        """
    )

    connection.executemany(
        """
        INSERT INTO autos (
            marca, modelo, placa, color, tipo, anio, precio_dia, estado,
            cilindraje, airbags, transmision, combustible, pasajeros, traccion
        )
        VALUES (
            :marca, :modelo, :placa, :color, :tipo, :anio, :precio_dia, 'Disponible',
            :cilindraje, :airbags, :transmision, :combustible, :pasajeros, :traccion
        )
        ON CONFLICT(placa) DO UPDATE SET
            marca = excluded.marca,
            modelo = excluded.modelo,
            color = excluded.color,
            tipo = excluded.tipo,
            anio = excluded.anio,
            precio_dia = excluded.precio_dia,
            cilindraje = excluded.cilindraje,
            airbags = excluded.airbags,
            transmision = excluded.transmision,
            combustible = excluded.combustible,
            pasajeros = excluded.pasajeros,
            traccion = excluded.traccion
        """,
        CARS,
    )

    connection.commit()
    connection.close()


# =========================================================
# USUARIOS
# =========================================================
def password_hash(password, salt=None):
    if salt is None:
        salt = os.urandom(16)

    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        120_000,
    )
    return salt.hex(), key.hex()


def verify_password(password, salt_hex, saved_hash):
    salt = bytes.fromhex(salt_hex)
    _, current_hash = password_hash(password, salt)
    return secrets.compare_digest(current_hash, saved_hash)


def register_user(nombre, cedula, correo, telefono, edad, password):
    salt, saved_hash = password_hash(password)
    connection = connect()

    try:
        cursor = connection.execute(
            """
            INSERT INTO usuarios (
                nombre, cedula, correo, telefono, edad,
                salt, password_hash, fecha_registro
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nombre.strip(),
                cedula.strip(),
                correo.strip().lower(),
                telefono.strip(),
                int(edad),
                salt,
                saved_hash,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        connection.commit()

        user = connection.execute(
            "SELECT * FROM usuarios WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

        return True, dict(user)
    except sqlite3.IntegrityError:
        return False, "La cédula o el correo ya están registrados."
    finally:
        connection.close()


def login_user(correo, password):
    connection = connect()
    user = connection.execute(
        "SELECT * FROM usuarios WHERE correo = ?",
        (correo.strip().lower(),),
    ).fetchone()
    connection.close()

    if user and verify_password(
        password,
        user["salt"],
        user["password_hash"],
    ):
        return dict(user)

    return None


# =========================================================
# VEHÍCULOS
# =========================================================
def car_image(car):
    filename = f"{car['placa']}.jpg"

    possible_paths = [
        BASE_DIR / "imagenes_autos" / filename,
        BASE_DIR / filename,
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    return "https://placehold.co/1200x675/151515/FFFFFF?text=Imagen+no+disponible"


def list_cars(vehicle_type="Todos", search=""):
    connection = connect()
    sql = "SELECT * FROM autos WHERE 1 = 1"
    parameters = []

    if vehicle_type != "Todos":
        sql += " AND tipo = ?"
        parameters.append(vehicle_type)

    if search.strip():
        search_value = f"%{search.strip().lower()}%"
        sql += """
            AND (
                lower(marca) LIKE ?
                OR lower(modelo) LIKE ?
                OR lower(placa) LIKE ?
                OR lower(color) LIKE ?
            )
        """
        parameters.extend(
            [
                search_value,
                search_value,
                search_value,
                search_value,
            ]
        )

    sql += " ORDER BY tipo, precio_dia"
    rows = connection.execute(sql, parameters).fetchall()
    connection.close()

    return [dict(row) for row in rows]


def get_car(car_id):
    if car_id is None:
        return None

    connection = connect()
    row = connection.execute(
        "SELECT * FROM autos WHERE id = ?",
        (car_id,),
    ).fetchone()
    connection.close()

    return dict(row) if row else None


def reserved_periods(car_id):
    connection = connect()
    rows = connection.execute(
        """
        SELECT fecha_inicio, fecha_fin
        FROM reservaciones
        WHERE auto_id = ?
          AND estado IN ('Confirmada', 'Pendiente')
          AND date(fecha_fin) >= date(?)
        ORDER BY date(fecha_inicio)
        """,
        (car_id, date.today().isoformat()),
    ).fetchall()
    connection.close()

    return [dict(row) for row in rows]


def is_available(car_id, start, end):
    connection = connect()
    conflict = connection.execute(
        """
        SELECT 1
        FROM reservaciones
        WHERE auto_id = ?
          AND estado IN ('Confirmada', 'Pendiente')
          AND NOT (
              date(fecha_fin) < date(?)
              OR date(fecha_inicio) > date(?)
          )
        LIMIT 1
        """,
        (
            car_id,
            start.isoformat(),
            end.isoformat(),
        ),
    ).fetchone()
    connection.close()

    return conflict is None


def availability_rows(car_id, days=30):
    periods = reserved_periods(car_id)
    result = []

    for offset in range(days):
        current_date = date.today() + timedelta(days=offset)
        occupied = any(
            date.fromisoformat(period["fecha_inicio"])
            <= current_date
            <= date.fromisoformat(period["fecha_fin"])
            for period in periods
        )

        result.append(
            {
                "Fecha": current_date.strftime("%d/%m/%Y"),
                "Estado": "Reservado" if occupied else "Disponible",
            }
        )

    return result


# =========================================================
# RESERVACIONES
# =========================================================
def reservation_code():
    random_part = "".join(
        secrets.choice(
            string.ascii_uppercase + string.digits
        )
        for _ in range(6)
    )
    return f"QDR-{datetime.now().strftime('%Y%m%d')}-{random_part}"


def save_reservation(user_id, car_id, start, end, days, total):
    if not is_available(car_id, start, end):
        return False, "El vehículo ya está reservado durante ese periodo."

    code = reservation_code()
    connection = connect()

    try:
        connection.execute("BEGIN IMMEDIATE")

        conflict = connection.execute(
            """
            SELECT 1
            FROM reservaciones
            WHERE auto_id = ?
              AND estado IN ('Confirmada', 'Pendiente')
              AND NOT (
                  date(fecha_fin) < date(?)
                  OR date(fecha_inicio) > date(?)
              )
            LIMIT 1
            """,
            (
                car_id,
                start.isoformat(),
                end.isoformat(),
            ),
        ).fetchone()

        if conflict:
            connection.rollback()
            return False, "El vehículo acaba de ser reservado para esas fechas."

        connection.execute(
            """
            INSERT INTO reservaciones (
                codigo, usuario_id, auto_id, fecha_inicio,
                fecha_fin, dias, total, estado, fecha_creacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Confirmada', ?)
            """,
            (
                code,
                user_id,
                car_id,
                start.isoformat(),
                end.isoformat(),
                days,
                total,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )

        connection.commit()
        return True, code
    except sqlite3.Error:
        connection.rollback()
        return False, "No se pudo guardar la reservación."
    finally:
        connection.close()


def user_reservations(user_id):
    connection = connect()
    rows = connection.execute(
        """
        SELECT
            r.*,
            a.marca,
            a.modelo,
            a.placa,
            a.color,
            a.tipo,
            a.cilindraje,
            a.airbags
        FROM reservaciones r
        JOIN autos a ON a.id = r.auto_id
        WHERE r.usuario_id = ?
        ORDER BY r.id DESC
        """,
        (user_id,),
    ).fetchall()
    connection.close()

    return [dict(row) for row in rows]


# =========================================================
# ESTADO
# =========================================================
init_db()

defaults = {
    "user": None,
    "show_register": False,
    "selected_car_id": None,
    "booking_open": False,
    "last_code": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CABECERA ESTÁTICA
# =========================================================
st.html(
    """
<div class="modern-nav">
    <a class="modern-brand" href="#inicio">🚗 QuitoDrive</a>
    <div class="modern-links">
        <a href="#inicio">Inicio</a>
        <a href="#login">Cuenta</a>
        <a href="#catalogo">Catálogo</a>
        <a href="#reservaciones">Reservaciones</a>
    </div>
</div>
"""
)

st.html('<div id="inicio" class="section-anchor"></div>')

st.html(
    """
<section class="hero">
    <div class="hero-content">
        <span class="hero-kicker">Movilidad premium en Quito</span>
        <h1>Tu próximo auto empieza aquí.</h1>
        <p>
            Explora vehículos, revisa sus características,
            consulta fechas disponibles y confirma tu reservación.
        </p>
        <div class="hero-actions">
            <a class="hero-button hero-primary" href="#login">Iniciar sesión</a>
            <a class="hero-button hero-secondary" href="#catalogo">Ver catálogo</a>
        </div>
    </div>
</section>
"""
)

metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("Vehículos", len(CARS))
metric_2.metric("Categorías", len(CATEGORIES) - 1)
metric_3.metric("Proceso", "100% digital")


# =========================================================
# SECCIONES INTERACTIVAS
# Un fragmento evita que cada clic recargue toda la página.
# =========================================================
@st.fragment
def interactive_sections():
    # -----------------------------------------------------
    # 2. CUENTA
    # -----------------------------------------------------
    st.html('<div id="login" class="section-anchor"></div>')
    st.html(
        """
<div class="section-heading">
    <small>02 · Tu cuenta</small>
    <h2>Inicia sesión o crea una cuenta</h2>
    <p>Accede para confirmar reservas y consultar tu historial.</p>
</div>
"""
    )

    if st.session_state.user:
        with st.container(border=True):
            st.success(
                f"Sesión iniciada como {st.session_state.user['nombre']}."
            )
            account_1, account_2 = st.columns([2, 1])

            with account_1:
                st.write(
                    f"**Correo:** {st.session_state.user['correo']}"
                )

            with account_2:
                if st.button(
                    "Cerrar sesión",
                    key="logout_button",
                    use_container_width=True,
                ):
                    st.session_state.user = None
                    st.session_state.last_code = None
                    st.rerun(scope="fragment")
    else:
        login_column, benefits_column = st.columns([1, 1])

        with login_column:
            with st.container(border=True):
                st.subheader("Iniciar sesión")

                with st.form(
                    "login_form",
                    clear_on_submit=False,
                ):
                    login_email = st.text_input(
                        "Correo electrónico",
                        key="login_email",
                    )
                    login_password = st.text_input(
                        "Contraseña",
                        type="password",
                        key="login_password",
                    )
                    login_submit = st.form_submit_button(
                        "Ingresar",
                        type="primary",
                        use_container_width=True,
                    )

                if login_submit:
                    user = login_user(
                        login_email,
                        login_password,
                    )

                    if user:
                        st.session_state.user = user
                        st.session_state.show_register = False
                        st.toast(
                            "Inicio de sesión correcto.",
                            icon="✅",
                        )
                        st.rerun(scope="fragment")
                    else:
                        st.error(
                            "Correo o contraseña incorrectos."
                        )

                if st.button(
                    "Crear cuenta",
                    key="toggle_register_button",
                    use_container_width=True,
                ):
                    st.session_state.show_register = (
                        not st.session_state.show_register
                    )

        with benefits_column:
            with st.container(border=True):
                st.subheader("Beneficios")
                st.write("✓ Guarda tus reservaciones")
                st.write("✓ Consulta códigos de confirmación")
                st.write("✓ Revisa periodos ocupados")
                st.write("✓ Accede desde cualquier dispositivo")

        if st.session_state.show_register:
            with st.container(border=True):
                st.subheader("Crear una cuenta")

                with st.form(
                    "register_form",
                    clear_on_submit=False,
                ):
                    register_1, register_2 = st.columns(2)

                    with register_1:
                        name = st.text_input(
                            "Nombre completo",
                            key="register_name",
                        )
                        identification = st.text_input(
                            "Cédula",
                            key="register_id",
                        )
                        phone = st.text_input(
                            "Teléfono",
                            key="register_phone",
                        )

                    with register_2:
                        email = st.text_input(
                            "Correo",
                            key="register_email",
                        )
                        age = st.number_input(
                            "Edad",
                            min_value=18,
                            max_value=100,
                            value=18,
                            key="register_age",
                        )
                        password = st.text_input(
                            "Contraseña",
                            type="password",
                            key="register_password",
                        )

                    confirm_password = st.text_input(
                        "Confirmar contraseña",
                        type="password",
                        key="register_confirm",
                    )
                    terms = st.checkbox(
                        "Confirmo que soy mayor de 18 años.",
                        key="register_terms",
                    )
                    register_submit = st.form_submit_button(
                        "Crear cuenta",
                        type="primary",
                        use_container_width=True,
                    )

                if register_submit:
                    if not all(
                        [
                            name.strip(),
                            identification.strip(),
                            phone.strip(),
                            email.strip(),
                            password,
                        ]
                    ):
                        st.error("Completa todos los campos.")
                    elif "@" not in email or "." not in email:
                        st.error("Ingresa un correo válido.")
                    elif len(password) < 8:
                        st.error(
                            "La contraseña debe tener al menos 8 caracteres."
                        )
                    elif password != confirm_password:
                        st.error(
                            "Las contraseñas no coinciden."
                        )
                    elif not terms:
                        st.error(
                            "Debes confirmar que eres mayor de edad."
                        )
                    else:
                        success, result = register_user(
                            name,
                            identification,
                            email,
                            phone,
                            age,
                            password,
                        )

                        if success:
                            st.session_state.user = result
                            st.session_state.show_register = False
                            st.toast(
                                "Cuenta creada correctamente.",
                                icon="✅",
                            )
                            st.rerun(scope="fragment")
                        else:
                            st.error(result)

    # -----------------------------------------------------
    # 3. CATÁLOGO
    # -----------------------------------------------------
    st.html('<div id="catalogo" class="section-anchor"></div>')
    st.html(
        """
<div class="section-heading">
    <small>03 · Catálogo</small>
    <h2>Encuentra el vehículo ideal</h2>
    <p>
        Filtra por categoría, revisa las fotografías y selecciona
        el vehículo que deseas reservar.
    </p>
</div>
"""
    )

    filter_column, search_column = st.columns(2)

    with filter_column:
        selected_type = st.selectbox(
            "Categoría",
            CATEGORIES,
            key="catalog_type",
        )

    with search_column:
        search_text = st.text_input(
            "Buscar por marca, modelo, placa o color",
            key="catalog_search",
        )

    cars = list_cars(
        selected_type,
        search_text,
    )

    st.caption(
        f"{len(cars)} vehículos encontrados."
    )

    catalog_columns = st.columns(3)

    for index, car in enumerate(cars):
        with catalog_columns[index % 3]:
            with st.container(border=True):
                st.image(
                    car_image(car),
                    use_container_width=True,
                )
                st.subheader(
                    f"{car['marca']} {car['modelo']}"
                )
                st.caption(
                    f"{car['tipo']} · Año {car['anio']}"
                )

                detail_1, detail_2 = st.columns(2)

                with detail_1:
                    st.write(
                        f"**Color:** {car['color']}"
                    )
                    st.write(
                        f"**Cilindraje:** {car['cilindraje']}"
                    )

                with detail_2:
                    st.write(
                        f"**Airbags:** {car['airbags']}"
                    )
                    st.write(
                        f"**Precio:** ${car['precio_dia']:.2f}/día"
                    )

                selected = (
                    st.session_state.selected_car_id
                    == car["id"]
                )

                if st.button(
                    (
                        "✓ Vehículo seleccionado"
                        if selected
                        else "Seleccionar vehículo"
                    ),
                    key=f"select_car_{car['id']}",
                    type=(
                        "primary"
                        if selected
                        else "secondary"
                    ),
                    use_container_width=True,
                ):
                    st.session_state.selected_car_id = car["id"]
                    st.session_state.booking_open = False

    selected_car = get_car(
        st.session_state.selected_car_id
    )

    if selected_car:
        st.subheader("Vehículo seleccionado")

        selected_image, selected_details = st.columns(
            [1.25, 1]
        )

        with selected_image:
            st.image(
                car_image(selected_car),
                use_container_width=True,
            )

        with selected_details:
            with st.container(border=True):
                st.subheader(
                    f"{selected_car['marca']} "
                    f"{selected_car['modelo']}"
                )

                characteristic_1, characteristic_2 = st.columns(2)

                with characteristic_1:
                    st.write(
                        f"**Color:** {selected_car['color']}"
                    )
                    st.write(
                        f"**Año:** {selected_car['anio']}"
                    )
                    st.write(
                        f"**Placa:** {selected_car['placa']}"
                    )
                    st.write(
                        f"**Pasajeros:** {selected_car['pasajeros']}"
                    )

                with characteristic_2:
                    st.write(
                        f"**Cilindraje:** "
                        f"{selected_car['cilindraje']}"
                    )
                    st.write(
                        f"**Airbags:** {selected_car['airbags']}"
                    )
                    st.write(
                        f"**Transmisión:** "
                        f"{selected_car['transmision']}"
                    )
                    st.write(
                        f"**Tracción:** "
                        f"{selected_car['traccion']}"
                    )

                st.metric(
                    "Precio por día",
                    f"${selected_car['precio_dia']:.2f}",
                )

                if st.button(
                    "Reservar este vehículo",
                    key="open_booking_button",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state.booking_open = True

        with st.expander(
            "Consultar disponibilidad de los próximos 30 días"
        ):
            st.dataframe(
                availability_rows(
                    selected_car["id"],
                    30,
                ),
                use_container_width=True,
                hide_index=True,
            )

    # -----------------------------------------------------
    # 4. RESERVACIONES
    # -----------------------------------------------------
    st.html('<div id="reservaciones" class="section-anchor"></div>')
    st.html(
        """
<div class="section-heading">
    <small>04 · Reservaciones</small>
    <h2>Confirma tu próxima experiencia</h2>
    <p>
        Selecciona las fechas y guarda la reservación.
        Tus registros aparecen en esta misma sección.
    </p>
</div>
"""
    )

    if selected_car and st.session_state.booking_open:
        with st.container(border=True):
            st.subheader(
                f"Reservar {selected_car['marca']} "
                f"{selected_car['modelo']}"
            )

            with st.form(
                "reservation_form",
                clear_on_submit=False,
            ):
                date_1, date_2 = st.columns(2)

                with date_1:
                    start_date = st.date_input(
                        "Fecha de inicio",
                        min_value=date.today(),
                        value=date.today(),
                    )

                with date_2:
                    end_date = st.date_input(
                        "Fecha de devolución",
                        min_value=start_date,
                        value=start_date,
                    )

                days = (end_date - start_date).days + 1
                total = days * selected_car["precio_dia"]
                available = is_available(
                    selected_car["id"],
                    start_date,
                    end_date,
                )

                summary_1, summary_2 = st.columns(2)
                summary_1.metric("Días", days)
                summary_2.metric("Total", f"${total:.2f}")

                license_confirm = st.checkbox(
                    "Tengo licencia de conducir vigente."
                )
                documents_confirm = st.checkbox(
                    "Presentaré cédula y documentos requeridos."
                )

                reservation_submit = st.form_submit_button(
                    "Confirmar y guardar reservación",
                    type="primary",
                    disabled=not available,
                    use_container_width=True,
                )

            if available:
                st.success(
                    "El vehículo está disponible para esas fechas."
                )
            else:
                st.error(
                    "El vehículo ya tiene una reserva durante ese periodo."
                )

            if reservation_submit:
                if not st.session_state.user:
                    st.error(
                        "Primero debes iniciar sesión o crear una cuenta."
                    )
                elif (
                    not license_confirm
                    or not documents_confirm
                ):
                    st.error(
                        "Debes confirmar los dos requisitos."
                    )
                else:
                    success, result = save_reservation(
                        st.session_state.user["id"],
                        selected_car["id"],
                        start_date,
                        end_date,
                        days,
                        total,
                    )

                    if success:
                        st.session_state.last_code = result
                        st.session_state.booking_open = False
                        st.toast(
                            "Reservación guardada.",
                            icon="✅",
                        )
                    else:
                        st.error(result)
    else:
        st.info(
            "Selecciona un vehículo y presiona "
            "“Reservar este vehículo”."
        )

    if st.session_state.user:
        if st.session_state.last_code:
            st.success(
                "Tu reservación fue guardada correctamente."
            )
            st.code(
                st.session_state.last_code,
                language=None,
            )

        reservations = user_reservations(
            st.session_state.user["id"]
        )

        st.subheader("Mis reservaciones")

        if not reservations:
            st.info(
                "Todavía no tienes reservaciones."
            )
        else:
            for reservation in reservations:
                with st.expander(
                    f"{reservation['codigo']} · "
                    f"{reservation['marca']} "
                    f"{reservation['modelo']}"
                ):
                    reservation_image, reservation_data = st.columns(
                        [1, 1.35]
                    )

                    with reservation_image:
                        st.image(
                            car_image(reservation),
                            use_container_width=True,
                        )

                    with reservation_data:
                        st.write(
                            f"**Código:** {reservation['codigo']}"
                        )
                        st.write(
                            f"**Periodo:** "
                            f"{reservation['fecha_inicio']} "
                            f"al {reservation['fecha_fin']}"
                        )
                        st.write(
                            f"**Color:** {reservation['color']}"
                        )
                        st.write(
                            f"**Cilindraje:** "
                            f"{reservation['cilindraje']}"
                        )
                        st.write(
                            f"**Airbags:** {reservation['airbags']}"
                        )
                        st.write(
                            f"**Días:** {reservation['dias']}"
                        )
                        st.write(
                            f"**Total:** "
                            f"${reservation['total']:.2f}"
                        )
                        st.write(
                            f"**Estado:** {reservation['estado']}"
                        )
    else:
        st.caption(
            "Inicia sesión para visualizar tus reservaciones."
        )


interactive_sections()

st.divider()
st.caption(
    f"{APP_VERSION} · Python + Streamlit + SQLite"
)
