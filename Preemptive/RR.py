# rr.py
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    remaining: int = field(init=False)

    def __post_init__(self):
        self.remaining = self.burst

Schedule = List[Tuple[str, int, int]]  # (pid, start, end)

def merge_idle(schedule: Schedule) -> Schedule:
    out: Schedule = []
    for pid, s, e in schedule:
        if out and pid == "IDLE" and out[-1][0] == "IDLE":
            out[-1] = ("IDLE", out[-1][1], e)
        else:
            out.append((pid, s, e))
    return out

def summarize(schedule: Schedule, procs: Dict[str, Process]) -> Dict[str, Dict[str, float]]:
    first_start: Dict[str, int] = {}
    finish: Dict[str, int] = {}
    for pid, s, e in schedule:
        if pid == "IDLE":
            continue
        first_start.setdefault(pid, s)
        finish[pid] = e

    waiting: Dict[str, int] = {}
    tat: Dict[str, int] = {}
    for pid, p in procs.items():
        f = finish.get(pid)
        if f is None:
            waiting[pid] = 0
            tat[pid] = 0
        else:
            tat[pid] = f - p.arrival
            waiting[pid] = tat[pid] - p.burst

    avg_wait = sum(waiting.values()) / len(procs) if procs else 0.0
    avg_tat = sum(tat.values()) / len(procs) if procs else 0.0

    return {
        "per_process": {pid: {"waiting": waiting[pid], "turnaround": tat[pid], "finish": finish.get(pid)} for pid in procs},
        "averages": {"avg_waiting": avg_wait, "avg_turnaround": avg_tat},
    }

def gantt(schedule: Schedule) -> str:
    if not schedule:
        return "(empty)"
    blocks = []
    for pid, s, e in schedule:
        width = max(1, e - s)
        blocks.append(("┌" + "─" * (2*width) + "┐",
                       "│" + pid.center(2*width) + "│",
                       "└" + "─" * (2*width) + "┘",
                       s, e))
    line1 = "".join(b[0] for b in blocks)
    line2 = "".join(b[1] for b in blocks)
    line3 = "".join(b[2] for b in blocks)
    ticks = [blocks[0][3]] + [b[4] for b in blocks]
    return f"{line1}\n{line2}\n{line3}\n" + " ".join(str(t) for t in ticks)

def print_per_process_table(per_process: Dict[str, Dict[str, float]]) -> None:
    if not per_process:
        print("No process data available.")
        return
    headers = ["Process ID", "Waiting Time", "Turnaround Time", "Finish Time"]
    table = []
    for pid, data in sorted(per_process.items()):
        row = [pid, data["waiting"], data["turnaround"], data.get("finish", "N/A")]
        table.append(row)
    print("+------------+--------------+------------------+-------------+")
    print("| Process ID | Waiting Time | Turnaround Time | Finish Time |")
    print("+------------+--------------+------------------+-------------+")
    for row in table:
        print(f"| {row[0]:<10} | {row[1]:<12} | {row[2]:<16} | {row[3]:<11} |")
    print("+------------+--------------+------------------+-------------+")

def round_robin(processes: List[Process], quantum: int = 2) -> Schedule:
    procs = [Process(p.pid, p.arrival, p.burst) for p in processes]
    procs.sort(key=lambda p: (p.arrival, p.pid))
    schedule: Schedule = []
    ready: List[Process] = []
    t = 0
    i = 0

    while i < len(procs) or ready:
        while i < len(procs) and procs[i].arrival <= t:
            ready.append(procs[i]); i += 1

        if not ready:
            nxt = procs[i].arrival
            schedule.append(("IDLE", t, nxt))
            t = nxt
            continue

        p = ready.pop(0)
        slice_time = min(quantum, p.remaining)
        start = t
        end = t + slice_time
        schedule.append((p.pid, start, end))
        t = end
        p.remaining -= slice_time

        while i < len(procs) and procs[i].arrival <= t:
            ready.append(procs[i]); i += 1

        if p.remaining > 0:
            ready.append(p)

    return merge_idle(schedule)

if __name__ == "__main__":
    processes = [
        Process("P1", 0, 8),
        Process("P2", 1, 4),
        Process("P3", 2, 9),
        Process("P4", 3, 5),
    ]
    sched = round_robin(processes, quantum=2)
    print("=== Round Robin (q=2) ===")
    print("Schedule:", sched)
    print(gantt(sched))
    summary = summarize(sched, {p.pid: p for p in processes})
    print("Per-process:")
    print_per_process_table(summary["per_process"])
    print("Averages:", summary["averages"])
