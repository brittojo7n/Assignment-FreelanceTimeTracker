import psycopg2
from database import get_db_connection
from file_handler import FileHandler

class ClientManager:
    def __init__(self, file_handler: FileHandler):
        self.file_handler = file_handler

    def add_client(self):
        client_name = input("Enter client name: ")
        sql = "INSERT INTO clients (name) VALUES (%s) RETURNING id"
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (client_name,))
                    client_id = cur.fetchone()[0]
                conn.commit()
                self.file_handler.log_activity(f"Added client: {client_name} with ID {client_id}")
                print(f"Client '{client_name}' added successfully.")
        except psycopg2.IntegrityError:
            print("Client with this name already exists.")
        except (Exception, psycopg2.Error) as error:
            print("Error while adding client:", error)

    def list_clients(self):
        sql = "SELECT id, name FROM clients ORDER BY name"
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    clients = cur.fetchall()
            if not clients:
                print("No clients found.")
                return False
            print("\n--- Clients ---")
            for client in clients:
                print(f"ID: {client[0]}, Name: {client[1]}")
            print("---------------")
            return True
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching clients:", error)
            return False