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


class WindowTest(unittest.TestCase):
    def test_window_evicts_old_games(self):
        board = Board(300)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", True, 100)
        board.record("r3", "p1", True, 200)
        self.assertEqual(board.stats("p1", 1000), {"current": 0, "best": 0, "games": 0})

    def test_window_boundary_is_inclusive(self):
        board = Board(100)
        board.record("r1", "p1", True, 0)
        item = board.stats("p1", 100)
        self.assertEqual(item["games"], 1)
        self.assertEqual(item["current"], 1)
        self.assertEqual(board.stats("p1", 101)["games"], 0)

    def test_window_eviction_updates_best(self):
        board = Board(100)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", True, 10)
        board.record("r3", "p1", False, 20)
        board.record("r4", "p1", True, 30)
        self.assertEqual(board.stats("p1", 30)["best"], 2)
        self.assertEqual(board.stats("p1", 130), {"current": 1, "best": 1, "games": 1})

    def test_partial_run_eviction(self):
        board = Board(100)
        for index in range(3):
            board.record("r%d" % index, "p1", True, index * 10)
        self.assertEqual(board.stats("p1", 110), {"current": 2, "best": 2, "games": 2})


class DrawTest(unittest.TestCase):
    def test_draw_breaks_streak(self):
        board = Board(1000)
        board.record("r1", "p1", True, 0)
        board.record("r2", "p1", None, 10)
        board.record("r3", "p1", True, 20)
        item = board.stats("p1", 20)
        self.assertEqual(item["current"], 1)
        self.assertEqual(item["best"], 1)
        self.assertEqual(item["games"], 3)

    def test_draw_is_neither_win_nor_loss(self):
        board = Board(1000)
        board.record("r1", "p1", None, 0)
        self.assertEqual(board.stats("p1", 0), {"current": 0, "best": 0, "games": 1})


class DedupTest(unittest.TestCase):
    def test_duplicate_req_id_counted_once(self):
        board = Board(1000)
        self.assertTrue(board.record("r1", "p1", True, 0))
        self.assertFalse(board.record("r1", "p1", True, 10))
        item = board.stats("p1", 10)
        self.assertEqual(item["games"], 1)
        self.assertEqual(item["current"], 1)

    def test_same_req_id_across_players_counted_once(self):
        board = Board(1000)
        board.record("r1", "p1", True, 0)
        board.record("r1", "p2", True, 0)
        self.assertEqual(board.stats("p2", 0)["games"], 0)


class WorkTest(unittest.TestCase):
    def test_work_does_not_scale_with_records_times_stats(self):
        board = Board(100000)
        for index in range(3000):
            board.record("r-%d" % index, "p1", True, index)
        for _ in range(3000):
            board.stats("p1", 2999)
        self.assertLessEqual(board.work_count(), 6000)

    def test_repeated_stats_cost_is_constant(self):
        board = Board(100000)
        for index in range(3000):
            board.record("r-%d" % index, "p1", True, index)
        board.stats("p1", 2999)
        before = board.work_count()
        for _ in range(100):
            board.stats("p1", 2999)
        self.assertEqual(board.work_count() - before, 100)


if __name__ == "__main__":
    unittest.main()
