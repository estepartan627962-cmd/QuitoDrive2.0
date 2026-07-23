import hashlib
import os
import secrets
import string
from datetime import date, datetime, timedelta
from urllib.parse import quote

import psycopg2
import psycopg2.extras
import requests
import streamlit as st

# Conexión PostgreSQL — ajusta puerto, usuario y contraseña.
PG_HOST = os.getenv("PGHOST", "144.217.15.162")
PG_PORT = int(os.getenv("PGPORT", "7732"))
PG_USER = os.getenv("PGUSER", "tad")
PG_PASSWORD = os.getenv("PGPASSWORD", "tad")
PG_DATABASE = os.getenv("PGDATABASE", "quitodrive")

DB_CONFIG = {
    "host": PG_HOST,
    "port": PG_PORT,
    "user": PG_USER,
    "password": PG_PASSWORD,
    "dbname": PG_DATABASE,
}

SCHEMA = {
    "usuarios": {
        "id": "SERIAL PRIMARY KEY",
        "nombre": "TEXT NOT NULL",
        "cedula": "TEXT UNIQUE NOT NULL",
        "correo": "TEXT UNIQUE NOT NULL",
        "telefono": "TEXT NOT NULL",
        "edad": "INTEGER NOT NULL CHECK (edad >= 18)",
        "salt": "TEXT NOT NULL",
        "password_hash": "TEXT NOT NULL",
    },
    "autos": {
        "id": "SERIAL PRIMARY KEY",
        "marca": "TEXT NOT NULL",
        "modelo": "TEXT NOT NULL",
        "placa": "TEXT UNIQUE NOT NULL",
        "color": "TEXT NOT NULL",
        "tipo": "TEXT NOT NULL",
        "anio": "INTEGER NOT NULL",
        "precio_dia": "DOUBLE PRECISION NOT NULL",
        "estado": "TEXT NOT NULL DEFAULT 'Disponible'",
    },
    "reservaciones": {
        "id": "SERIAL PRIMARY KEY",
        "codigo": "TEXT UNIQUE NOT NULL",
        "usuario_id": "INTEGER NOT NULL REFERENCES usuarios(id)",
        "auto_id": "INTEGER NOT NULL REFERENCES autos(id)",
        "fecha_inicio": "DATE NOT NULL",
        "fecha_fin": "DATE NOT NULL",
        "dias": "INTEGER NOT NULL",
        "total": "DOUBLE PRECISION NOT NULL",
        "estado": "TEXT NOT NULL DEFAULT 'Confirmada'",
    },
}

