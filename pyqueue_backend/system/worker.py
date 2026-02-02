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
    """
    Basically a (Worker) Thread - executes a single Task/Job.
    One Worker instance == one execution attempt lifecycle.
    """

    # 0. Constructor: Equivalent of Worker.java's constructor:
    def __init__(self, task: Task, queue: Queue) -> None:
        self.task: Task = task    # The unit of work being processed.
        self.queue: Queue = queue  # Coordination service (for retries / re-enqueue)

    # 1. Entry point for Executor: Translating - public void run() {...}:
    def run(self) -> None:
        """
        Executor entrypoint. Mutates task state and then delegates execution logic.
        """
        try:
            self.task.attempts = self.task.attempts + 1
            self.task.status = TaskStatus.INPROGRESS
            print(f"[Worker] Processing Task {self.task.t_id} (Attempt {self.task.attempts}, Type: {self.task.t_type})")
            self._handle_task_type(self.task)

        except RuntimeError as e:
            print(f"[Worker] Runtime error in task {self.task.t_id}: {e}")
            self.task.status = TaskStatus.FAILED

        except Exception as e:
            print(f"[Worker] Unexpected failure in task {self.task.t_id}: {e}")
            self.task.status = TaskStatus.FAILED

    # 2. Dispatch based on task type: Translating - private void handleTaskType(Task t) throws InterruptedException {...}:
    def _handle_task_type(self, task: Task) -> None:
        match task.t_type:
            case TaskType.FAIL:
                self._handle_fail_type(task)
            case TaskType.FAILABS:
                self._handle_absolute_fail(task)
            case TaskType.EMAIL:
                self._simulate_work(task, 2000)
            case TaskType.REPORT:
                self._simulate_work(task, 5000)
            case TaskType.DATACLEANUP:
                self._simulate_work(task, 3000)
            case TaskType.SMS:
                self._simulate_work(task, 1000)
            case TaskType.NEWSLETTER:
                self._simulate_work(task, 4000)
            case TaskType.TAKESLONG:
                self._simulate_work(task, 10000)
            case _:
                self._simulate_work(task, 2000)

    #3. Fail-with-retry: Translating - private void handleFailType(Task t) throws InterruptedException {...}:
    def _handle_fail_type(self, task: Task) -> None:
        success_chance: float = 0.25
        random_float = random.uniform(0, 1)
        if random_float <= success_chance:
            self._sleep_ms(2000)
            task.status = TaskStatus.COMPLETED
            print(f"[Worker] Task {task.t_id} (Type: {task.t_type}) - 0.25 success rate on retry) completed")
        else:
            self._sleep_ms(1000)
            self._retry_or_fail(task)
            # Old code factored out (of this and _handle_absolute_fail):
            """
            task.status = TaskStatus.FAILED
            if task.attempts < task.max_retries:
                print(f"[Worker] Task {task.t_id} (Type: {task.t_type} - 0.25 success rate on retry) failed! Retrying...")
                self.queue.enqueue(task)
            else:
                print(f"[Worker] Task {task.t_id} (Type: {task.t_type} - 0.25 success rate on retry) failed permanently!")
            """

    # 4. Translating - private void handleAbsoluteFail(Task t) throws InterruptedException {...}:
    def _handle_absolute_fail(self, task: Task) -> None:
        self._sleep_ms(1000)
        self._retry_or_fail(task)

    # 5. Translating - private void simulateWork(Task t, int durationMs, String type) throws InterruptedException {...}:
    def _simulate_work(self, task: Task, duration_ms: int) -> None:
        # DEBUG: Not sure if I should enforce a "private" equivalence here?
        self._sleep_ms(duration_ms)
        task.status = TaskStatus.COMPLETED
        print(f"[Worker] Task {task.t_id} (Type: {task.t_type}) complete")

    # Helper Method(s):
    # Shared retry logic for _handle_fail_type and _handle_absolute_fail:
    def _retry_or_fail(self, task: Task) -> None:
        task.status = TaskStatus.FAILED
        if task.attempts < task.max_retries:
            print(f"[Worker] Task {task.t_id} (Type: {task.t_type}) failed! Retrying...")
            self.queue.enqueue(task)
        else:
            print(f"[Worker] Task {task.t_id} (Type: {task.t_type}) failed permanently!")

    # Sleep method (/1000 conversion needed to bridge gap between Java and Python):
    @staticmethod
    def _sleep_ms(ms: int) -> None:
        time.sleep(ms / 1000)
