from collections import deque
from dataclasses import dataclass, field
from typing import List, Tuple, Dict

@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    remaining: int = field(init=False)
    runs: int = 0

    def __post_init__(self):
        self.remaining = self.burst

Schedule = List[Tuple[str, int, int]]  # (pid, start, end)

def rr_dynamic_n2(processes: List[Process]) -> Tuple[Schedule, Dict[str, Dict[str, int]]]:
    arrivals_list = sorted([(p.pid, p.arrival, p.burst) for p in processes],
                           key=lambda x: (x[1], x[0]))
    procs = {pid: Process(pid, at, bt) for pid, at, bt in arrivals_list}

    t = 0
    i = 0  
    q = deque()
    schedule: Schedule = []
    first_start: Dict[str, int] = {}
    finish: Dict[str, int] = {}

    while True:
        while i < len(arrivals_list) and arrivals_list[i][1] <= t:
            q.append(arrivals_list[i][0])
            i += 1

        if not q:
            if i >= len(arrivals_list):
                break 
            t = arrivals_list[i][1]
            continue

        pid = q.popleft()
        p = procs[pid]
        p.runs += 1
        quantum = 3 * (p.runs ** 2)

        start = t
        if pid not in first_start:
            first_start[pid] = start

        run = min(quantum, p.remaining)
        end = start + run

        schedule.append((pid, start, end))

        while i < len(arrivals_list) and arrivals_list[i][1] <= end:
            q.append(arrivals_list[i][0])
            i += 1

        p.remaining -= run
        t = end

        if p.remaining == 0:
            finish[pid] = end
        else:
            q.append(pid)


        if all(pp.remaining == 0 for pp in procs.values()):
            break


    stats: Dict[str, Dict[str, int]] = {}
    for pid, p in procs.items():
        at = p.arrival
        bt = p.burst
        st = first_start.get(pid, None)
        ct = finish.get(pid, None)
        tat = (ct - at) if ct is not None else None
        wt  = (tat - bt) if tat is not None else None  # == CT - (AT + BT)
        stats[pid] = {"arrival": at, "burst": bt, "start": st, "finish": ct, "turnaround": tat, "waiting": wt}

    return schedule, stats

def print_report(schedule: Schedule, stats: Dict[str, Dict[str, int]]):
    print("Execution order:")
    print(" → ".join(pid for pid, _, _ in schedule))

    print("\nSchedule (pid, start, end):")
    for seg in schedule:
        print(seg)


    print("\nPer-process times:")
    header = ("PID", "AT", "BT", "START", "FINISH", "TAT", "WT")
    print("{:>3} {:>4} {:>4} {:>6} {:>7} {:>4} {:>4}".format(*header))
    for pid in sorted(stats.keys()):
        s = stats[pid]
        at, bt = s["arrival"], s["burst"]
        st = s["start"] if s["start"] is not None else -1
        ct = s["finish"] if s["finish"] is not None else -1
        tat = s["turnaround"] if s["turnaround"] is not None else -1
        wt  = s["waiting"] if s["waiting"] is not None else -1
        print("{:>3} {:>4} {:>4} {:>6} {:>7} {:>4} {:>4}".format(pid, at, bt, st, ct, tat, wt))

    tats = [s["turnaround"] for s in stats.values() if s["turnaround"] is not None]
    wts  = [s["waiting"]    for s in stats.values() if s["waiting"]    is not None]
    avg_tat = sum(tats) / len(tats) if tats else 0.0
    avg_wt  = sum(wts)  / len(wts)  if wts  else 0.0
    print("\nAverages:")
    print(f"  Avg Turnaround: {avg_tat:.3f}")
    print(f"  Avg Waiting   : {avg_wt:.3f}")

if __name__ == "__main__":
    procs = [
        Process("P1", 0, 10),
        Process("P2", 7, 30),
        Process("P3", 3, 7),
        Process("P4", 20, 14),
        Process("P5", 15, 5),
        Process("P6", 4, 22),
        Process("P7", 10, 8),
    ]

    sched, stats = rr_dynamic_n2(procs)
    print_report(sched, stats)
