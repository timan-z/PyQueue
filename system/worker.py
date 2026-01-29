import random
import time

from models.task import Task
from models.queue import Queue
from enums.TaskStatus import TaskStatus
from enums.TaskType import TaskType

"""
This file is probably where the difference in ergonomics begins to really show between
PyQueue (Python) and SpringQueue (Java).

1.
- My Worker.java in SpringQueue (base) implements Runnable, which functionally gives it a run() method
which my file overrode. (This also let the executor know how to execute it).
- Python doesn't have a Runnable interface, executors here work with callable functions, objects callable
w/ __call__ and bound methods. Keep the same idea of Workers being units of executable work, just no more inheritance / implementing things.
2.
In Worker.java, QueueService was automatically wired into Worker since it is a @Service and SpringBoot
has the dependency injection feature. Nothing does that explicitly in Python, instead here dependencies
are just passed explicitly. (No framework magic, just references -- which is closer to Go's explicit dependency passing).

IMPORTANT-NOTE:
- When I do time.sleep(int_val), that int_val is seconds unlike Thread.sleep(int_val) in Java where in_tval is miliseconds.
-- Hence why I'm doing / 1000 for all the values within time.sleep() now...

***
NOTE: When the first pass pre-refactoring edition of PyQueue (base) is finished, make a
document that's dedicated to comparing differences between PyQueue and SpringQueue (base).
I did a bad job of documenting little details like this in SpringQueue and SpringQueuePro. Fix it here.
"""

class Worker:
    # 0. Equivalent of Worker.java's constructor:
    def __init__(self, task: Task, queue: Queue):
        self.task = task    # The unit of work being processed.
        self.queue = queue  # Coordination service (for retries / re-enqueue)

    # 1. Translating - public void run() {...}:
    def run(self):
        try:
            self.task.attempts = self.task.attempts + 1
            self.task.status = TaskStatus.INPROGRESS
            print(f"[Worker] Processing Task {self.task.t_id} (Attempt {self.task.attempts}, Type: {self.task.t_type})")
            self.handle_task_type(self.task)
        except Exception as e:
            print(f"[Worker] Task {self.task.t_id} failed due to error: {e}")
            self.task.status = TaskStatus.FAILED

    # 2. Translating - private void handleTaskType(Task t) throws InterruptedException {...}:
    def handle_task_type(self, task: Task):
        match task.t_type:
            case TaskType.FAIL:
                self.handle_fail_type(task)
            case TaskType.FAILABS:
                self.handle_absolute_fail(task)
            case TaskType.EMAIL:
                self.simulate_work(task, 2000, str(TaskType.EMAIL))
            case TaskType.REPORT:
                self.simulate_work(task, 5000, str(TaskType.REPORT))
            case TaskType.DATACLEANUP:
                self.simulate_work(task, 3000, str(TaskType.DATACLEANUP))
            case TaskType.SMS:
                self.simulate_work(task, 1000, str(TaskType.SMS))
            case TaskType.NEWSLETTER:
                self.simulate_work(task, 4000, str(TaskType.NEWSLETTER))
            case TaskType.TAKESLONG:
                self.simulate_work(task, 10000, str(TaskType.TAKESLONG))
            case _:
                self.simulate_work(task, 2000, "Undefined")

    #3. Translating - private void handleFailType(Task t) throws InterruptedException {...}:
    def handle_fail_type(self, task: Task):
        success_chance = 0.25
        random_float = random.uniform(0, 1)
        if random_float <= success_chance:
            time.sleep(2000 / 1000)
            task.status = TaskStatus.COMPLETED
            print(f"[Worker] Task {task.t_id} (Type: {task.t_type}) - 0.25 success rate on retry) completed")
        else:
            time.sleep(1000 / 1000)
            task.status = TaskStatus.FAILED
            if task.attempts < task.max_retries:
                print(f"[Worker] Task {task.t_id} (Type: {task.t_type} - 0.25 success rate on retry) failed! Retrying...")
                self.queue.enqueue(task)
            else:
                print(f"[Worker] Task {task.t_id} (Type: {task.t_type} - 0.25 success rate on retry) failed permanently!")

    # 4. Translating - private void handleAbsoluteFail(Task t) throws InterruptedException {...}:
    def handle_absolute_fail(self, task: Task):
        # DEBUG: Not sure if I should enforce a "private" equivalence here?
        time.sleep(1000 / 1000)
        task.status = TaskStatus.FAILED
        if task.attempts < task.max_retries:
            print(f"[Worker] Task {task.t_id} (Type: FAILABS) failed! Retrying...")
            self.queue.enqueue(task)
        else:
            print(f"[Worker] Task {task.t_id} (Type: FAILABS) failed permanently!")

    # 5. Translating - private void simulateWork(Task t, int durationMs, String type) throws InterruptedException {...}:
    def simulate_work(self, task: Task, duration_ms: int, t_type: str):
        # DEBUG: Not sure if I should enforce a "private" equivalence here?
        time.sleep(duration_ms / 1000)
        task.status = TaskStatus.COMPLETED
        print(f"[Worker] Task {task.t_id} (Type: {t_type}) complete")