st.set_page_config(
    page_title="QuitoDrive",
    page_icon="🚗",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root{color-scheme:dark}
    .stApp{background:linear-gradient(135deg,#050505,#111,#202020);color:#fff}
    [data-testid="stHeader"]{background:rgba(5,5,5,.92)}
    [data-testid="stSidebar"]{background:#080808;border-right:1px solid #333}
    [data-testid="stSidebar"] *{color:#fff}
    h1,h2,h3,h4,p,label,span{color:#fff}
    [data-testid="stMetric"]{background:#151515;border:1px solid #3a3a3a;border-radius:15px;padding:14px}
    [data-testid="stMetricLabel"],[data-testid="stMetricValue"]{color:#fff}
    [data-testid="stVerticalBlockBorderWrapper"]{
        background:linear-gradient(145deg,#111,#1c1c1c);
        border:1px solid #3b3b3b;
        border-radius:18px
    }
    div[data-baseweb="select"]>div,
    div[data-baseweb="input"]>div,
    div[data-baseweb="textarea"]>div{background:#171717;color:#fff;border-color:#555}
    input,textarea{background:#171717!important;color:#fff!important}
    button[kind="primary"]{background:linear-gradient(90deg,#6b7280,#d1d5db);color:#050505;border:0;font-weight:800}
    button[kind="secondary"]{background:#222;color:#fff;border:1px solid #555;font-weight:700}
    [data-testid="stAlert"]{background:#171717;color:#fff;border:1px solid #4a4a4a}
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
    return psycopg2.connect(**DB_CONFIG)


def table_exists(cur, table_name):
    cur.execute(
        """
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = %s
        """,
        (table_name,),
    )
    return cur.fetchone() is not None


def column_exists(cur, table_name, column_name):
    cur.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
          AND column_name = %s
        """,
        (table_name, column_name),
    )
    return cur.fetchone() is not None


def ensure_table(cur, table_name, columns):
    if table_exists(cur, table_name):
        for column_name, definition in columns.items():
            if column_exists(cur, table_name, column_name):
                continue
            # En tablas existentes solo se agregan columnas faltantes.
            # No se recrea PRIMARY KEY ni se tocan campos ya presentes.
            add_definition = (
                definition.replace("PRIMARY KEY", "")
                .replace("primary key", "")
                .strip()
            )
            cur.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {add_definition}"
            )
        return

    column_sql = ", ".join(
        f"{name} {definition}" for name, definition in columns.items()
    )
    cur.execute(f"CREATE TABLE {table_name} ({column_sql})")


def init_db():
    con = connect()
    try:
        with con.cursor() as cur:
            for table_name, columns in SCHEMA.items():
                ensure_table(cur, table_name, columns)

            cur.executemany(
                """
                INSERT INTO autos
                    (marca, modelo, placa, color, tipo, anio, precio_dia)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (placa) DO NOTHING
                """,
                CARS,
            )
        con.commit()
    finally:
        con.close()


def password_hash(password, salt=None):
    salt = salt or os.urandom(16)
    result = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return salt.hex(), result.hex()


def register_user(nombre, cedula, correo, telefono, edad, password):
    salt, saved_hash = password_hash(password)
    con = connect()
    try:
        with con.cursor() as cur:
            cur.execute(
                """
                INSERT INTO usuarios
                    (nombre, cedula, correo, telefono, edad, salt, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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
    except psycopg2.IntegrityError:
        con.rollback()
        return False, "La cédula o el correo ya están registrados."
    finally:
        con.close()


def login_user(correo, password):
    con = connect()
    try:
        with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM usuarios WHERE correo = %s",
                (correo.strip().lower(),),
            )
            user = cur.fetchone()
    finally:
        con.close()

    if not user:
        return None

    _, current_hash = password_hash(password, bytes.fromhex(user["salt"]))
    if secrets.compare_digest(current_hash, user["password_hash"]):
        return dict(user)
    return None


@st.cache_data(ttl=86400, show_spinner=False)
def car_image(marca, modelo):
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
        sql += " AND tipo = %s"
        params.append(vehicle_type)

    if search.strip():
        value = f"%{search.strip().lower()}%"
        sql += """
            AND (
                lower(marca) LIKE %s OR lower(modelo) LIKE %s
                OR lower(placa) LIKE %s OR lower(color) LIKE %s
            )
        """
        params.extend([value, value, value, value])

    sql += " ORDER BY tipo, precio_dia"
    try:
        with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        con.close()
    return [dict(row) for row in rows]


def get_car(car_id):
    if car_id is None:
        return None
    con = connect()
    try:
        with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM autos WHERE id = %s", (car_id,))
            row = cur.fetchone()
    finally:
        con.close()
    return dict(row) if row else None


def reserved_periods(car_id):
    con = connect()
    try:
        with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT fecha_inicio, fecha_fin
                FROM reservaciones
                WHERE auto_id = %s
                  AND estado IN ('Confirmada', 'Pendiente')
                  AND fecha_fin >= CURRENT_DATE
                ORDER BY fecha_inicio
                """,
                (car_id,),
            )
            rows = cur.fetchall()
    finally:
        con.close()
    return [dict(row) for row in rows]


def car_available(car_id, start, end):
    con = connect()
    try:
        with con.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM reservaciones
                WHERE auto_id = %s
                  AND estado IN ('Confirmada', 'Pendiente')
                  AND NOT (fecha_fin < %s OR fecha_inicio > %s)
                LIMIT 1
                """,
                (car_id, start, end),
            )
            conflict = cur.fetchone()
    finally:
        con.close()
    return conflict is None


def availability(car_id):
    periods = reserved_periods(car_id)
    result = []

    for offset in range(30):
        current = date.today() + timedelta(days=offset)
        occupied = any(
            _as_date(p["fecha_inicio"]) <= current <= _as_date(p["fecha_fin"])
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


def _as_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


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
        with con.cursor() as cur:
            cur.execute(
                """
                INSERT INTO reservaciones (
                    codigo, usuario_id, auto_id, fecha_inicio, fecha_fin,
                    dias, total, estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Confirmada')
                """,
                (code, user_id, car_id, start, end, days, total),
            )
        con.commit()
        return True, code
    finally:
        con.close()


def my_reservations(user_id):
    con = connect()
    try:
        with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT r.*, a.marca, a.modelo, a.placa, a.color, a.tipo, a.anio
                FROM reservaciones r
                JOIN autos a ON a.id = r.auto_id
                WHERE r.usuario_id = %s
                ORDER BY r.id DESC
                """,
                (user_id,),
            )
            rows = cur.fetchall()
    finally:
        con.close()
    return [dict(row) for row in rows]


def show_car(car):
    st.image(
        car_image(car["marca"], car["modelo"]),
        caption=f"{car['marca']} {car['modelo']} — imagen referencial",
        use_container_width=True,
    )
    st.subheader(f"{car['marca']} {car['modelo']}")
    st.caption(f"{car['tipo']} · Año {car['anio']}")

    c1, c2 = st.columns(2)
    c1.write(f"**Placa:** {car['placa']}")
    c1.write(f"**Color:** {car['color']}")
    c2.write(f"**Estado:** {car['estado']}")
    c2.write(f"**Precio:** ${car['precio_dia']:.2f}/día")


def selected_car_panel(car):
    st.divider()
    st.header("Vehículo seleccionado")

    photo, details = st.columns([1.2, 1])

    with photo:
        st.image(
            car_image(car["marca"], car["modelo"]),
            caption=f"{car['marca']} {car['modelo']} — imagen referencial",
            use_container_width=True,
        )

    with details:
        with st.container(border=True):
            st.subheader(f"{car['marca']} {car['modelo']}")
            st.write(f"**Categoría:** {car['tipo']}")
            st.write(f"**Año:** {car['anio']}")
            st.write(f"**Placa:** {car['placa']}")
            st.write(f"**Color:** {car['color']}")
            st.write(f"**Precio:** ${car['precio_dia']:.2f}/día")

    tab_dates, tab_reserve = st.tabs(
        ["Fechas disponibles", "Realizar reservación"]
    )

    with tab_dates:
        st.dataframe(
            availability(car["id"]),
            use_container_width=True,
            hide_index=True,
        )

        periods = reserved_periods(car["id"])
        if periods:
            st.warning("Periodos ocupados:")
            for period in periods:
                st.write(f"• {period['fecha_inicio']} al {period['fecha_fin']}")
        else:
            st.success("El vehículo no tiene reservas futuras.")

    with tab_reserve:
        if not st.session_state.user:
            st.warning("Debes iniciar sesión para reservar.")
            if st.button("Ir a iniciar sesión", use_container_width=True):
                st.session_state.page = "Ingresar"
                st.rerun()
            return

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
            st.success("El vehículo está disponible para esas fechas.")
        else:
            st.error("El vehículo está ocupado en ese periodo.")

        m1, m2 = st.columns(2)
        m1.metric("Días", days)
        m2.metric("Total", f"${total:.2f}")

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
                st.error("Confirma los dos requisitos.")
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
                    st.success("Reservación confirmada.")
                    st.code(result, language=None)
                    st.balloons()
                else:
                    st.error(result)


def home():
    st.title("🚗 QuitoDrive")
    st.write(
        "Renta de autos fácil, segura y rápida en Quito. "
        "Selecciona un vehículo, revisa sus fechas y reserva."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Vehículos", len(list_cars()))
    c2.metric("Categorías", len(CATEGORIES))
    c3.metric("Reservación", "100% en línea")

    a, b, c = st.columns(3)
    with a:
        with st.container(border=True):
            st.subheader("1. Regístrate")
            st.write("Crea una cuenta.")
    with b:
        with st.container(border=True):
            st.subheader("2. Selecciona")
            st.write("Elige un vehículo.")
    with c:
        with st.container(border=True):
            st.subheader("3. Reserva")
            st.write("Escoge fechas disponibles.")

    st.info("Servicio para mayores de 18 años con licencia vigente.")


def catalog():
    st.title("Catálogo de vehículos")

    with st.expander("ℹ️ Acerca de los tipos de autos"):
        cols = st.columns(3)
        for index, (name, data) in enumerate(CATEGORIES.items()):
            icon, description, models = data
            with cols[index % 3]:
                with st.container(border=True):
                    st.subheader(f"{icon} {name}")
                    st.write(description)
                    st.write(f"**Modelos:** {models}")

    f1, f2 = st.columns(2)
    with f1:
        vehicle_type = st.selectbox(
            "Tipo de vehículo",
            ["Todos", *CATEGORIES.keys()],
        )
    with f2:
        search = st.text_input("Buscar marca, modelo, placa o color")

    cars = list_cars(vehicle_type, search)
    st.write(f"**Vehículos encontrados:** {len(cars)}")

    cols = st.columns(3)
    for index, car in enumerate(cars):
        with cols[index % 3]:
            with st.container(border=True):
                show_car(car)

                selected = st.session_state.selected_car_id == car["id"]
                if st.button(
                    "✓ Seleccionado" if selected else "Seleccionar este auto",
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
    st.title("Crear cuenta")

    with st.form("register_form"):
        nombre = st.text_input("Nombre completo")
        cedula = st.text_input("Cédula")
        correo = st.text_input("Correo electrónico")
        telefono = st.text_input("Teléfono")
        edad = st.number_input("Edad", 18, 100, 18)
        password = st.text_input("Contraseña", type="password")
        confirm = st.text_input("Confirmar contraseña", type="password")
        terms = st.checkbox("Soy mayor de 18 años y acepto las condiciones.")
        submit = st.form_submit_button("Registrarme", use_container_width=True)

    if submit:
        if not all([nombre, cedula, correo, telefono, password]):
            st.error("Completa todos los campos.")
        elif "@" not in correo or "." not in correo:
            st.error("Correo no válido.")
        elif len(password) < 8:
            st.error("La contraseña debe tener al menos 8 caracteres.")
        elif password != confirm:
            st.error("Las contraseñas no coinciden.")
        elif not terms:
            st.error("Acepta las condiciones.")
        else:
            ok, message = register_user(
                nombre, cedula, correo, telefono, edad, password
            )
            st.success(message) if ok else st.error(message)


def login():
    st.title("Iniciar sesión")

    with st.form("login_form"):
        correo = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar", use_container_width=True)

    if submit:
        user = login_user(correo, password)
        if user:
            st.session_state.user = user
            st.session_state.page = "Catálogo"
            st.rerun()
        else:
            st.error("Correo o contraseña incorrectos.")


def reservations():
    st.title("Mis reservaciones")
    rows = my_reservations(st.session_state.user["id"])

    if not rows:
        st.info("Todavía no tienes reservaciones.")
        return

    for row in rows:
        with st.expander(f"{row['codigo']} | {row['marca']} {row['modelo']}"):
            c1, c2 = st.columns([1, 1.3])
            with c1:
                st.image(
                    car_image(row["marca"], row["modelo"]),
                    caption="Imagen referencial",
                    use_container_width=True,
                )
            with c2:
                st.write(f"**Categoría:** {row['tipo']}")
                st.write(f"**Placa:** {row['placa']}")
                st.write(f"**Color:** {row['color']}")
                st.write(f"**Periodo:** {row['fecha_inicio']} al {row['fecha_fin']}")
                st.write(f"**Días:** {row['dias']}")
                st.write(f"**Total:** ${row['total']:.2f}")
                st.write(f"**Estado:** {row['estado']}")


def main():
    init_db()

    st.session_state.setdefault("user", None)
    st.session_state.setdefault("selected_car_id", None)
    st.session_state.setdefault("page", "Inicio")

    with st.sidebar:
        st.title("🚗 QuitoDrive")

        if st.session_state.user:
            st.success(f"Hola, {st.session_state.user['nombre']}")
            pages = ["Inicio", "Catálogo", "Mis reservaciones"]
        else:
            pages = ["Inicio", "Catálogo", "Ingresar", "Registrarse"]

        if st.session_state.page not in pages:
            st.session_state.page = "Inicio"

        page = st.radio(
            "Menú principal",
            pages,
            index=pages.index(st.session_state.page),
        )

        if page != st.session_state.page:
            st.session_state.page = page
            st.rerun()

        st.caption("Servicio para mayores de 18 años.")

        if st.session_state.user and st.button(
            "Cerrar sesión",
            use_container_width=True,
        ):
            st.session_state.user = None
            st.session_state.page = "Inicio"
            st.rerun()

    if st.session_state.page == "Inicio":
        home()
    elif st.session_state.page == "Catálogo":
        catalog()
    elif st.session_state.page == "Ingresar":
        login()
    elif st.session_state.page == "Registrarse":
        register()
    elif st.session_state.page == "Mis reservaciones":
        reservations()


if __name__ == "__main__":
    main()

