import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Project, TimeEntry
from project_manager import ProjectManager
from file_handler import FileHandler

class Reporter:
    def __init__(self, project_manager: ProjectManager, file_handler: FileHandler):
        self.project_manager = project_manager
        self.file_handler = file_handler
        self.db: Session = SessionLocal()

    def generate_project_summary(self):
        if not self.project_manager.list_projects():
            return
        try:
            project_id = int(input("Enter the project ID for the summary: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        try:
            project = self.db.query(Project).filter(Project.id == project_id).one_or_none()
            if not project:
                print("Invalid project ID.")
                return
            
            entries = self.db.query(TimeEntry).filter(TimeEntry.project_id == project_id).order_by(TimeEntry.start_time).all()
            
            if not entries:
                print(f"No time entries found for project '{project.name}'.")
                return

            total_hours = sum(entry.duration_hours for entry in entries)
            total_cost = total_hours * project.hourly_rate

            print(f"\n--- Summary for Project: {project.name} ---")
            print(f"Hourly Rate: ${project.hourly_rate:.2f}/hr")
            print("\nTime Entries:")
            for entry in entries:
                print(f"  - Task: {entry.task}, Duration: {float(entry.duration_hours):.2f} hours (from {entry.start_time.strftime('%Y-%m-%d %H:%M')} to {entry.end_time.strftime('%H:%M')})")

            print("\n--- Totals ---")
            print(f"Total Billable Hours: {float(total_hours):.2f}")
            print(f"Total Project Cost: ${float(total_cost):.2f}")
            print("--------------")
            self.file_handler.log_activity(f"Generated summary for project '{project.name}'.")
        except Exception as error:
            print("Error generating summary:", error)

    def export_invoice_csv(self):
        if not self.project_manager.list_projects():
            return
        try:
            project_id = int(input("Enter the project ID to invoice: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        try:
            project = self.db.query(Project).filter(Project.id == project_id).one_or_none()
            if not project:
                print("Invalid project ID.")
                return
            
            entries = self.db.query(TimeEntry).filter(TimeEntry.project_id == project_id).order_by(TimeEntry.start_time).all()
            
            if not entries:
                print(f"No time entries to invoice for project '{project.name}'.")
                return
            
            project_details = {'name': project.name, 'hourly_rate': project.hourly_rate}
            self.file_handler.export_invoice_to_csv(project_details, project.client.name, entries)

        except Exception as error:
            print("Error exporting invoice:", error)

    def import_time_entries_from_json(self):
        file_path = input("Enter the full path to the JSON file to import: ")
        new_entries_data = self.file_handler.import_json_file(file_path)
        if new_entries_data is None:
            return

        imported_count = 0
        try:
            for entry_data in new_entries_data:
                if all(k in entry_data for k in ['project_id', 'task', 'start_time', 'end_time', 'duration_hours']):
                    new_entry = TimeEntry(**entry_data)
                    self.db.add(new_entry)
                    imported_count += 1
                else:
                    print(f"Skipping invalid entry: {entry_data}")
            self.db.commit()
            self.file_handler.log_activity(f"Imported {imported_count} time entries from {file_path}.")
            print(f"Successfully imported {imported_count} time entries into the database.")
        except Exception as error:
            self.db.rollback()
            print("Error during database import:", error)

    def analyze_data(self):
        query = self.db.query(
            Project.name.label("project_name"),
            TimeEntry.duration_hours,
            Project.hourly_rate,
            TimeEntry.start_time
        ).join(Project, TimeEntry.project_id == Project.id).statement

        try:
            df = pd.read_sql(query, engine)
            if df.empty:
                print("No time entries to analyze.")
                return

            df['cost'] = df['duration_hours'].astype(float) * df['hourly_rate'].astype(float)
            df['date'] = pd.to_datetime(df['start_time']).dt.date

            print("\n--- Data Analysis ---")
            billable_hours = df.groupby('project_name')['duration_hours'].sum().round(2)
            print("\nTotal Billable Hours per Project:")
            print(billable_hours.to_string())

            project_costs = df.groupby('project_name')['cost'].sum().round(2)
            print("\nTotal Earnings per Project:")
            print(project_costs.to_string())

            daily_hours = df.groupby('date')['duration_hours'].sum().round(2)
            print("\nWork Trend (Total Hours per Day):")
            print(daily_hours.to_string())
            
            print("\n---------------------")
            self.file_handler.log_activity("Performed data analysis.")
        except Exception as error:
            print("Error during data analysis:", error)
