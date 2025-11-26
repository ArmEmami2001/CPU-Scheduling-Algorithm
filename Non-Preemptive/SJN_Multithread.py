import threading
import time

processes = [
    {"pid": "P1", "arrival": 0, "execution": 5},
    {"pid": "P2", "arrival": 1, "execution": 3},
    {"pid": "P3", "arrival": 2, "execution": 8},
    {"pid": "P4", "arrival": 3, "execution": 2},
]

class Process(threading.Thread):
    def __init__(self, pid, burst):
        threading.Thread.__init__(self, name=pid)
        self.pid = pid
        self.burst = burst

    def run(self):
        print(f"\nRunning {self.pid}")
        for i in range(self.burst, 0, -1):
            print(f"Process {self.pid} remaining time: {i}")
            time.sleep(0.2)
        print(f"Process {self.pid} finished.\n")


def sjn_scheduler(process_list):
    print("\n--- SJN (Shortest Job Next) Scheduling Start ---\n")

    process_list = sorted(process_list, key=lambda p: p["arrival"])

    current_time = 0
    ready_queue = []
    finished = []

    waiting_times = {}
    turnaround_times = {}

    while len(finished) < len(process_list):

        for p in process_list:
            if p not in ready_queue and p not in finished:
                if p["arrival"] <= current_time:
                    ready_queue.append(p)

        if not ready_queue:
            current_time += 1
            continue

        next_proc = min(ready_queue, key=lambda x: x["execution"])

        pid = next_proc["pid"]
        arrival = next_proc["arrival"]
        burst = next_proc["execution"]
        
        start_time = current_time
        waiting_time = start_time - arrival
        waiting_times[pid] = waiting_time

        print(f"Dispatching {pid} | Burst = {burst} | Waiting = {waiting_time}")

        proc = Process(pid, burst)
        proc.start()
        proc.join()

        current_time += burst

        turnaround_times[pid] = waiting_time + burst


        finished.append(next_proc)
        ready_queue.remove(next_proc)

    avg_wait = sum(waiting_times.values()) / len(waiting_times)
    avg_tat = sum(turnaround_times.values()) / len(turnaround_times)

    print("\n--- SJN Scheduling Complete ---\n")
    print("Waiting Times:", waiting_times)
    print(f"Average Waiting Time = {avg_wait:.2f}")
    print(f"Average Turnaround Time = {avg_tat:.2f}\n")


# MAIN
if __name__ == "__main__":
    sjn_scheduler(processes)
