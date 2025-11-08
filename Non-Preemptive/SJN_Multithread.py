import threading
import itertools

processes = [
    {"pid": "P1", "arrival": 0, "burst": 7},
    {"pid": "P2", "arrival": 2, "burst": 4},
    {"pid": "P3", "arrival": 4, "burst": 1},
    {"pid": "P4", "arrival": 5, "burst": 4},
]

pending = []
cv = threading.Condition()
counter = itertools.count()
producers_done = False

def submit_process(proc):
    with cv:
        p = dict(proc)
        p["seq"] = next(counter)
        pending.append(p)
        cv.notify()

def worker_sjn():
    time = 0
    completed = []
    print("Execution order:")

    while True:
        with cv:
            current = None

            while True:
                if pending:
                    available = [p for p in pending if p["arrival"] <= time]
                    if available:
                        available.sort(key=lambda p: (p["burst"], p["arrival"], p["seq"]))
                        current = available[0]
                        pending.remove(current)
                        break
                    else:
                        next_arrival = min(p["arrival"] for p in pending)
                        if time < next_arrival:
                            time = next_arrival
                            continue

                if producers_done:
                    current = None
                    break
                cv.wait()

        if current is None:
            break

        start = time
        waiting = time - current["arrival"]
        time += current["burst"]
        end = time
        current["waiting"] = waiting
        completed.append(current)

        print(f"{current['pid']} (Waiting={waiting}, Start={start}, End={end})")

    if completed:
        avg_wait = sum(p["waiting"] for p in completed) / len(completed)
        print(f"\nAverage Waiting Time: {avg_wait:.2f}")

producers = []
for proc in processes:
    t = threading.Thread(target=submit_process, args=(proc,))
    t.start()
    producers.append(t)

worker = threading.Thread(target=worker_sjn)
worker.start()

for t in producers:
    t.join()

with cv:
    producers_done = True
    cv.notify_all()

worker.join()
