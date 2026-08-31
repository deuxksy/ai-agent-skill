#!/usr/bin/env python3
"""풀가동 구간 집계 — 램프 제외, Transaction parent(URL 컬럼이 null) 제외, HTTP 요청 기준.

parent 판별은 라벨 '→' 포함 여부가 아닌 URL 필드로 한다 — 2-4처럼 화살표 없는
TX 이름("2.4 FAQ 생성")에서도 정확히 제외된다 (2026-08-31 2배 과대 집계 수정).
"""
import csv
import statistics
import sys

URL_COL = 13  # 표준 JMeter CSV 14번째 필드(0-based 13): ...,grpThreads,allThreads,URL,Latency,...


def main():
    path, ramp = sys.argv[1], int(sys.argv[2]) * 1000
    d = list(csv.reader(open(path, encoding="utf-8")))[1:]
    t0 = int(d[0][0])
    full = [r for r in d if int(r[0]) >= t0 + ramp
            and len(r) > URL_COL and r[URL_COL] not in ("", "null")]
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
