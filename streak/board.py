"""连胜看板：按真实时间窗口记录胜负,统计当前连胜与最长连胜。

实现要点:
- 每个玩家维护一个按到达顺序排列的对局双端队列,统计时按窗口下界回收过期对局;
- 当前连胜与胜场段(run)长度随写入、回收增量维护,最长连胜用懒删除堆取最大值;
- 同一个 req_id 只计一次,重复上报直接忽略;
- work_count 只随写入、回收与统计次数线性增长,不做全量扫描。

假设同一玩家的对局按 at_ms 非递减顺序到达(实时上报场景)。
"""

from collections import deque
from heapq import heappop, heappush


class _PlayerBoard:
    """单个玩家的窗口内增量状态。"""

    __slots__ = (
        "times",
        "wins",
        "current",
        "runs",
        "run_len",
        "heap",
        "next_run_id",
        "prev_win",
    )

    def __init__(self):
        self.times = deque()
        self.wins = deque()
        self.current = 0
        self.runs = deque()   # [run_id, length],窗口内胜场段,按时间先后
        self.run_len = {}     # run_id -> 当前长度,堆懒删除的依据
        self.heap = []        # (-length, run_id),取最长连胜
        self.next_run_id = 0
        self.prev_win = False


class Board:
    """战绩台账。"""

    def __init__(self, window_ms):
        self.window_ms = window_ms
        self.players = {}
        self.seen = set()
        self.work = 0

    def record(self, req_id, player, win, at_ms):
        """记一场对局,win 为 True、False 或 None(平局)。重复 req_id 直接忽略。"""
        if req_id in self.seen:
            return False
        self.seen.add(req_id)
        state = self.players.get(player)
        if state is None:
            state = self.players[player] = _PlayerBoard()
        self.work += 1
        state.times.append(at_ms)
        state.wins.append(win)
        if win is True:
            state.current += 1
            if state.prev_win:
                run_id, length = state.runs[-1]
                length += 1
                state.runs[-1][1] = length
                state.run_len[run_id] = length
                heappush(state.heap, (-length, run_id))
            else:
                run_id = state.next_run_id
                state.next_run_id += 1
                state.runs.append([run_id, 1])
                state.run_len[run_id] = 1
                heappush(state.heap, (-1, run_id))
        else:
            state.current = 0
        state.prev_win = win is True
        return True

    def _evict(self, state, cutoff):
        """回收 at_ms 早于 cutoff 的对局,边界(cutoff 本身)保留。"""
        times = state.times
        wins = state.wins
        while times and times[0] < cutoff:
            times.popleft()
            win = wins.popleft()
            self.work += 1
            if win is True:
                run_id, length = state.runs[0]
                length -= 1
                if length:
                    state.runs[0][1] = length
                    state.run_len[run_id] = length
                    heappush(state.heap, (-length, run_id))
                else:
                    state.runs.popleft()
                    del state.run_len[run_id]
        if state.current > len(times):
            state.current = len(times)

    def stats(self, player, now_ms):
        """返回窗口 [now_ms - window_ms, now_ms] 内的 current / best / games。"""
        self.work += 1
        state = self.players.get(player)
        if state is None:
            return {"current": 0, "best": 0, "games": 0}
        self._evict(state, now_ms - self.window_ms)
        best = 0
        heap = state.heap
        while heap:
            neg_length, run_id = heap[0]
            if state.run_len.get(run_id) == -neg_length:
                best = -neg_length
                break
            heappop(heap)
        return {"current": state.current, "best": best, "games": len(state.times)}

    def work_count(self):
        return self.work
