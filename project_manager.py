from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models import Project
from client_manager import ClientManager
from file_handler import FileHandler

class ProjectManager:
    def __init__(self, client_manager: ClientManager, file_handler: FileHandler):
        self.client_manager = client_manager
        self.file_handler = file_handler
        self.db: Session = SessionLocal()

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

        new_project = Project(name=project_name, hourly_rate=hourly_rate, client_id=client_id)
        try:
            self.db.add(new_project)
            self.db.commit()
            self.file_handler.log_activity(f"Added project: {project_name} for client ID {client_id}")
            print(f"Project '{project_name}' added successfully.")
        except IntegrityError:
            self.db.rollback()
            print("Error: A database integrity issue occurred. Please ensure the Client ID is valid.")
        except Exception as e:
            self.db.rollback()
            print("Error while adding project:", e)

    def list_projects(self):
        try:
            projects = self.db.query(Project).order_by(Project.name).all()
            if not projects:
                print("No projects found.")
                return False
            print("\n--- Projects ---")
            for p in projects:
                print(f"ID: {p.id}, Name: {p.name}, Client: {p.client.name}, Rate: ${p.hourly_rate:.2f}/hr")
            print("----------------")
            return True
        except Exception as e:
            print("Error while fetching projects:", e)
            return False
