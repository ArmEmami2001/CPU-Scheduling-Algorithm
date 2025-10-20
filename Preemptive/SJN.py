processes = [
    {"pid": "P1", "arrival": 0, "burst": 7},
    {"pid": "P2", "arrival": 2, "burst": 4},
    {"pid": "P3", "arrival": 4, "burst": 1},
    {"pid": "P4", "arrival": 5, "burst": 4}
]

completed = []
time = 0
print("Execution order:")

while processes:
    available = [p for p in processes if p["arrival"] <= time]
    if not available:
        time += 1
        continue

    current = min(available, key=lambda x: x["burst"])
    processes.remove(current)
    start = time
    current["waiting"] = time - current["arrival"]
    time += current["burst"]
    completed.append(current)
    print(f"{current['pid']} (Waiting={current['waiting']}, Start={start}, End={time})")

avg_wait = sum(p["waiting"] for p in completed) / len(completed)

print(f"\nAverage Waiting Time: {avg_wait:.2f}")

