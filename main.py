import database
from file_handler import FileHandler
from client_manager import ClientManager
from project_manager import ProjectManager
from time_tracker import TimeTracker
from reporter import Reporter
from ui import UIManager

def main():
    database.initialize_database()
    file_handler = FileHandler()
    
    client_manager = ClientManager(file_handler)
    project_manager = ProjectManager(client_manager, file_handler)
    time_tracker = TimeTracker(project_manager, file_handler)
    reporter = Reporter(project_manager, file_handler)
    
    ui = UIManager(client_manager, project_manager, time_tracker, reporter)
    ui.main_menu()

if __name__ == "__main__":
    main()