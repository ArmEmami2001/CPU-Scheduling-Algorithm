from dataclasses import dataclass

@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    remaining: int = 0

    def __post_init__(self):
        self.remaining = self.burst


def round_robin(processes, quantum):
    processes = sorted(processes, key=lambda p: p.arrival)
    ready = []
    schedule = []
    time = 0
    i = 0

    while i < len(processes) or ready:
        while i < len(processes) and processes[i].arrival <= time:
            ready.append(processes[i])
            i += 1

        if not ready:
            time = processes[i].arrival
            continue

        current = ready.pop(0)
        run_time = min(quantum, current.remaining)
        start = time
        end = time + run_time
        schedule.append((current.pid, start, end))
        time = end
        current.remaining -= run_time

        while i < len(processes) and processes[i].arrival <= time:
            ready.append(processes[i])
            i += 1

        if current.remaining > 0:
            ready.append(current)

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
    sched = round_robin(processes, q)
    print("Schedule (pid, start, end):")
    for s in sched:
        print(s)
    summarize(processes, sched)
