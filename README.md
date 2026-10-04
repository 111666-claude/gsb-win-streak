# win-streak

连胜看板：按真实时间窗口记录胜负，统计当前连胜与最长连胜，只用 Python 标准库。

```
python3 -m streak.cli --sample window
python3 -m streak.cli --sample draw
python3 -m streak.cli --sample dup
python3 -m streak.cli --sample table
python3 -m streak.cli --sample work
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **时间窗口**：只统计 `[now_ms - window_ms, now_ms]` 内的对局，正好等于窗口边界算在内，窗口外必须回收。
- **平局**：`win` 为 None 表示平局，平局打断连胜，但既不算胜利也不算失败。
- **当前连胜**：窗口内从最后一场往前连续胜利的场数。
- **最长连胜**：窗口内最长的一段连续胜利场数。
- **幂等**：同一个 `req_id` 只计一次，重复上报不改变任何统计。
- **代价**：统计不许全扫全部记录，`work_count()` 不随记录数乘统计次数增长；100 万场对局每秒 10 万次统计。

## 输出契约（不改格式）

```
games=.. current=..
current=..
work=..
player  games  current  best   （--sample table 的对齐表格）
```

## 目录

```
streak/board.py      窗口统计与连胜计算
streak/cli.py        命令行入口与表格渲染
tests/test_board.py  unittest 用例
```
