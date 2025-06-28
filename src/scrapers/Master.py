import csv
import os
import time
from multiprocessing import Queue, Process, Manager
from threading import Thread
import glob

from src.utils.logger import log
from src.scrapers.Worker import Worker
from src.data.processors import data_output_manager, consolidate_worker_data, save_consolidated_data, cleanup_worker_files
from src.data.models import Article, ScrapingResult, ScrapingStats, ScrapingTask
from src.data.database import Database
import json

# create master
class Master:
    def __init__(self, task_queue=None, result_queue=None, worker_status=None, n=3):
        self.task_queue = task_queue if task_queue is not None else Queue()
        self.result_queue = result_queue if result_queue is not None else Queue()
        self.worker_status = worker_status if worker_status is not None else Manager().dict()
        
        # Initialize database manager
        self.db_manager = Database()
        
        # Initialize scraping stats
        self.stats = ScrapingStats()
        self.stats.start_timer()
        
        # min and max workers, configurable
        with open("config.json", "r") as f:
            config = json.load(f)
        # change number of workers if it does not fit in pre specified range
        if n < config["min_workers"]:
            self.workers = config["min_workers"]
        elif n > config["max_workers"]:
            self.workers = config["max_workers"]
        else:
            self.workers = n

        self.workers_queue = Queue()
        self.worker_list = []
        self.results = []
        self.number_of_Tasks = 0
        self.completed_tasks = 0
        self.stop = 0

    def __del__(self):
        """Cleanup database connection."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()

    def add_tasks(self, tasks):
        for task in tasks:
            self.task_queue.put(task)
            self.number_of_Tasks += 1
        log.info(f"Added {len(tasks)} tasks")

    def start_workers(self):
        #Start all worker processes
        log.info("Starting workers")
        for i in range(self.workers):
            worker = Worker(i, self.task_queue, self.result_queue, self.stop,self.worker_status)
            process = Process(target=worker.run)
            self.worker_list.append(process)
            process.start()

    def stop_workers(self):
        #Stop all worker processes
        log.info("Stopping workers")
        self.stop = 1

        for _ in range(self.workers):
            self.task_queue.put(None)

        # Wait for workers to finish
        for worker in self.worker_list:
            worker.join(timeout=5)
            if worker.is_alive():
                worker.terminate()

    def save_summary_to_csv(self,path = "summary"):
        log.info("Saving summary to csv")
        total = len(self.results)
        successes = sum(1 for r in self.results if r.success)
        failures = total - successes
        success_rate = (100 * successes / total) if total > 0 else 0
        avg_time = sum(r.processing_time for r in self.results) / total if total else 0
        
        # Use data output manager to save summary
        data_output_manager.save_summary_csv(self.results, f"{path}.csv")

    def collect_results(self):
        log.info("Collecting results")
        #Collect results from workers
        while self.completed_tasks < self.number_of_Tasks:
            try:
                result = self.result_queue.get(timeout=1.0)
                self.results.append(result)
                self.completed_tasks += 1

                if result.success:
                    log.info(f"Task {result.task_id} completed successfully "
                                f"by worker {result.worker_id} ({len(result.data)} items)")

                else:
                    log.warning(f"Task {result.task_id} failed: {result.error_message}")
                
                # Don't export combined results after each task - wait until all are done
            except:
                continue
        
        # Export combined results only after ALL tasks are completed
        self.export_combined_results()
        
        # progress report for task 10
        self.save_summary_to_csv()

    # def _save_articles_to_database(self, raw_data, source_type):
    #     """Convert raw data to Article objects and save to database."""
    #     try:
    #         articles = []
    #         for item in raw_data:
    #             try:
    #                 # Convert raw data to Article object
    #                 article = Article(
    #                     title=item.get('title', ''),
    #                     url=item.get('url', ''),
    #                     author=item.get('author'),
    #                     publication_date_datetime=item.get('publication_date_datetime'),
    #                     publication_date_readable=item.get('publication_date_readable'),
    #                     summary=item.get('summary'),
    #                     content=item.get('content'),
    #                     tags=item.get('tags', []),
    #                     source_type=source_type,
    #                     source=item.get('source'),
    #                     headline=item.get('headline'),
    #                     link=item.get('link'),
    #                     href=item.get('href'),
    #                     scraped_at=item.get('scraped_at'),
    #                     metadata=item.get('metadata', {})
    #                 )
    #                 articles.append(article)
    #             except Exception as e:
    #                 log.error(f"Error converting item to Article: {e}")
    #                 continue
    #
    #         # Save articles to database
    #         if articles:
    #             saved_count = self.db_manager.save_articles(articles)
    #             log.info(f"Saved {saved_count} articles to database for {source_type}")
    #
    #     except Exception as e:
    #         log.error(f"Error saving articles to database: {e}")

    def cleanup_worker_files(self):
        """Clean up individual worker files after combining"""
        try:
            # Use the new cleanup function from processors
            success = cleanup_worker_files("data_output")
            if success:
                log.info("Successfully cleaned up worker files")
            else:
                log.error("Failed to clean up worker files")
        except Exception as e:
            log.error(f"Error in cleanup_worker_files: {e}")
            # Fallback to original cleanup method
            self._fallback_cleanup_worker_files()

    def _fallback_cleanup_worker_files(self):
        """Fallback cleanup method"""
        import glob
        
        # Clean up any remaining worker files
        worker_files = glob.glob("data_output/worker_*.json")
        for file_path in worker_files:
            try:
                os.remove(file_path)
                log.info(f"Cleaned up worker file: {file_path}")
            except Exception as e:
                log.error(f"Error cleaning up {file_path}: {e}")

    def run(self,tasks):
        try:
            log.info("Starting workers")
            self.add_tasks(tasks)
            self.start_workers()
            thread = Thread(target=self.collect_results)
            thread.start()
            self.monitor()
            thread.join()
            
            # Finalize stats
            self.stats.end_timer()
            self.stats.successful_scrapes = sum(1 for r in self.results if r.success)
            self.stats.failed_scrapes = sum(1 for r in self.results if not r.success)
            self.stats.total_errors = sum(len(r.errors) if hasattr(r, 'errors') else 0 for r in self.results)
            
            # Save session stats
            # session_id = f"session_{int(time.time())}"
            # self.db_manager.(session_id, self.stats)
            
            # Export final results
            self.export_final_results()
            
            return self.results
        finally:
            self.stop_workers()
            # Cleanup is now handled in export_combined_results after all tasks complete

    def monitor(self):
        while self.completed_tasks < self.number_of_Tasks:
            log.info("Monitoring tasks...")
            # progress report for task 7
            completion = f"{(self.completed_tasks/self.number_of_Tasks)*100}% completed"
            print(completion)
            success =  sum(1 for r in self.results if r.success)
            successful_tasks = f"Successful tasks: {success}"
            failed_tasks = f"Failed tasks: {len(self.results) - success}"

            print(successful_tasks)
            print(failed_tasks)
            for wid, status in self.worker_status.items():
                print(f"Worker {wid} status: {status}")
            time.sleep(4)

    def export_combined_results(self):
        log.info("Exporting organized data by type")
        
        try:
            # Consolidate all worker files by type
            consolidated_data = consolidate_worker_data("data_output")
            
            # Save consolidated data to type-specific JSON files and combined CSV
            success = save_consolidated_data(consolidated_data, "data_output")
            self.db_manager.convert_csv_to_sqlite()
            if success:
                log.info("Successfully exported consolidated data")
                # Clean up worker files after successful consolidation
                cleanup_worker_files("data_output")
            else:
                log.error("Failed to export consolidated data")
                
        except Exception as e:
            log.error(f"Error in export_combined_results: {e}")
            # Fallback to original method if new method fails
            self._fallback_export_combined_results()

    def _fallback_export_combined_results(self):
        """Fallback method for exporting combined results"""
        log.info("Using fallback export method")
        
        # Organize data by type from results
        data_by_type = {}

        for r in self.results:
            for item in r.data:
                source_type = r.source_type
                if source_type not in data_by_type:
                    data_by_type[source_type] = []
                data_by_type[source_type].append(item)

        # Save data organized by type (JSON only) with append functionality
        for source_type, items in data_by_type.items():
            if items:
                data_output_manager.append_to_json(f"{source_type}_data.json", items)

        # Save combined CSV (all data from news, blog, and rss) with append functionality
        data_output_manager.save_combined_csv(data_by_type, "combined.csv")

        log.info(f"Fallback: Combined CSV saved with data from {len(data_by_type)} sources")

    def export_final_results(self):
        """Export final results using database data."""
        log.info("Exporting final results from database")
        
        try:
            # Get recent articles from database
            recent_articles = self.db_manager.get_recent_articles(limit=10000)
            
            if recent_articles:
                # Convert articles to dictionaries for export
                articles_data = [article.to_dict() for article in recent_articles]
                
                # Export to CSV
                data_output_manager.append_to_csv("final_combined.csv", articles_data)
                self.db_manager.convert_csv_to_sqlite("data_output/final_combined.csv")

                # Export database stats
                db_stats = self.db_manager.get_stats()
                with open("data_output/database_stats.json", "w") as f:
                    json.dump(db_stats, f, indent=2)
                
                log.info(f"Final export completed with {len(articles_data)} articles")
            
        except Exception as e:
            log.error(f"Error in final export: {e}")
