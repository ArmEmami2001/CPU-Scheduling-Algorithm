processes = [
    {"pid": "P1", "arrival": 0, "execution": 5},
    {"pid": "P2", "arrival": 1, "execution": 3},
    {"pid": "P3", "arrival": 2, "execution": 8}
]

processes.sort(key=lambda x: x["arrival"])

time = 0
print("Execution order:")
for p in processes:
    if time < p["arrival"]:
        time = p["arrival"]
    p["waiting"] = time - p["arrival"]
    start = time
    time += p["execution"]
    print(f"{p['pid']} (Waiting={p['waiting']}) , (Start={start}, End={time})")

avg_wait = sum(p["waiting"] for p in processes) / len(processes)

print(f"\nAverage Waiting Time: {avg_wait:.2f}")
