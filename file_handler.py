import os
import json
import csv
from datetime import datetime
import config

class FileHandler:
    def __init__(self):
        os.makedirs(config.INVOICES_DIR, exist_ok=True)
        if not os.path.exists(config.ACTIVITY_LOG_FILE):
            self.log_activity("Activity Log Initialized.")
        print("File handler initialized.")

    def log_activity(self, message):
        with open(config.ACTIVITY_LOG_FILE, 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp} - {message}\n")

    def export_invoice_to_csv(self, project_details, client_name, time_entries):
        invoice_date = datetime.now().strftime('%Y%m%d')
        project_name_safe = project_details['name'].replace(' ', '')
        client_name_safe = client_name.replace(' ', '')
        
        file_name = f"Invoice_{client_name_safe}_{project_name_safe}_{invoice_date}.csv"
        file_path = os.path.join(config.INVOICES_DIR, file_name)

        total_hours = sum(entry.duration_hours for entry in time_entries)
        total_cost = total_hours * project_details['hourly_rate']

        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                header = [
                    'Project Name', 'Client', 'Invoice Date', 'Hourly Rate', 
                    'Task Description', 'Start Time', 'End Time', 
                    'Duration (Hours)', 'Cost', 'Total Hours', 'Total Cost'
                ]
                writer.writerow(header)

                project_info_row = [
                    project_details['name'],
                    client_name,
                    datetime.now().strftime('%Y-%m-%d'),
                    f"${project_details['hourly_rate']:.2f}",
                    '', '', '', '', '', '', ''
                ]
                writer.writerow(project_info_row)

                for entry in time_entries:
                    cost = entry.duration_hours * project_details['hourly_rate']
                    task_row = [
                        '', '', '', '',
                        entry.task,
                        entry.start_time.strftime('%Y-%m-%d %H:%M'),
                        entry.end_time.strftime('%Y-%m-%d %H:%M'),
                        f"{float(entry.duration_hours):.2f}",
                        f"{float(cost):.2f}",
                        '', ''
                    ]
                    writer.writerow(task_row)
                
                totals_row = [
                    '', '', '', '', '', '', '', '', '',
                    f"{float(total_hours):.2f}",
                    f"${float(total_cost):.2f}"
                ]
                writer.writerow(totals_row)
            
            self.log_activity(f"Exported invoice for project '{project_details['name']}' to {file_path}")
            print(f"Invoice successfully exported to {file_path}")
        except IOError as e:
            print(f"Error writing to file: {e}")

    def import_json_file(self, file_path):
        if not os.path.exists(file_path):
            print(f"Error: File not found at '{file_path}'")
            return None
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            if not isinstance(data, list):
                print("Error: JSON file should contain a list of entries.")
                return None
            return data
        except json.JSONDecodeError:
            print("Error: Could not decode JSON. Please check the file format.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while reading the file: {e}")
            return None
