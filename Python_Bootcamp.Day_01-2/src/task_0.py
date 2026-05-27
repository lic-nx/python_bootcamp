# add_ingot(purse), get_ingot(purse), и empty(purse)
import unittest
from typing import Dict


def empty(purse: Dict[str, int]) -> Dict[str, int]:
    return {}


def get_ingot(purse: Dict[str, int]) -> Dict[str, int]:
    new_purse = purse.copy()
    if "gold_ingots" in new_purse:
        if new_purse["gold_ingots"] > 1:
            new_purse["gold_ingots"] -= 1
        else:
            del new_purse["gold_ingots"]
    return new_purse


def add_ingot(purse: Dict[str, int]) -> Dict[str, int]:
    new_purse = purse.copy()
    if "gold_ingots" in new_purse.keys():
        new_purse["gold_ingots"] += 1
    else:
        new_purse["gold_ingots"] = 1
    return new_purse


class TestAddIngot(unittest.TestCase):

    def test_add_to_empty_purse(self):
        self.assertEqual(add_ingot({}), {"gold_ingots": 1})

    def test_add_to_purse_with_ingot(self):
        self.assertEqual(add_ingot({"gold_ingots": 2}), {"gold_ingots": 3})

    def test_original_purse_unchanged(self):
        purse = {"gold_ingots": 1}
        new_purse = add_ingot(purse)
        self.assertEqual(purse, {"gold_ingots": 1})
        self.assertIsNot(purse, new_purse)
        self.assertEqual(new_purse, {"gold_ingots": 2})

    def test_other_keys_preserved(self):
        purse = {"silver_ingots": 5, "gold_ingots": 1}
        result = add_ingot(purse)
        self.assertEqual(result, {"silver_ingots": 5, "gold_ingots": 2})
        self.assertIn("silver_ingots", result)

    def test_no_gold_ingots_key_initially(self):
        purse = {"silver_ingots": 3}
        result = add_ingot(purse)
        self.assertEqual(result, {"silver_ingots": 3, "gold_ingots": 1})

    def test_empty_returns_empty_dict(self):
        self.assertEqual(empty({"gold_ingots": 5}), {})

    def test_empty_with_other_keys(self):
        self.assertEqual(empty({"silver_ingots": 3}), {})

    def test_empty_input(self):
        self.assertEqual(empty({}), {})

    def test_get_ingot_removes_when_one(self):
        self.assertEqual(get_ingot({"gold_ingots": 1}), {})

    def test_get_ingot_decreases_when_more_than_one(self):
        self.assertEqual(get_ingot({"gold_ingots": 5}), {"gold_ingots": 4})

    def test_get_ingot_key_not_present(self):
        self.assertEqual(get_ingot({"silver_ingots": 3}), {"silver_ingots": 3})

    def test_get_ingot_with_other_items(self):
        input_purse = {"gold_ingots": 3, "silver_ingots": 2}
        expected = {"gold_ingots": 2, "silver_ingots": 2}
        self.assertEqual(get_ingot(input_purse), expected)

    def test_original_purse_unchanged(self):
        purse = {"gold_ingots": 2}
        get_ingot(purse)
        self.assertEqual(purse, {"gold_ingots": 2})


if __name__ == "__main__":
    unittest.main()
