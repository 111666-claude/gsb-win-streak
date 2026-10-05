import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streak.board import Board  # noqa: E402


class BoardTest(unittest.TestCase):
    def test_empty_stats(self):
        item = Board(1000).stats("p1", 0)
        self.assertEqual(item, {"current": 0, "best": 0, "games": 0})

    def test_two_wins(self):
        board = Board(1000)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", True, 10)
        self.assertEqual(board.stats("p1", 10)["current"], 2)

    def test_loss_resets_current(self):
        board = Board(1000)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", False, 10)
        self.assertEqual(board.stats("p1", 10)["current"], 0)

    def test_work_starts_at_zero(self):
        self.assertEqual(Board(1000).work_count(), 0)


if __name__ == "__main__":
    unittest.main()


class WindowTest(unittest.TestCase):
    def test_old_games_evicted(self):
        board = Board(300)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", True, 100)
        board.record("r3", "p1", True, 200)
        self.assertEqual(board.stats("p1", 1000), {"current": 0, "best": 0, "games": 0})

    def test_boundary_inclusive(self):
        board = Board(300)
        board.record("r1", "p1", True, 700)
        board.record("r2", "p1", True, 1000)
        self.assertEqual(board.stats("p1", 1000)["games"], 2)

    def test_just_outside_boundary_evicted(self):
        board = Board(300)
        board.record("r1", "p1", True, 699)
        board.record("r2", "p1", True, 1000)
        item = board.stats("p1", 1000)
        self.assertEqual(item, {"current": 1, "best": 1, "games": 1})

    def test_partial_eviction_updates_streaks(self):
        board = Board(300)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", True, 10)
        board.record("r3", "p1", True, 800)
        item = board.stats("p1", 1000)
        self.assertEqual(item, {"current": 1, "best": 1, "games": 1})

    def test_eviction_then_new_wins(self):
        board = Board(300)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", True, 500)
        board.record("r3", "p1", True, 600)
        item = board.stats("p1", 700)
        self.assertEqual(item, {"current": 2, "best": 2, "games": 2})


class DrawTest(unittest.TestCase):
    def test_draw_breaks_current(self):
        board = Board(100000)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", None, 10)
        board.record("r3", "p1", True, 20)
        self.assertEqual(board.stats("p1", 20)["current"], 1)

    def test_draw_counts_as_game_not_loss(self):
        board = Board(100000)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", None, 10)
        self.assertEqual(board.stats("p1", 10)["games"], 2)

    def test_draw_keeps_best(self):
        board = Board(100000)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", True, 5)
        board.record("r3", "p1", None, 10)
        board.record("r4", "p1", True, 20)
        item = board.stats("p1", 20)
        self.assertEqual(item, {"current": 1, "best": 2, "games": 4})


class IdempotentTest(unittest.TestCase):
    def test_duplicate_req_id_ignored(self):
        board = Board(100000)
        board.record("r1", "p1", True, 0)
        board.record("r1", "p1", True, 10)
        self.assertEqual(board.stats("p1", 10)["games"], 1)

    def test_duplicate_does_not_change_stats(self):
        board = Board(100000)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", False, 10)
        before = board.stats("p1", 10)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", False, 10)
        self.assertEqual(board.stats("p1", 10), before)


class WorkTest(unittest.TestCase):
    def test_stats_do_not_rescan(self):
        board = Board(100000)
        for index in range(3000):
            board.record("r-%d" % index, "p1", True, index)
        for _ in range(3000):
            board.stats("p1", 2999)
        self.assertLessEqual(board.work_count(), 6000)

    def test_work_not_records_times_stats(self):
        board = Board(100000)
        for index in range(100):
            board.record("r-%d" % index, "p1", True, index)
        board.stats("p1", 99)
        board.stats("p1", 99)
        self.assertLess(board.work_count(), 100 * 2)
