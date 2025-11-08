from dataclasses import dataclass
import threading
from collections import deque
import itertools

@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    remaining: int = 0

    def __post_init__(self):
        self.remaining = self.burst


def round_robin_mt(processes, quantum):
    cv = threading.Condition()
    pending = []
    ready = deque()
    seq_counter = itertools.count()
    schedule = []
    producers_done = {"flag": False}

    def submit_process(p: Process):
        with cv:
            obj = Process(p.pid, p.arrival, p.burst)
            obj.seq = next(seq_counter)
            pending.append(obj)
            cv.notify()

    def worker():
        time = 0
        def enqueue_arrivals():
            arrived = [x for x in pending if x.arrival <= time]
            if arrived:
                arrived.sort(key=lambda x: (x.arrival, x.seq))
                for x in arrived:
                    pending.remove(x)
                    ready.append(x)

        with cv:
            print("Schedule (pid, start, end):")
            while True:
                enqueue_arrivals()

                if ready:
                    current = ready.popleft()
                    run_time = min(quantum, current.remaining)
                    start = time
                    end = time + run_time
                    schedule.append((current.pid, start, end))
                    time = end
                    current.remaining -= run_time

                    enqueue_arrivals()

                    if current.remaining > 0:
                        ready.append(current)
                    continue

                if pending:
                    next_arrival = min(p.arrival for p in pending)
                    if time < next_arrival:
                        time = next_arrival
                    continue

                if producers_done["flag"]:
                    break
                cv.wait()

    producer_threads = []
    for p in processes:
        t = threading.Thread(target=submit_process, args=(p,))
        t.start()
        producer_threads.append(t)

    w = threading.Thread(target=worker)
    w.start()

    for t in producer_threads:
        t.join()
    with cv:
        producers_done["flag"] = True
        cv.notify_all()

    w.join()

    return schedule


def summarize(processes, schedule):
    finish = {}
    for pid, s, e in schedule:
        finish[pid] = e

    print("\nProcess\tArrival\tBurst\tFinish\tTurnaround\tWaiting")
    total_wait = total_tat = 0
    for p in processes:
        tat = finish[p.pid] - p.arrival
        wait = tat - p.burst
        total_wait += wait
        total_tat += tat
        print(f"{p.pid}\t{p.arrival}\t{p.burst}\t{finish[p.pid]}\t{tat}\t\t{wait}")
    n = len(processes)
    print(f"Average Waiting: {total_wait/n:.2f}")


if __name__ == "__main__":
    processes = [
        Process("P1", 0, 8),
        Process("P2", 1, 4),
        Process("P3", 2, 9),
        Process("P4", 3, 5),
    ]
    q = 2
    sched = round_robin_mt(processes, q)
    for s in sched:
        print(s)
    summarize(processes, sched)
