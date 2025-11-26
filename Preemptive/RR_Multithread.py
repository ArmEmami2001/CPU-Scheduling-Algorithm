import time
import threading
from collections import deque

class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        
        self.burst = burst
        self.remaining = burst
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0


class CPUCore:
    def __init__(self, cid):
        self.cid = cid
        self.current = None
        self.time_left = 0 


def rr_two_thread_scheduler(process_list, quantum=2):
    print("\n=== ROUND ROBIN (2 THREADS, QUANTUM = 2) ===\n")

    processes = [Process(p["pid"], p["arrival"], p["execution"]) for p in process_list]

    proc_map = {p.pid: p for p in processes}

    processes.sort(key=lambda x: x.arrival)

    ready = deque()

 
    cores = [CPUCore(1), CPUCore(2)]

    time_now = 0
    completed = 0
    n = len(processes)

    print("Simulation starting...\n")

    while completed < n:


        for p in processes:
            if p.arrival == time_now:
                ready.append(p)
                print(f"t={time_now}: {p.pid} arrives → added to ready queue")


        for core in cores:
            if core.current is None and ready:
                proc = ready.popleft()
                core.current = proc

                if proc.start_time is None:
                    proc.start_time = time_now

                core.time_left = min(quantum, proc.remaining)

                print(f"t={time_now}: Core {core.cid} starts {proc.pid} "
                      f"(remaining={proc.remaining})")


        for core in cores:
            if core.current:
                core.current.remaining -= 1
                core.time_left -= 1

                print(f"t={time_now}: Core {core.cid} executing {core.current.pid} "
                      f"(rem={core.current.remaining})")

                if core.current.remaining == 0:
                    core.current.finish_time = time_now + 1
                    print(f"t={time_now+1}: {core.current.pid} finished")
                    core.current = None
                    completed += 1

                elif core.time_left == 0:
                    print(f"t={time_now+1}: Quantum expired for {core.current.pid} "
                          "(preempted)")
                    ready.append(core.current)
                    core.current = None

        for p in ready:
            p.waiting_time += 1

        time_now += 1
        time.sleep(0.15)

    print("\n=== FINAL RESULTS ===")
    for p in processes:
        tat = p.finish_time - p.arrival - p.burst
        print(f"{p.pid}: Waiting={p.waiting_time}, Turnaround={tat}")

    avg_wait = sum(p.waiting_time for p in processes) / n
    avg_tat = sum((p.finish_time - p.arrival) for p in processes) / n

    print(f"\nAverage Waiting Time = {avg_wait:.2f}")
    print(f"Average Turnaround Time = {avg_tat:.2f}\n")


processes = [
    {"pid": "P1", "arrival": 0, "execution": 5},
    {"pid": "P2", "arrival": 0, "execution": 3},
    {"pid": "P3", "arrival": 1, "execution": 2},
]

rr_two_thread_scheduler(processes, quantum=2)
