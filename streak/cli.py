"""命令行入口：跑连胜看板样例，支持对齐表格输出。"""

import argparse

from .board import Board


def build_parser():
    parser = argparse.ArgumentParser(prog="win-streak", description="连胜看板")
    parser.add_argument("--sample", default="window", help="window / draw / dup / table / work")
    return parser


def render(rows):
    """把若干行统计渲染成对齐表格。"""
    header = ("player", "games", "current", "best")
    widths = [len(item) for item in header]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(str(cell)))
    lines = ["  ".join(header[i].ljust(widths[i]) for i in range(len(header))).rstrip()]
    for row in rows:
        lines.append("  ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)).rstrip())
    return "\n".join(lines)


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "window":
        board = Board(300)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", True, 100)
        board.record("r3", "p1", True, 200)
        item = board.stats("p1", 1000)
        print("games=%d current=%d" % (item["games"], item["current"]))
    elif args.sample == "draw":
        board = Board(100000)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", None, 10)
        board.record("r3", "p1", True, 20)
        print("current=%d" % board.stats("p1", 20)["current"])
    elif args.sample == "dup":
        board = Board(100000)
        board.record("r1", "p1", True, 0)
        board.record("r1", "p1", True, 10)
        print("games=%d" % board.stats("p1", 10)["games"])
    elif args.sample == "table":
        board = Board(100000)
        for index in range(3):
            board.record("r-%d" % index, "p1", True, index * 10)
        board.record("r-9", "p2", False, 40)
        rows = []
        for name in ("p1", "p2"):
            item = board.stats(name, 100)
            rows.append((name, item["games"], item["current"], item["best"]))
        print(render(rows))
    elif args.sample == "work":
        board = Board(100000)
        for index in range(3000):
            board.record("r-%d" % index, "p1", True, index)
        for index in range(3000):
            board.stats("p1", 2999)
        print("work=%d" % board.work_count())
    else:
        raise SystemExit("需要 --sample window|draw|dup|table|work")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
