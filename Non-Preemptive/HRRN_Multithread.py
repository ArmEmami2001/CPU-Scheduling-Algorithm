import threading
import time

processes = [
    {"pid": "P1", "arrival": 0, "execution": 5},
    {"pid": "P2", "arrival": 2, "execution": 3},
    {"pid": "P3", "arrival": 4, "execution": 8},
]


class Process(threading.Thread):
    def __init__(self, pid, burst):
        threading.Thread.__init__(self, name=pid)
        self.pid = pid
        self.burst = burst

    def run(self):
        print(f"\nRunning {self.pid}")
        for i in range(self.burst, 0, -1):
            print(f"Process: {self.pid}, remaining time: {i}")
            time.sleep(0.2)
        print(f"Process {self.pid} finished.\n")

def hrrn_scheduler(process_list):
    print("\n--- HRRN Scheduling Start ---\n")

    current_time = 0
    ready = []
    finished = []


    waiting_times = {}


    process_list = sorted(process_list, key=lambda p: p["arrival"])

    while len(finished) < len(process_list):


        for p in process_list:
            if p not in ready and p not in finished:
                if p["arrival"] <= current_time:
                    ready.append(p)

        if not ready:
            current_time += 1
            continue


        for p in ready:
            wait = current_time - p["arrival"]
            burst = p["execution"]
            p["hrrn"] = (wait + burst) / burst

        next_proc = max(ready, key=lambda x: x["hrrn"])

        start_time = current_time
        waiting_time = start_time - next_proc["arrival"]
        waiting_times[next_proc["pid"]] = waiting_time

        print(f"Dispatching {next_proc['pid']} (HRRN = {next_proc['hrrn']:.2f})")
        print(f"Waiting Time for {next_proc['pid']}: {waiting_time}")
        proc = Process(next_proc["pid"], next_proc["execution"])
        proc.start()
        proc.join()  
        current_time += next_proc["execution"]
        finished.append(next_proc)
        ready.remove(next_proc)


    total_wait = sum(waiting_times.values())
    avg_wait = total_wait / len(waiting_times)

    print("\n--- HRRN Scheduling Complete ---\n")
    print("Waiting Times:", waiting_times)
    print(f"Average Waiting Time = {avg_wait:.2f} time units\n")


if __name__ == "__main__":
    hrrn_scheduler(processes)
