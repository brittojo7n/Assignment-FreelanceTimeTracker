import psycopg2
import config

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error: Could not connect to the database. Please check your .env settings.")
        print(f"Details: {e}")
        return None

def initialize_database():
    conn = get_db_connection()
    if conn is None:
        return

    commands = (
        """
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            hourly_rate NUMERIC(10, 2) NOT NULL,
            client_id INTEGER NOT NULL,
            FOREIGN KEY (client_id)
                REFERENCES clients (id)
                ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS time_entries (
            id SERIAL PRIMARY KEY,
            task TEXT,
            start_time TIMESTAMPTZ NOT NULL,
            end_time TIMESTAMPTZ NOT NULL,
            duration_hours NUMERIC(10, 4) NOT NULL,
            project_id INTEGER NOT NULL,
            FOREIGN KEY (project_id)
                REFERENCES projects (id)
                ON DELETE CASCADE
        )
        """
    )
    
    try:
        with conn.cursor() as cur:
            for command in commands:
                cur.execute(command)
        conn.commit()
        print("Database tables checked/initialized successfully.")
    except (psycopg2.Error) as e:
        print(f"Error during database initialization: {e}")
    finally:
        if conn:
            conn.close()