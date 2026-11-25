"""محاكي بسيط: FCFS و Round Robin. التشغيل: python main.py input.txt"""
import sys


def read_processes(filename):
    processes = []
    q = None
    with open(filename, encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, 1):
            line = line.split("#")[0].strip()
            if not line:
                continue
            parts = line.split()
            try:
                if parts[0] == "q":
                    if len(parts) != 2 or q is not None:
                        raise ValueError("Use one final q line, such as: q 2")
                    q = int(parts[1])
                    if q <= 0:
                        raise ValueError("q must be greater than zero")
                else:
                    if len(parts) != 4 or q is not None:
                        raise ValueError("Expected: P1 arrival burst priority, before q")
                    name = parts[0]
                    if not name.startswith("P") or not name[1:].isascii() or not name[1:].isdigit() or int(name[1:]) < 1:
                        raise ValueError("Names must be P1, P2, ...")
                    if name != "P" + str(int(name[1:])):
                        raise ValueError("Do not use leading zeros in process names")
                    arrival, burst, priority = map(int, parts[1:])
                    if arrival < 0 or burst <= 0:
                        raise ValueError("arrival must be >= 0 and burst > 0")
                    for p in processes:
                        if p["name"] == name:
                            raise ValueError("Duplicate process: " + name)
                    processes.append({"name": name, "arrival": arrival,
                                      "burst": burst, "priority": priority})
            except ValueError as error:
                raise ValueError(f"Line {line_number}: {error}") from None
    if not processes or q is None:
        raise ValueError("The file must contain processes and a final q line")
    return processes, q


def arrival_order(p):
    # عند تساوي الوصول: P2 قبل P10، وليس ترتيباً أبجدياً.
    return p["arrival"], int(p["name"][1:])


def fcfs(processes):
    time = 0
    gantt = []
    for p in sorted(processes, key=arrival_order):
        if time < p["arrival"]:
            gantt.append(("Idle", time, p["arrival"]))
            time = p["arrival"]
        gantt.append((p["name"], time, time + p["burst"]))
        time += p["burst"]
    return gantt


def round_robin(processes, q):
    if q <= 0:
        raise ValueError("q must be greater than zero")
    waiting = sorted(processes, key=arrival_order)
    remaining = {p["name"]: p["burst"] for p in processes}
    ready = []
    gantt = []
    time = 0
    while waiting or ready:
        if not ready and time < waiting[0]["arrival"]:
            gantt.append(("Idle", time, waiting[0]["arrival"]))
            time = waiting[0]["arrival"]
        while waiting and waiting[0]["arrival"] <= time:
            ready.append(waiting.pop(0))
        p = ready.pop(0)
        name = p["name"]
        duration = min(q, remaining[name])
        gantt.append((name, time, time + duration))
        time += duration
        remaining[name] -= duration
        # الوافدون أثناء الشريحة وعند نهايتها يدخلون قبل إعادة العملية الحالية.
        while waiting and waiting[0]["arrival"] <= time:
            ready.append(waiting.pop(0))
        if remaining[name] > 0:
            ready.append(p)
    return gantt


def calculate_results(processes, gantt):
    results = []
    for p in processes:
        # أول مقطع هو أول تشغيل، وآخر مقطع يعطينا زمن الانتهاء.
        segments = [s for s in gantt if s[0] == p["name"]]
        start = segments[0][1]
        finish = segments[-1][2]
        turnaround = finish - p["arrival"]
        waiting = turnaround - p["burst"]
        response = start - p["arrival"]
        results.append([p["name"], finish, turnaround, waiting, response])
    return results


def print_results(title, gantt, results):
    print("\n===", title, "===")
    print("Gantt:", end=" ")
    for name, start, end in gantt:
        print(f"| {name} {start}-{end}", end=" ")
    print("|")
    print(f'{"Process":<10}{"Finish":>10}{"Turnaround":>14}{"Waiting":>12}{"Response":>12}')
    for name, finish, turnaround, waiting, response in results:
        print(f"{name:<10}{finish:>10}{turnaround:>14}{waiting:>12}{response:>12}")
    averages = []
    for column in (2, 3, 4):
        total = sum(row[column] for row in results)
        averages.append(total / len(results))
    print(f"Average turnaround: {averages[0]:.2f}")
    print(f"Average waiting:    {averages[1]:.2f}")
    print(f"Average response:   {averages[2]:.2f}")
    return averages


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    try:
        processes, q = read_processes(filename)
        gantt_fcfs = fcfs(processes)
        gantt_rr = round_robin(processes, q)
        a = print_results("FCFS", gantt_fcfs, calculate_results(processes, gantt_fcfs))
        b = print_results(f"RR (q = {q})", gantt_rr, calculate_results(processes, gantt_rr))
        print("\n=== Comparison (lower is better) ===")
        for i, metric in enumerate(["Turnaround", "Waiting", "Response"]):
            if a[i] < b[i]:
                winner = "FCFS is better"
            elif b[i] < a[i]:
                winner = "RR is better"
            else:
                winner = "Equal"
            print(f"{metric}: {winner} (FCFS {a[i]:.2f}, RR {b[i]:.2f})")
    except (OSError, ValueError) as error:
        print("Error:", error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
