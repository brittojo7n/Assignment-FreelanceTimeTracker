import pandas as pd
import psycopg2
from database import get_db_connection
from project_manager import ProjectManager
from file_handler import FileHandler

class Reporter:
    def __init__(self, project_manager: ProjectManager, file_handler: FileHandler):
        self.project_manager = project_manager
        self.file_handler = file_handler

    def generate_project_summary(self):
        if not self.project_manager.list_projects():
            return
        try:
            project_id = int(input("Enter the project ID for the summary: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        sql_project = "SELECT name, hourly_rate FROM projects WHERE id = %s"
        sql_entries = "SELECT task, start_time, end_time, duration_hours FROM time_entries WHERE project_id = %s ORDER BY start_time"
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql_project, (project_id,))
                    project = cur.fetchone()
                    if not project:
                        print("Invalid project ID.")
                        return
                    
                    cur.execute(sql_entries, (project_id,))
                    entries = cur.fetchall()

            project_details = {'name': project[0], 'hourly_rate': float(project[1])}
            
            if not entries:
                print(f"No time entries found for project '{project_details['name']}'.")
                return

            total_hours = sum(float(e[3]) for e in entries)
            total_cost = total_hours * project_details['hourly_rate']

            print(f"\n--- Summary for Project: {project_details['name']} ---")
            print(f"Hourly Rate: ${project_details['hourly_rate']:.2f}/hr")
            print("\nTime Entries:")
            for entry in entries:
                print(f"  - Task: {entry[0]}, Duration: {float(entry[3]):.2f} hours (from {entry[1].strftime('%Y-%m-%d %H:%M')} to {entry[2].strftime('%H:%M')})")

            print("\n--- Totals ---")
            print(f"Total Billable Hours: {total_hours:.2f}")
            print(f"Total Project Cost: ${total_cost:.2f}")
            print("--------------")
            self.file_handler.log_activity(f"Generated summary for project '{project_details['name']}'.")
        except (Exception, psycopg2.Error) as error:
            print("Error generating summary:", error)

    def export_invoice_csv(self):
        if not self.project_manager.list_projects():
            return
        try:
            project_id = int(input("Enter the project ID to invoice: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        sql_project = "SELECT p.name, p.hourly_rate, c.name FROM projects p JOIN clients c ON p.client_id = c.id WHERE p.id = %s"
        sql_entries = "SELECT task, start_time, end_time, duration_hours FROM time_entries WHERE project_id = %s ORDER BY start_time"

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql_project, (project_id,))
                    project = cur.fetchone()
                    if not project:
                        print("Invalid project ID.")
                        return
                    
                    cur.execute(sql_entries, (project_id,))
                    entries_data = cur.fetchall()

            project_details = {'name': project[0], 'hourly_rate': float(project[1])}
            client_name = project[2]
            
            if not entries_data:
                print(f"No time entries to invoice for project '{project_details['name']}'.")
                return
            
            time_entries = [{'task': e[0], 'start_time': e[1], 'end_time': e[2], 'duration_hours': float(e[3])} for e in entries_data]
            
            self.file_handler.export_invoice_to_csv(project_details, client_name, time_entries)

        except (Exception, psycopg2.Error) as error:
            print("Error exporting invoice:", error)

    def import_time_entries_from_json(self):
        file_path = input("Enter the full path to the JSON file to import: ")
        new_entries = self.file_handler.import_json_file(file_path)
        if new_entries is None:
            return

        sql = "INSERT INTO time_entries (project_id, task, start_time, end_time, duration_hours) VALUES (%s, %s, %s, %s, %s)"
        imported_count = 0
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    for entry in new_entries:
                        if all(k in entry for k in ['project_id', 'task', 'start_time', 'end_time', 'duration_hours']):
                            cur.execute(sql, (
                                entry['project_id'],
                                entry['task'],
                                entry['start_time'],
                                entry['end_time'],
                                entry['duration_hours']
                            ))
                            imported_count += 1
                        else:
                            print(f"Skipping invalid entry: {entry}")
                conn.commit()
            self.file_handler.log_activity(f"Imported {imported_count} time entries from {file_path}.")
            print(f"Successfully imported {imported_count} time entries into the database.")
        except (Exception, psycopg2.Error) as error:
            print("Error during database import:", error)

    def analyze_data(self):
        sql = """
            SELECT p.name AS project_name, te.duration_hours, p.hourly_rate, te.start_time
            FROM time_entries te
            JOIN projects p ON te.project_id = p.id
        """
        try:
            with get_db_connection() as conn:
                df = pd.read_sql(sql, conn)

            if df.empty:
                print("No time entries to analyze.")
                return

            df['cost'] = df['duration_hours'] * df['hourly_rate']
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
        except (Exception, psycopg2.Error) as error:
            print("Error during data analysis:", error)