"""连胜看板：按真实时间窗口记录胜负，统计当前连胜与最长连胜。

每个玩家维护一条按时间排列的事件队列，窗口外的对局在统计时从队首回收；
连续胜利按“连胜段”增量维护，最长连胜用惰性失效的最大堆保存，
每条对局一生只进出队列一次，统计调用本身均摊 O(1)。
"""

import heapq
from collections import deque


class _PlayerState:
    def __init__(self):
        self.events = deque()
        self.games = 0
        self.runs = deque()
        self.lengths = {}
        self.next_run = 0
        self.last_run = None
        self.best_heap = []


class Board:
    """战绩台账。"""

    def __init__(self, window_ms):
        self.window_ms = window_ms
        self._req_ids = set()
        self._players = {}
        self.work = 0

    def record(self, req_id, player, win, at_ms):
        """记一场对局，win 为 True、False 或 None（平局）。重复 req_id 忽略。"""
        if req_id in self._req_ids:
            return False
        self._req_ids.add(req_id)
        self.work += 1
        state = self._players.setdefault(player, _PlayerState())
        state.events.append((at_ms, win))
        state.games += 1
        if win is True:
            if state.last_run is None:
                run_id = state.next_run
                state.next_run += 1
                state.runs.append(run_id)
                state.lengths[run_id] = 0
                state.last_run = run_id
            else:
                run_id = state.last_run
            state.lengths[run_id] += 1
            heapq.heappush(state.best_heap, (-state.lengths[run_id], run_id))
        else:
            state.last_run = None
        return True

    def stats(self, player, now_ms):
        """返回 current / best / games，只统计 [now_ms-window_ms, now_ms]。"""
        self.work += 1
        state = self._players.get(player)
        if state is None:
            return {"current": 0, "best": 0, "games": 0}
        cutoff = now_ms - self.window_ms
        while state.events and state.events[0][0] < cutoff:
            _, win = state.events.popleft()
            self.work += 1
            state.games -= 1
            if win is True:
                run_id = state.runs[0]
                state.lengths[run_id] -= 1
                if state.lengths[run_id] == 0:
                    del state.lengths[run_id]
                    state.runs.popleft()
                    if state.last_run == run_id:
                        state.last_run = None
        while state.best_heap:
            neg_length, run_id = state.best_heap[0]
            if state.lengths.get(run_id) == -neg_length:
                break
            heapq.heappop(state.best_heap)
        current = state.lengths[state.last_run] if state.last_run is not None else 0
        best = -state.best_heap[0][0] if state.best_heap else 0
        return {"current": current, "best": best, "games": state.games}

    def work_count(self):
        return self.work
