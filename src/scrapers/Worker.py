import json
from src.utils.logger import log
from src.scrapers.Task import Result
from src.utils.RateLimiter import RateLimiter
import src.utils.configs as con
from src.scrapers.ScraperFactory import ScraperFactory
from src.data.processors import data_output_manager
from src.data.models import Article, ScrapingResult

import time
import random
import os

class Worker:

    def __init__(self,name,task_queue,result_queue, stop,worker_status):
        self.name = name
        self.taskQueue = task_queue
        self.resultQueue = result_queue
        self.stop_flag = stop
        self.worker_status = worker_status
        self.rate_limiter = RateLimiter(max_requests_per_second=1)
        self.max_retries = 3
        log.info(f'worker {name} was initialized')

    def _process(self, task):
        start_time = time.time()
        log.info(f"process {self.name} started at {start_time}")
        for i in range(self.max_retries):
            try:
                # Use Factory pattern to create appropriate scraper
                if not ScraperFactory.validate_task_type(task.type):
                    raise ValueError(f"Unsupported task type: {task.type}")
                
                self.scraper = ScraperFactory.create_scraper(task.type, self.rate_limiter, task.search_word)
                log.info(f"scraping {self.name} {task.type} at {task.url}")
                
                log.info(f"scraping started")
                articles = self.scraper.scrape(task.url)

                processing_time = time.time() - start_time
                log.info(f"scraping completed in {processing_time} seconds, save")
                
                # Convert Article objects to dictionaries for storage
                data = []
                for article in articles:
                    article_dict = article.to_dict()
                    article_dict['worker_id'] = self.name
                    article_dict['task_id'] = task.id
                    data.append(article_dict)
                
                return Result(
                    task_id=task.id,
                    worker_name=self.name,
                    source_type=task.type,
                    data=data,
                    success=True,
                    processing_time=processing_time
                )
            except Exception as e:
                log.error(f"Task {task.id} failed: {str(e)}, retrying")
                time.sleep(2)

        log.error(f"Task {task.id} failed, returning it to task queue")
        processing_time = time.time() - start_time
        self.taskQueue.put(task)
        return Result(
            task_id=task.id,
            worker_name=self.name,
            source_type=task.type,
            data=[],
            success=False,
            error_message=str(e),
            processing_time=processing_time
        )

    def save_result(self, data):
        log.info(f"saving result")
        # Use data output manager to save worker results
        data_output_manager.save_worker_result(self.name, data)

    def run(self):
        while self.stop_flag == 0:
            try:
                self.worker_status[self.name] = "idle"
                task = self.taskQueue.get(timeout=1)
                if task is None:
                    break
                log.info(f"Worker {self.name} started task {task.id}")
                self.worker_status[self.name] = "busy"
                result = self._process(task)
                self.save_result(result.data)
                self.resultQueue.put(result)
                self.worker_status[self.name] = "idle"
            except Exception as e:
                self.worker_status[self.name] = "idle"
                continue
        log.info(f"Worker {self.name} finished")