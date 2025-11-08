import threading
import itertools

processes = [
    {"pid": "P1", "arrival": 0, "execution": 3},
    {"pid": "P2", "arrival": 2, "execution": 6},
    {"pid": "P3", "arrival": 4, "execution": 4},
    {"pid": "P4", "arrival": 6, "execution": 5},
]

pending = []
counter = itertools.count()
cv = threading.Condition()
producers_done = False

def submit_process(proc):
    with cv:
        p = dict(proc)
        p["seq"] = next(counter)
        pending.append(p)
        cv.notify()

def worker_hrrn():
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
                        for p in available:
                            waiting = time - p["arrival"]
                            p["rr"] = (waiting / p["execution"]) + 1

                        available.sort(key=lambda p: (p["rr"], -p["arrival"], -p["seq"]), reverse=True)
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

        waiting = time - current["arrival"]
        start = time
        time += current["execution"]
        end = time
        current["waiting"] = waiting

        completed.append(current)
        print(f"{current['pid']} (RR={current['rr']:.2f}, Waiting={waiting} , Start={start}, End={end})")

    if completed:
        avg_wait = sum(p["waiting"] for p in completed) / len(completed)
        print(f"\nAverage Waiting Time: {avg_wait:.2f}")

producers = []
for proc in processes:
    t = threading.Thread(target=submit_process, args=(proc,))
    t.start()
    producers.append(t)

worker = threading.Thread(target=worker_hrrn)
worker.start()

for t in producers:
    t.join()

with cv:
    producers_done = True
    cv.notify_all()

worker.join()
