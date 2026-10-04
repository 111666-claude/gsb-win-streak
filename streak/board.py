"""连胜看板：按真实时间窗口记录胜负，统计当前连胜与最长连胜。

缺陷：窗口从不滑动（历史全留）、平局被当成胜利、同一个 req_id 重复计数、
每次统计全扫全部记录。
"""


class Board:
    """战绩台账。"""

    def __init__(self, window_ms):
        self.window_ms = window_ms
        self.records = []
        self.work = 0

    def record(self, req_id, player, win, at_ms):
        """记一场对局，win 为 True、False 或 None（平局）。缺陷：不查 req_id。"""
        self.records.append((req_id, player, win, at_ms))
        return True

    def stats(self, player, now_ms):
        """返回 current / best / games。缺陷：窗口不滑、平局算胜、全扫记录。"""
        self.work += len(self.records)
        games = 0
        run = 0
        best = 0
        for _, name, win, _ in self.records:
            if name != player:
                continue
            games += 1
            if win is not False:
                run += 1
                if run > best:
                    best = run
            else:
                run = 0
        return {"current": run, "best": best, "games": games}

    def work_count(self):
        return self.work
