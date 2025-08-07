from datetime import datetime
import psycopg2
from database import get_db_connection
from project_manager import ProjectManager
from file_handler import FileHandler

class TimeTracker:
    def __init__(self, project_manager: ProjectManager, file_handler: FileHandler):
        self.project_manager = project_manager
        self.file_handler = file_handler
        self.active_timers = {}

    def start_timer(self):
        if not self.project_manager.list_projects():
            print("Please add a project first.")
            return

        try:
            project_id = int(input("Enter the project ID to start tracking: "))
            if project_id in self.active_timers:
                print("A timer is already running for this project.")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        task_description = input("Enter a brief description for this task: ")
        start_time = datetime.now()
        self.active_timers[project_id] = {
            "start_time": start_time,
            "task": task_description
        }
        self.file_handler.log_activity(f"Started timer for project ID {project_id} (Task: {task_description})")
        print(f"Timer started for project ID {project_id} at {start_time.strftime('%H:%M:%S')}")

    def stop_timer(self):
        if not self.active_timers:
            print("No active timers to stop.")
            return

        self.view_active_timers()
        try:
            project_id_to_stop = int(input("Enter the project ID to stop the timer for: "))
            if project_id_to_stop not in self.active_timers:
                print("No active timer found for this project ID.")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        timer_data = self.active_timers.pop(project_id_to_stop)
        start_time = timer_data['start_time']
        end_time = datetime.now()
        duration_hours = (end_time - start_time).total_seconds() / 3600

        sql = """
            INSERT INTO time_entries (project_id, task, start_time, end_time, duration_hours)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (
                        project_id_to_stop, 
                        timer_data['task'], 
                        start_time, 
                        end_time, 
                        duration_hours
                    ))
                conn.commit()
            self.file_handler.log_activity(f"Logged entry for project ID {project_id_to_stop}. Duration: {duration_hours:.2f} hours.")
            print(f"Timer stopped. Logged {duration_hours:.2f} hours for project ID {project_id_to_stop}.")
        except (Exception, psycopg2.Error) as error:
            print("Error while logging time entry:", error)
            self.active_timers[project_id_to_stop] = timer_data

    def view_active_timers(self):
        if not self.active_timers:
            print("No active timers.")
            return
        
        print("\n--- Active Timers ---")
        for project_id, data in self.active_timers.items():
            start_time_str = data['start_time'].strftime('%H:%M:%S')
            print(f"Project ID: {project_id}, Task: {data['task']}, Started: {start_time_str}")
        print("-----------------------")