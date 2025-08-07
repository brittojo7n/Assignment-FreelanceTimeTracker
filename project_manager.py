import psycopg2
from database import get_db_connection
from client_manager import ClientManager
from file_handler import FileHandler

class ProjectManager:
    def __init__(self, client_manager: ClientManager, file_handler: FileHandler):
        self.client_manager = client_manager
        self.file_handler = file_handler

    def add_project(self):
        if not self.client_manager.list_clients():
            print("Please add a client first.")
            return
        
        try:
            client_id = int(input("Enter the client ID for this project: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        project_name = input("Enter project name: ")
        try:
            hourly_rate = float(input("Enter hourly rate for this project: "))
        except ValueError:
            print("Invalid hourly rate. Please enter a number.")
            return

        sql = "INSERT INTO projects (name, hourly_rate, client_id) VALUES (%s, %s, %s)"
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (project_name, hourly_rate, client_id))
                conn.commit()
            self.file_handler.log_activity(f"Added project: {project_name} for client ID {client_id}")
            print(f"Project '{project_name}' added successfully.")
        except (Exception, psycopg2.Error) as error:
            print("Error while adding project:", error)
            print("Please ensure the Client ID is valid.")

    def list_projects(self):
        sql = """
            SELECT p.id, p.name, c.name, p.hourly_rate 
            FROM projects p
            JOIN clients c ON p.client_id = c.id
            ORDER BY p.name
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    projects = cur.fetchall()
            if not projects:
                print("No projects found.")
                return False
            print("\n--- Projects ---")
            for p in projects:
                print(f"ID: {p[0]}, Name: {p[1]}, Client: {p[2]}, Rate: ${p[3]:.2f}/hr")
            print("----------------")
            return True
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching projects:", error)
            return False