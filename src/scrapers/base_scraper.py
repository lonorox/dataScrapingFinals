from src.scrapers.Master import Master
from src.scrapers.Task import Task
import src.utils.configs as con
from multiprocessing import Queue, Manager



if __name__ == '__main__':
    task_queue = Queue()
    result_queue = Queue()
    manager = Manager()
    worker_status = manager.dict()

    tasks = con.generate_tasks()
    tasks = [Task(i,tasks[i]["priority"],tasks[i]["url"],tasks[i]["type"],tasks[i].get("search_word")) for i in range(len(tasks))]
    master = Master(task_queue=task_queue, result_queue=result_queue, worker_status=worker_status)
    master.run(tasks)

