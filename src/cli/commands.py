#!/usr/bin/env python3
"""
Web Scraping CLI Commands
Command implementations for the web scraping project
"""

import json
import os
import sys
import time
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path

# Add src to path for imports
sys.path.append('src')

from src.scrapers.Master import Master
from src.scrapers.Task import Task
from src.utils.logger import log
from src.utils.configs import generate_tasks
from multiprocessing import Queue, Manager


class WebScrapingCommands:
    def __init__(self, config_file="config.json", results_dir="src/data"):
        self.config_file = config_file
        self.results_dir = results_dir

    def run_all_tasks(self):
        """Run all configured tasks"""
        print("\n🚀 Starting all scraping tasks...")
        try:
            # Create multiprocessing objects
            task_queue = Queue()
            result_queue = Queue()
            manager = Manager()
            worker_status = manager.dict()
            
            # Get tasks from config
            tasks = generate_tasks()
            tasks = [Task(i, tasks[i]["priority"], tasks[i]["url"], tasks[i]["type"], 
                         tasks[i].get("search_word")) 
                    for i in range(len(tasks))]
            
            # Create and run master
            master = Master(task_queue=task_queue, result_queue=result_queue, 
                          worker_status=worker_status)
            
            print(f"📋 Loaded {len(tasks)} tasks")
            print("⏳ Starting workers...")
            
            master.run(tasks)
            
            print("✅ Scraping completed successfully!")
            self.show_completion_summary()
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            log.error(f"Scraping error: {e}")

    def run_news_only(self):
        """Run only news scraping tasks"""
        print("\n📰 Starting news scraping...")
        self.run_filtered_tasks("news")

    def run_rss_only(self):
        """Run only RSS scraping tasks"""
        print("\n📻 Starting RSS scraping...")
        self.run_filtered_tasks("rss")

    def run_blog_only(self):
        """Run only blog scraping tasks"""
        print("\n📝 Starting blog scraping...")
        self.run_filtered_tasks("blog")

    def run_filtered_tasks(self, task_type):
        """Run tasks filtered by type"""
        try:
            tasks = generate_tasks()
            filtered_tasks = []
            
            for i, task in enumerate(tasks):
                if task["type"] == task_type:
                    filtered_tasks.append(Task(i, task["priority"], task["url"], task["type"], 
                                             task.get("search_word")))
            
            if not filtered_tasks:
                print(f"❌ No {task_type} tasks found in configuration.")
                return
            
            print(f"📋 Found {len(filtered_tasks)} {task_type} tasks")
            
            # Create multiprocessing objects
            task_queue = Queue()
            result_queue = Queue()
            manager = Manager()
            worker_status = manager.dict()
            
            # Create and run master
            master = Master(task_queue=task_queue, result_queue=result_queue, 
                          worker_status=worker_status)
            
            master.run(filtered_tasks)
            
            print(f"✅ {task_type.capitalize()} scraping completed!")
            self.show_completion_summary()
            
        except Exception as e:
            print(f"❌ Error during {task_type} scraping: {e}")
            log.error(f"{task_type} scraping error: {e}")

    def run_custom_selection(self):
        """Run custom task selection"""
        print("\n🎯 Custom Task Selection")
        tasks = generate_tasks()
        
        print("\nAvailable tasks:")
        for i, task in enumerate(tasks):
            print(f"{i+1}. {task['type'].upper()}: {task['url']} (Priority: {task['priority']})")
        
        try:
            selection = input("\nEnter task numbers to run (comma-separated, e.g., 1,3,4): ").strip()
            task_indices = [int(x.strip()) - 1 for x in selection.split(',')]
            
            selected_tasks = []
            for idx in task_indices:
                if 0 <= idx < len(tasks):
                    task = tasks[idx]
                    selected_tasks.append(Task(idx, task["priority"], task["url"], task["type"], 
                                             task.get("search_word")))
            
            if not selected_tasks:
                print("❌ No valid tasks selected.")
                return
            
            print(f"📋 Running {len(selected_tasks)} selected tasks...")
            
            # Create multiprocessing objects
            task_queue = Queue()
            result_queue = Queue()
            manager = Manager()
            worker_status = manager.dict()
            
            # Create and run master
            master = Master(task_queue=task_queue, result_queue=result_queue, 
                          worker_status=worker_status)
            
            master.run(selected_tasks)
            
            print("✅ Custom scraping completed!")
            self.show_completion_summary()
            
        except (ValueError, IndexError) as e:
            print(f"❌ Invalid selection: {e}")

    def edit_tasks(self):
        """Edit task configuration"""
        print("\n📝 Edit Tasks")
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            print("\nCurrent tasks:")
            for i, task in enumerate(config["tasks"]):
                print(f"{i+1}. {task['type'].upper()}: {task['url']} (Priority: {task['priority']})")
            
            print("\nOptions:")
            print("1. Add new task")
            print("2. Edit existing task")
            print("3. Delete task")
            print("4. ⬅️  Back")
            
            choice = input("Select option (1-4): ").strip()
            
            if choice == '1':
                self.add_task(config)
            elif choice == '2':
                self.edit_existing_task(config)
            elif choice == '3':
                self.delete_task(config)
            elif choice == '4':
                return
            else:
                print("❌ Invalid option.")
                
        except Exception as e:
            print(f"❌ Error editing tasks: {e}")

    def add_task(self, config):
        """Add a new task"""
        print("\n➕ Add New Task")
        
        task_type = input("Task type (news/rss/blog): ").strip().lower()
        if task_type not in ['news', 'rss', 'blog']:
            print("❌ Invalid task type.")
            return

        # todo: modify for different types
        url = input("URL: ").strip()
        if not url.startswith(('http://', 'https://')):
            print("❌ Invalid URL.")
            return
        
        try:
            priority = int(input("Priority (1-10): ").strip())
            if not 1 <= priority <= 10:
                print("❌ Priority must be between 1 and 10.")
                return
        except ValueError:
            print("❌ Invalid priority.")
            return
        
        new_task = {
            "priority": priority,
            "url": url,
            "type": task_type
        }
        
        config["tasks"].append(new_task)
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Task added successfully!")

    def edit_existing_task(self, config):
        """Edit an existing task"""
        print("\n✏️  Edit Existing Task")
        
        try:
            task_index = int(input("Enter task number to edit: ").strip()) - 1
            if not 0 <= task_index < len(config["tasks"]):
                print("❌ Invalid task number.")
                return
            
            task = config["tasks"][task_index]
            print(f"\nEditing task: {task['type'].upper()}: {task['url']}")
            
            # Edit fields
            new_url = input(f"New URL (current: {task['url']}): ").strip()
            if new_url:
                task['url'] = new_url
            
            new_priority = input(f"New priority (current: {task['priority']}): ").strip()
            if new_priority:
                try:
                    task['priority'] = int(new_priority)
                except ValueError:
                    print("❌ Invalid priority.")
                    return
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Task updated successfully!")
            
        except ValueError:
            print("❌ Invalid input.")

    def delete_task(self, config):
        """Delete a task"""
        print("\n🗑️  Delete Task")
        
        try:
            task_index = int(input("Enter task number to delete: ").strip()) - 1
            if not 0 <= task_index < len(config["tasks"]):
                print("❌ Invalid task number.")
                return
            
            task = config["tasks"][task_index]
            confirm = input(f"Are you sure you want to delete {task['type'].upper()}: {task['url']}? (y/N): ").strip().lower()
            
            if confirm == 'y':
                del config["tasks"][task_index]
                
                with open(self.config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print("✅ Task deleted successfully!")
            else:
                print("❌ Deletion cancelled.")
                
        except ValueError:
            print("❌ Invalid input.")

    def worker_settings(self):
        """Configure worker settings"""
        print("\n🔧 Worker Settings")
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            print(f"\nCurrent settings:")
            print(f"Min workers: {config.get('min_workers', 2)}")
            print(f"Max workers: {config.get('max_workers', 5)}")
            
            new_min = input("New min workers (press Enter to keep current): ").strip()
            if new_min:
                config['min_workers'] = int(new_min)
            
            new_max = input("New max workers (press Enter to keep current): ").strip()
            if new_max:
                config['max_workers'] = int(new_max)
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Worker settings updated!")
            
        except Exception as e:
            print(f"❌ Error updating worker settings: {e}")

    def proxy_settings(self):
        """Configure proxy settings"""
        print("\n🌐 Proxy Settings")
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            print(f"\nCurrent proxies: {len(config.get('proxies', []))}")
            for i, proxy in enumerate(config.get('proxies', [])):
                print(f"  {i+1}. {proxy}")
            
            print("\nOptions:")
            print("1. Add proxy")
            print("2. Remove proxy")
            print("3. Clear all proxies")
            print("4. ⬅️  Back")
            
            choice = input("Select option (1-4): ").strip()
            
            if choice == '1':
                new_proxy = input("Enter proxy URL (e.g., http://proxy:port): ").strip()
                if new_proxy:
                    if 'proxies' not in config:
                        config['proxies'] = []
                    config['proxies'].append(new_proxy)
                    print("✅ Proxy added!")
            
            elif choice == '2':
                try:
                    proxy_index = int(input("Enter proxy number to remove: ").strip()) - 1
                    if 0 <= proxy_index < len(config.get('proxies', [])):
                        del config['proxies'][proxy_index]
                        print("✅ Proxy removed!")
                    else:
                        print("❌ Invalid proxy number.")
                except ValueError:
                    print("❌ Invalid input.")
            
            elif choice == '3':
                config['proxies'] = []
                print("✅ All proxies cleared!")
            
            elif choice == '4':
                return
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error updating proxy settings: {e}")

    def rate_limiting_settings(self):
        """Configure rate limiting settings"""
        print("\n📊 Rate Limiting Settings")
        print("⚠️  Rate limiting is currently hardcoded in the Worker class.")
        print("To modify rate limits, edit src/scrapers/Worker.py")
        print("Current setting: max_requests_per_second=1")

    def data_overview(self):
        """Show data overview"""
        print("\n📈 Data Overview")
        
        if not os.path.exists(self.results_dir):
            print("❌ No data directory found.")
            return
        
        data_files = [f for f in os.listdir(self.results_dir) if f.endswith('.json')]
        
        if not data_files:
            print("❌ No data files found.")
            return
        
        print(f"\n📁 Data files in {self.results_dir}:")
        total_items = 0
        
        for file in data_files:
            file_path = os.path.join(self.results_dir, file)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        count = len(data)
                    else:
                        count = 1
                    total_items += count
                    print(f"  📄 {file}: {count} items")
            except Exception as e:
                print(f"  ❌ {file}: Error reading file")
        
        print(f"\n📊 Total items: {total_items}")

    def performance_analytics(self):
        """Show performance analytics"""
        print("\n📊 Performance Analytics")
        
        summary_file = os.path.join(self.results_dir, "summary.csv")
        if not os.path.exists(summary_file):
            print("❌ No summary file found. Run scraping first.")
            return
        
        try:
            df = pd.read_csv(summary_file)
            print("\n📈 Task Performance:")
            print(df.to_string(index=False))
            
            if len(df) > 1:  # More than just summary rows
                task_data = df[df['task_id'].notna()]  # Filter out summary rows
                if not task_data.empty:
                    avg_time = task_data['processing_time'].mean()
                    total_time = task_data['processing_time'].sum()
                    print(f"\n⏱️  Average processing time: {avg_time:.2f} seconds")
                    print(f"⏱️  Total processing time: {total_time:.2f} seconds")
                    
        except Exception as e:
            print(f"❌ Error reading performance data: {e}")

    def task_summary(self):
        """Show task summary"""
        print("\n📋 Task Summary")
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            tasks = config.get('tasks', [])
            print(f"\n📋 Total tasks configured: {len(tasks)}")
            
            task_types = {}
            for task in tasks:
                task_type = task['type']
                task_types[task_type] = task_types.get(task_type, 0) + 1
            
            print("\n📊 Task breakdown:")
            for task_type, count in task_types.items():
                print(f"  📰 {task_type.upper()}: {count} tasks")
            
            print(f"\n🔧 Worker settings:")
            print(f"  Min workers: {config.get('min_workers', 2)}")
            print(f"  Max workers: {config.get('max_workers', 5)}")
            
        except Exception as e:
            print(f"❌ Error reading task summary: {e}")

    def data_visualization(self):
        """Create data visualizations"""
        print("\n🎯 Data Visualization")
        
        if not os.path.exists(self.results_dir):
            print("❌ No data directory found.")
            return
        
        # Create visualizations directory
        viz_dir = "visualizations"
        os.makedirs(viz_dir, exist_ok=True)
        
        try:
            # Load data
            data_files = [f for f in os.listdir(self.results_dir) if f.endswith('_data.json')]
            
            if not data_files:
                print("❌ No data files found for visualization.")
                return
            
            # Create summary plot
            plt.figure(figsize=(12, 8))
            
            # Data volume by type
            data_volumes = {}
            for file in data_files:
                file_path = os.path.join(self.results_dir, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        data_type = file.replace('_data.json', '')
                        data_volumes[data_type] = len(data)
            
            if data_volumes:
                plt.subplot(2, 2, 1)
                plt.bar(data_volumes.keys(), data_volumes.values())
                plt.title('Data Volume by Type')
                plt.ylabel('Number of Items')
                plt.xticks(rotation=45)
            
            # Performance data if available
            summary_file = os.path.join(self.results_dir, "summary.csv")
            if os.path.exists(summary_file):
                df = pd.read_csv(summary_file)
                task_data = df[df['task_id'].notna()]
                
                if not task_data.empty:
                    plt.subplot(2, 2, 2)
                    plt.bar(task_data['task_id'], task_data['processing_time'])
                    plt.title('Processing Time by Task')
                    plt.xlabel('Task ID')
                    plt.ylabel('Processing Time (seconds)')
            
            # Save plot
            plt.tight_layout()
            plot_file = os.path.join(viz_dir, f"scraping_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Visualization saved: {plot_file}")
            
        except Exception as e:
            print(f"❌ Error creating visualization: {e}")

    def generate_html_report(self):
        """Generate HTML report"""
        print("\n📄 Generating HTML Report")
        
        if not os.path.exists(self.results_dir):
            print("❌ No data directory found.")
            return
        
        try:
            # Create reports directory
            reports_dir = "data_output/reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate HTML content
            html_content = self.generate_html_content()
            
            # Save HTML file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_file = os.path.join(reports_dir, f"scraping_report_{timestamp}.html")
            
            with open(html_file, 'w') as f:
                f.write(html_content)
            
            print(f"✅ HTML report generated: {html_file}")
            
        except Exception as e:
            print(f"❌ Error generating HTML report: {e}")

    def generate_html_content(self):
        """Generate HTML content for the report"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Scraping Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        h2 { color: #007bff; margin-top: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }
        .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
        .stat-label { color: #666; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #007bff; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .timestamp { text-align: center; color: #666; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 Web Scraping Report</h1>
        <div class="timestamp">Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</div>
"""
        
        # Add statistics
        data_files = [f for f in os.listdir(self.results_dir) if f.endswith('_data.json')]
        total_items = 0
        data_volumes = {}
        
        for file in data_files:
            file_path = os.path.join(self.results_dir, file)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        count = len(data)
                        data_type = file.replace('_data.json', '')
                        data_volumes[data_type] = count
                        total_items += count
            except:
                pass
        
        html += f"""
        <h2>📊 Summary Statistics</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(data_files)}</div>
                <div class="stat-label">Data Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_items}</div>
                <div class="stat-label">Total Items</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(data_volumes)}</div>
                <div class="stat-label">Data Types</div>
            </div>
        </div>
        
        <h2>📈 Data Volume by Type</h2>
        <table>
            <tr>
                <th>Data Type</th>
                <th>Number of Items</th>
            </tr>
"""
        
        for data_type, count in data_volumes.items():
            html += f"""
            <tr>
                <td>{data_type.upper()}</td>
                <td>{count}</td>
            </tr>
"""
        
        html += """
        </table>
        
        <h2>⚙️ Configuration</h2>
"""
        
        # Add configuration info
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            html += f"""
        <table>
            <tr>
                <th>Setting</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Min Workers</td>
                <td>{config.get('min_workers', 'N/A')}</td>
            </tr>
            <tr>
                <td>Max Workers</td>
                <td>{config.get('max_workers', 'N/A')}</td>
            </tr>
            <tr>
                <td>Total Tasks</td>
                <td>{len(config.get('tasks', []))}</td>
            </tr>
            <tr>
                <td>Proxies</td>
                <td>{len(config.get('proxies', []))}</td>
            </tr>
        </table>
"""
        except:
            html += "<p>❌ Could not load configuration</p>"
        
        html += """
    </div>
</body>
</html>
"""
        return html

    def list_data_files(self):
        """List all data files"""
        print("\n📂 Data Files")
        
        if not os.path.exists(self.results_dir):
            print("❌ No data directory found.")
            return
        
        files = os.listdir(self.results_dir)
        json_files = [f for f in files if f.endswith('.json')]
        csv_files = [f for f in files if f.endswith('.csv')]
        
        if json_files:
            print("\n📄 JSON Files:")
            for file in json_files:
                file_path = os.path.join(self.results_dir, file)
                size = os.path.getsize(file_path)
                print(f"  📄 {file} ({size} bytes)")
        
        if csv_files:
            print("\n📊 CSV Files:")
            for file in csv_files:
                file_path = os.path.join(self.results_dir, file)
                size = os.path.getsize(file_path)
                print(f"  📊 {file} ({size} bytes)")

    def clean_old_data(self):
        """Clean old data files"""
        print("\n🗑️  Clean Old Data")
        
        if not os.path.exists(self.results_dir):
            print("❌ No data directory found.")
            return
        
        try:
            files = os.listdir(self.results_dir)
            data_files = [f for f in files if f.endswith(('.json', '.csv'))]
            
            if not data_files:
                print("❌ No data files to clean.")
                return
            
            print(f"📁 Found {len(data_files)} data files")
            confirm = input("Are you sure you want to delete all data files? (y/N): ").strip().lower()
            
            if confirm == 'y':
                for file in data_files:
                    file_path = os.path.join(self.results_dir, file)
                    os.remove(file_path)
                print("✅ All data files deleted!")
            else:
                print("❌ Cleanup cancelled.")
                
        except Exception as e:
            print(f"❌ Error cleaning data: {e}")

    def export_data(self):
        """Export data in different formats"""
        print("\n📤 Export Data")
        print("⚠️  Data is already available in JSON format in src/data/")
        print("You can access the files directly or use the data visualization features.")

    def search_data(self):
        """Search through scraped data"""
        print("\n🔍 Search Data")
        
        if not os.path.exists(self.results_dir):
            print("❌ No data directory found.")
            return
        
        search_term = input("Enter search term: ").strip().lower()
        if not search_term:
            print("❌ No search term provided.")
            return
        
        data_files = [f for f in os.listdir(self.results_dir) if f.endswith('_data.json')]
        
        if not data_files:
            print("❌ No data files found.")
            return
        
        print(f"\n🔍 Searching for '{search_term}'...")
        found_items = []
        
        for file in data_files:
            file_path = os.path.join(self.results_dir, file)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            # Search in title, summary, and other text fields
                            searchable_text = ""
                            for key, value in item.items():
                                if isinstance(value, str):
                                    searchable_text += value.lower() + " "
                            
                            if search_term in searchable_text:
                                found_items.append({
                                    'file': file,
                                    'item': item
                                })
            except Exception as e:
                print(f"❌ Error reading {file}: {e}")
        
        if found_items:
            print(f"\n✅ Found {len(found_items)} items:")
            for i, found in enumerate(found_items[:10]):  # Show first 10 results
                item = found['item']
                title = item.get('title', 'No title')
                print(f"  {i+1}. {title} ({found['file']})")
            
            if len(found_items) > 10:
                print(f"  ... and {len(found_items) - 10} more results")
        else:
            print("❌ No items found.")

    def system_status(self):
        """Show system status"""
        print("\n🔧 System Status")
        
        # Check configuration
        print("\n📋 Configuration:")
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                print(f"  ✅ Config file: {self.config_file}")
                print(f"  📝 Tasks: {len(config.get('tasks', []))}")
                print(f"  🔧 Min workers: {config.get('min_workers', 'N/A')}")
                print(f"  🔧 Max workers: {config.get('max_workers', 'N/A')}")
                print(f"  🌐 Proxies: {len(config.get('proxies', []))}")
            except Exception as e:
                print(f"  ❌ Config file error: {e}")
        else:
            print(f"  ❌ Config file missing: {self.config_file}")
        
        # Check data directory
        print("\n📁 Data Directory:")
        if os.path.exists(self.results_dir):
            files = os.listdir(self.results_dir)
            data_files = [f for f in files if f.endswith(('.json', '.csv'))]
            print(f"  ✅ Data directory: {self.results_dir}")
            print(f"  📄 Data files: {len(data_files)}")
        else:
            print(f"  ❌ Data directory missing: {self.results_dir}")
        
        # Check dependencies
        print("\n📦 Dependencies:")
        try:
            import selenium
            print("  ✅ Selenium")
        except ImportError:
            print("  ❌ Selenium")
        
        try:
            import scrapy
            print("  ✅ Scrapy")
        except ImportError:
            print("  ❌ Scrapy")
        
        try:
            import matplotlib
            print("  ✅ Matplotlib")
        except ImportError:
            print("  ❌ Matplotlib")
        
        try:
            import seaborn
            print("  ✅ Seaborn")
        except ImportError:
            print("  ❌ Seaborn")

    def view_tasks(self):
        """View current tasks"""
        print("\n📋 Current Tasks")
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            tasks = config.get('tasks', [])
            
            if not tasks:
                print("❌ No tasks configured.")
                return
            
            print(f"\n📋 Total tasks: {len(tasks)}")
            
            for i, task in enumerate(tasks):
                print(f"\n{i+1}. {task['type'].upper()} Task")
                print(f"   URL: {task['url']}")
                print(f"   Priority: {task['priority']}")
                print(f"   Type: {task['type']}")
                
        except Exception as e:
            print(f"❌ Error reading tasks: {e}")

    def schedule_scraping(self):
        """Schedule scraping tasks"""
        print("\n🎯 Schedule Scraping")
        print("⚠️  Scheduling feature not yet implemented.")
        print("You can use cron jobs or system schedulers to run the CLI automatically.")

    def show_completion_summary(self):
        """Show completion summary"""
        print("\n✅ Scraping Completed!")
        
        if os.path.exists(self.results_dir):
            data_files = [f for f in os.listdir(self.results_dir) if f.endswith('_data.json')]
            total_items = 0
            
            for file in data_files:
                file_path = os.path.join(self.results_dir, file)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            count = len(data)
                            data_type = file.replace('_data.json', '')
                            print(f"  📄 {data_type.upper()}: {count} items")
                            total_items += count
                except:
                    pass
            
            print(f"\n📊 Total items scraped: {total_items}")
        
        print("\n💡 Next steps:")
        print("  - View reports and analytics (Option 3)")
        print("  - Manage your data (Option 4)")
        print("  - Generate visualizations (Option 3 > 4)") 