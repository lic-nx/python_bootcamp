from typing import Dict
from task_0 import empty, add_ingot
import unittest


def split_booty(purses: list[Dict[str, int]]) -> list[Dict[str, int]]:
    total_ingots = sum(purse.get("gold_ingots", 0) for purse in purses)
    purse1 = empty({})
    purse2 = empty({})
    purse3 = empty({})
    for _ in range(total_ingots):
        if purse1.get("gold_ingots", 0) <= purse2.get("gold_ingots", 0) and purse1.get(
            "gold_ingots", 0
        ) <= purse3.get("gold_ingots", 0):
            purse1 = add_ingot(purse1)
        elif purse2.get("gold_ingots", 0) <= purse1.get(
            "gold_ingots", 0
        ) and purse2.get("gold_ingots", 0) <= purse3.get("gold_ingots", 0):
            purse2 = add_ingot(purse2)
        else:
            purse3 = add_ingot(purse3)

    return [purse1, purse2, purse3]


class TestSplitBooty(unittest.TestCase):

    def test_no_ingots(self):
        result = split_booty([{}, {"gold_ingots": 0}, {}])
        self.assertEqual(result, [{}, {}, {}])

    def test_split_evenly(self):
        purses = [{"gold_ingots": 3}, {}, {}]
        result = split_booty(purses)
        expected = [{"gold_ingots": 1}, {"gold_ingots": 1}, {"gold_ingots": 1}]
        self.assertEqual(result, expected)

    def test_split_unevenly(self):
        purses = [{"gold_ingots": 4}, {"gold_ingots": 2}]
        result = split_booty(purses)
        expected = [{"gold_ingots": 2}, {"gold_ingots": 2}, {"gold_ingots": 2}]
        self.assertEqual(result, expected)

    def test_one_purse_has_all(self):
        purses = [{"gold_ingots": 7}]
        result = split_booty(purses)
        expected = [{"gold_ingots": 3}, {"gold_ingots": 2}, {"gold_ingots": 2}]
        self.assertEqual(result, expected)

    def test_multiple_purses_with_gold(self):
        purses = [{"gold_ingots": 2}, {"gold_ingots": 3}, {"gold_ingots": 1}]
        result = split_booty(purses)
        expected = [{"gold_ingots": 2}, {"gold_ingots": 2}, {"gold_ingots": 2}]
        self.assertEqual(result, expected)

    def test_original_purses_not_modified(self):
        purses = [{"gold_ingots": 3}]
        original = purses[0].copy()
        split_booty(purses)
        self.assertEqual(
            purses[0], original
        )

    def test_other_keys_ignored(self):
        purses = [{"gold_ingots": 4, "silver": 5}, {"copper": 10}]
        result = split_booty(purses)
        expected = [{"gold_ingots": 2}, {"gold_ingots": 1}, {"gold_ingots": 1}]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
