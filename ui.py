from client_manager import ClientManager
from project_manager import ProjectManager
from time_tracker import TimeTracker
from reporter import Reporter

class UIManager:
    def __init__(self, client_manager, project_manager, time_tracker, reporter):
        self.client_manager = client_manager
        self.project_manager = project_manager
        self.time_tracker = time_tracker
        self.reporter = reporter

    def main_menu(self):
        menu_options = {
            "1": "Manage Clients",
            "2": "Manage Projects",
            "3": "Track Time",
            "4": "Reporting & Invoicing",
            "5": "Analyze Data",
            "6": "Exit"
        }
        while True:
            print("\n===== Freelance Time Tracker (DB + File) =====")
            for key, value in menu_options.items():
                print(f"{key}. {value}")
            choice = input("Enter your choice: ")

            if choice == '1':
                self.client_menu()
            elif choice == '2':
                self.project_menu()
            elif choice == '3':
                self.time_tracking_menu()
            elif choice == '4':
                self.reporting_menu()
            elif choice == '5':
                self.reporter.analyze_data()
            elif choice == '6':
                print("Exiting. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def client_menu(self):
        while True:
            print("\n--- Client Management ---")
            print("1. Add Client")
            print("2. List Clients")
            print("3. Back to Main Menu")
            choice = input("Enter your choice: ")
            if choice == '1':
                self.client_manager.add_client()
            elif choice == '2':
                self.client_manager.list_clients()
            elif choice == '3':
                break
            else:
                print("Invalid choice.")

    def project_menu(self):
        while True:
            print("\n--- Project Management ---")
            print("1. Add Project")
            print("2. List Projects")
            print("3. Back to Main Menu")
            choice = input("Enter your choice: ")
            if choice == '1':
                self.project_manager.add_project()
            elif choice == '2':
                self.project_manager.list_projects()
            elif choice == '3':
                break
            else:
                print("Invalid choice.")

    def time_tracking_menu(self):
        while True:
            print("\n--- Time Tracking ---")
            print("1. Start Timer")
            print("2. Stop Timer")
            print("3. View Active Timers")
            print("4. Back to Main Menu")
            choice = input("Enter your choice: ")
            if choice == '1':
                self.time_tracker.start_timer()
            elif choice == '2':
                self.time_tracker.stop_timer()
            elif choice == '3':
                self.time_tracker.view_active_timers()
            elif choice == '4':
                break
            else:
                print("Invalid choice.")

    def reporting_menu(self):
        while True:
            print("\n--- Reporting & Invoicing ---")
            print("1. Generate Project Summary")
            print("2. Export Invoice to CSV")
            print("3. Import Time Entries from JSON")
            print("4. Back to Main Menu")
            choice = input("Enter your choice: ")
            if choice == '1':
                self.reporter.generate_project_summary()
            elif choice == '2':
                self.reporter.export_invoice_csv()
            elif choice == '3':
                self.reporter.import_time_entries_from_json()
            elif choice == '4':
                break
            else:
                print("Invalid choice.")