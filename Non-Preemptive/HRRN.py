processes = [
    {"pid": "P1", "arrival": 0, "execution": 3},
    {"pid": "P2", "arrival": 2, "execution": 6},
    {"pid": "P3", "arrival": 4, "execution": 4},
    {"pid": "P4", "arrival": 6, "execution": 5}
]

completed = []
time = 0
print("Execution order:")

while processes:
    available = [p for p in processes if p["arrival"] <= time]
    if not available:
        time += 1
        continue

    for p in available:
        waiting = time - p["arrival"]
        p["rr"] = (waiting / p["execution"]) + 1

    current = max(available, key=lambda x: x["rr"])
    processes.remove(current)
    start = time
    current["waiting"] = time - current["arrival"]
    time += current["execution"]
    completed.append(current)
    print(f"{current['pid']} (RR={current['rr']:.2f}, Waiting={current['waiting']} , Start={start}, End={time})")

avg_wait = sum(p["waiting"] for p in completed) / len(completed)

print(f"\nAverage Waiting Time: {avg_wait:.2f}")

