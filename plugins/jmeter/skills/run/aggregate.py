#!/usr/bin/env python3
"""풀가동 구간 집계 — 램프 제외, Transaction parent(라벨에 '→' 포함) 제외, HTTP 요청 기준."""
import csv
import statistics
import sys


def main():
    path, ramp = sys.argv[1], int(sys.argv[2]) * 1000
    d = list(csv.reader(open(path, encoding="utf-8")))[1:]
    t0 = int(d[0][0])
    full = [r for r in d if int(r[0]) >= t0 + ramp and "→" not in r[2]]
    if not full:
        print("풀가동 구간 샘플 없음", file=sys.stderr)
        return 2
    span = (int(full[-1][0]) - int(full[0][0])) / 1000
    el = sorted(int(r[1]) for r in full)
    err = sum(1 for r in full if r[7] == "false")
    sd = statistics.stdev(el) if len(el) > 1 else 0.0
    print(f"풀가동 {span:.0f}s: {len(full)} req = {len(full)/span:.1f} req/s | "
          f"Err {100*err/len(full):.2f}% | p95 {el[int(len(el)*.95)]}ms | stdev {sd:.1f}ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
