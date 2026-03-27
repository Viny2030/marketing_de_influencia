cat << 'EOF' > database.py
import psycopg2
import os

def conectar_db():
    # Estos datos los sacaremos de Railway luego
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'marketing_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASS', 'password'),
            host=os.getenv('DB_HOST', 'localhost')
        )
        return conn
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def crear_tablas():
    conn = conectar_db()
    if conn:
        cur = conn.cursor()
        # Tabla para registrar cada posteo de influencer
        cur.execute("""
            CREATE TABLE IF NOT EXISTS campañas (
                id SERIAL PRIMARY KEY,
                influencer VARCHAR(255),
                url_video TEXT,
                fecha_pub TIMESTAMP,
                ventas_atribuidas INTEGER,
                monto_total FLOAT
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("🗄️ Estructura de base de datos lista.")

if __name__ == "__main__":
    crear_tablas()
EOF
