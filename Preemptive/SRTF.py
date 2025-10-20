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

Schedule = List[Tuple[str, int, int]]

def merge_idle(schedule: Schedule) -> Schedule:
    out: Schedule = []
    for pid, s, e in schedule:
        if out and pid == "IDLE" and out[-1][0] == "IDLE":
            out[-1] = ("IDLE", out[-1][1], e)
        else:
            out.append((pid, s, e))
    return out

def summarize(schedule: Schedule, procs: Dict[str, Process]) -> Dict[str, Dict[str, float]]:
    finish: Dict[str, int] = {}
    for pid, s, e in schedule:
        if pid == "IDLE":
            continue
        finish[pid] = e
    tat, wt = {}, {}
    for pid, p in procs.items():
        ct = finish.get(pid)
        if ct is None:
            tat[pid] = wt[pid] = 0
        else:
            tat[pid] = ct - p.arrival
            wt[pid] = tat[pid] - p.burst
    return {
        "per_process": {pid: {"finish": finish.get(pid), "turnaround": tat[pid], "waiting": wt[pid]} for pid in procs},
        "averages": {
            "avg_turnaround": sum(tat.values()) / len(procs) if procs else 0.0,
            "avg_waiting": sum(wt.values()) / len(procs) if procs else 0.0,
        },
    }

def gantt(schedule: Schedule) -> str:
    if not schedule:
        return "(empty)"
    blocks = []
    for pid, s, e in schedule:
        w = max(1, e - s)
        blocks.append((
            "┌" + "─" * (2*w) + "┐",
            "│" + pid.center(2*w) + "│",
            "└" + "─" * (2*w) + "┘",
            s, e
        ))
    line1 = "".join(b[0] for b in blocks)
    line2 = "".join(b[1] for b in blocks)
    line3 = "".join(b[2] for b in blocks)
    ticks = [blocks[0][3]] + [b[4] for b in blocks]
    return f"{line1}\n{line2}\n{line3}\n" + " ".join(str(t) for t in ticks)

def srtf_quantum(processes: List[Process], quantum: int = 2) -> Schedule:
    procs = [Process(p.pid, p.arrival, p.burst) for p in processes]
    procs.sort(key=lambda p: (p.arrival, p.pid))

    schedule: Schedule = []
    ready: List[Process] = []
    t = 0
    i = 0

    def push_arrivals_up_to(time_now: int):
        nonlocal i
        while i < len(procs) and procs[i].arrival <= time_now:
            ready.append(procs[i])
            i += 1

    def pick_shortest_remaining() -> Optional[int]:
        if not ready:
            return None

        best_idx = min(range(len(ready)), key=lambda k: (ready[k].remaining, ready[k].arrival, ready[k].pid))
        return best_idx

    while True:

        push_arrivals_up_to(t)

        if not ready and i >= len(procs):
            break

        if not ready:
            next_arrival = procs[i].arrival
            schedule.append(("IDLE", t, next_arrival))
            t = next_arrival
            push_arrivals_up_to(t)

        idx = pick_shortest_remaining()
        if idx is None:
            continue
        current = ready.pop(idx)
        start = t

        slice_left = min(quantum, current.remaining)

        while slice_left > 0:

            next_arrival = procs[i].arrival if i < len(procs) else None

            if next_arrival is None:
                run_to = t + slice_left
            else:
                run_to = min(t + slice_left, next_arrival)
            ran = run_to - t
            current.remaining -= ran
            t = run_to
            slice_left -= ran

            push_arrivals_up_to(t)
            if slice_left == 0:
                break

        schedule.append((current.pid, start, t))

        if current.remaining > 0:
            ready.append(current)

    return merge_idle(schedule)

if __name__ == "__main__":

    processes = [
        Process("P1", 0, 8),
        Process("P2", 1, 4),
        Process("P3", 2, 9),
        Process("P4", 3, 5),
    ]
    q = 2
    sched = srtf_quantum(processes, quantum=q)

    print(f"=== SRTF with Quantum (q={q}) ===")
    print("Schedule:", sched)
    print()
    print(gantt(sched))
    print()
    summary = summarize(sched, {p.pid: p for p in processes})
    print("Per-process:")
    header = f"{'Process':<10} {'Finish':<8} {'Turnaround':<12} {'Waiting':<8}"
    print(header)
    print("-" * len(header))
    for pid, data in summary["per_process"].items():
        print(f"{pid:<10} {data['finish']:<8} {data['turnaround']:<12} {data['waiting']:<8}")
    print()
    print("Averages:", summary["averages"])
