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
