from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models import Client
from file_handler import FileHandler

class ClientManager:
    def __init__(self, file_handler: FileHandler):
        self.file_handler = file_handler
        self.db: Session = SessionLocal()

    def add_client(self):
        client_name = input("Enter client name: ").strip()
        new_client = Client(name=client_name)
        if client_name == "":
            print("Invalid Name!")
        else:
            try:
                self.db.add(new_client)
                self.db.commit()
                self.db.refresh(new_client)
                self.file_handler.log_activity(f"Added client: {client_name} with ID {new_client.id}")
                print(f"Client '{client_name}' added successfully.")
            except IntegrityError:
                self.db.rollback()
                print("Client with this name already exists.")
            except Exception as e:
                self.db.rollback()
                print("Error while adding client:", e)

    def list_clients(self):
        try:
            clients = self.db.query(Client).order_by(Client.name).all()
            if not clients:
                print("No clients found.")
                return False
            print("\n--- Clients ---")
            for client in clients:
                print(f"ID: {client.id}, Name: {client.name}")
            print("---------------")
            return True
        except Exception as e:
            print("Error while fetching clients:", e)
            return False
