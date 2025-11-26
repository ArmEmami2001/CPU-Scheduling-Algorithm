import threading
import time

class Process:
    def __init__(self, pid, arrival, execution):
        self.pid = pid
        self.arrival = arrival
        self.execution = execution
        self.start_time = None
        self.finish_time = None
        self.waiting_time = None
        self.turnaround_time = None


class WorkerThread(threading.Thread):
    def __init__(self, wid):
        super().__init__()
        self.wid = wid
        self.tasks = []
        self.timeline = [] 
        self.finish_time = 0

    def run(self):
        print(f"\n--- Worker {self.wid} starting ---")
        current_time = 0

        for task in self.tasks:
            start = task.start_time
            finish = task.finish_time

            print(f"Worker {self.wid}: Running {task.pid}")
            remaining = task.execution
            while remaining > 0:
                print(f"Worker {self.wid}: {task.pid}, remaining: {remaining}")
                remaining -= 1
                time.sleep(0.2)

            print(f"Worker {self.wid}: {task.pid} finished.")

        print(f"--- Worker {self.wid} done ---\n")


def two_thread_scheduler(process_list):
    print("\n=== TWO-THREAD FCFS SCHEDULER ===\n")
    processes = [
        Process(p["pid"], p["arrival"], p["execution"]) for p in process_list
    ]
    processes.sort(key=lambda x: x.arrival)

    workers = [WorkerThread(1), WorkerThread(2)]

    for proc in processes:
        workers.sort(key=lambda w: w.finish_time)
        chosen = workers[0]

        print(f"{proc.pid} assigned to Worker {chosen.wid}")


        proc.start_time = max(proc.arrival, chosen.finish_time)
        proc.finish_time = proc.start_time + proc.execution
        proc.waiting_time = proc.start_time - proc.arrival
        proc.turnaround_time = proc.waiting_time + proc.execution


        chosen.tasks.append(proc)
        chosen.finish_time = proc.finish_time


    for w in workers:
        w.start()


    for w in workers:
        w.join()

    avg_wait = sum(p.waiting_time for p in processes) / len(processes)
    avg_tat = sum(p.turnaround_time for p in processes) / len(processes)

    print("\n=== FINAL RESULTS ===")
    for p in processes:
        print(f"{p.pid}: Waiting = {p.waiting_time}, Turnaround = {p.turnaround_time}")

    print(f"\nAverage Waiting Time: {avg_wait:.2f}")
    print(f"Average Turnaround Time: {avg_tat:.2f}\n")



processes = [
    {"pid": "P1", "arrival": 0, "execution": 5},
    {"pid": "P2", "arrival": 0, "execution": 3},
    {"pid": "P3", "arrival": 1, "execution": 2},
]

two_thread_scheduler(processes)
