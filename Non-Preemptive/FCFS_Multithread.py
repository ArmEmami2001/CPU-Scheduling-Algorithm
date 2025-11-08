import threading
import heapq
import itertools

processes = [
    {"pid": "P1", "arrival": 0, "execution": 5},
    {"pid": "P2", "arrival": 0,  "execution": 3},
    {"pid": "P3", "arrival": 0,  "execution": 8},
]

ready_heap = []
counter = itertools.count()
lock = threading.Lock()
cv = threading.Condition(lock)
producers_done = False

def submit_process(proc):
    with cv:
        seq = next(counter)
        heapq.heappush(ready_heap, (proc["arrival"], seq, proc["pid"], proc["execution"]))
        cv.notify()

def worker_fcfs():
    time = 0
    schedule = []

    with cv:
        while True:
            while not ready_heap and not producers_done:
                cv.wait()

            if not ready_heap and producers_done:
                break

            arrival, seq, pid, burst = heapq.heappop(ready_heap)

            if time < arrival:
                time = arrival
            waiting = time - arrival
            start = time
            time += burst
            end = time

            schedule.append((pid, waiting, start, end))
            print(f"{pid} (Waiting={waiting}) , (Start={start}, End={end})")

    if schedule:
        avg_wait = sum(w for _, w, _, _ in schedule) / len(schedule)
        print(f"\nAverage Waiting Time: {avg_wait:.2f}")

producer_threads = []
for proc in processes:
    t = threading.Thread(target=submit_process, args=(proc,))
    t.start()
    producer_threads.append(t)

worker = threading.Thread(target=worker_fcfs)
worker.start()

for t in producer_threads:
    t.join()

with cv:
    producers_done = True
    cv.notify_all()

worker.join()
