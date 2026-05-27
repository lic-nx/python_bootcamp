# add_ingot(purse), get_ingot(purse), и empty(purse)
import unittest
from unittest.mock import patch
from io import StringIO
from typing import Dict

def squeak_decorator(func):
    def wrapper(*args, **kwargs):
        print("SQUEAK")
        return func(*args, **kwargs)
    return wrapper

@squeak_decorator
def empty(purse: Dict[str, int]) -> Dict[str, int]:
    return {}

@squeak_decorator
def get_ingot(purse: Dict[str, int]) -> Dict[str, int]:
    new_purse = purse.copy()
    if "gold_ingots" in new_purse:
        if new_purse["gold_ingots"] > 1:
            new_purse["gold_ingots"] -= 1
        else:
            del new_purse["gold_ingots"]
    return new_purse

@squeak_decorator
def add_ingot(purse: Dict[str, int]) -> Dict[str, int]:
    new_purse = purse.copy()
    if "gold_ingots" in new_purse.keys():
        new_purse["gold_ingots"] += 1
    else:
        new_purse["gold_ingots"] = 1
    return new_purse


class TestPurseFunctions(unittest.TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    def test_empty_function_and_squeak(self, mock_stdout):
        result = empty({"gold_ingots": 5})
        self.assertEqual(result, {})
        self.assertEqual(mock_stdout.getvalue().strip(), "SQUEAK")

    @patch('sys.stdout', new_callable=StringIO)
    def test_get_ingot_remove_key(self, mock_stdout):
        result = get_ingot({"gold_ingots": 1})
        self.assertEqual(result, {})
        self.assertEqual(mock_stdout.getvalue().strip(), "SQUEAK")

    @patch('sys.stdout', new_callable=StringIO)
    def test_get_ingot_decrement(self, mock_stdout):
        result = get_ingot({"gold_ingots": 3})
        self.assertEqual(result, {"gold_ingots": 2})
        self.assertEqual(mock_stdout.getvalue().strip(), "SQUEAK")

    @patch('sys.stdout', new_callable=StringIO)
    def test_add_ingot_create_key(self, mock_stdout):
        result = add_ingot({})
        self.assertEqual(result, {"gold_ingots": 1})
        self.assertEqual(mock_stdout.getvalue().strip(), "SQUEAK")

    @patch('sys.stdout', new_callable=StringIO)
    def test_add_ingot_increment(self, mock_stdout):
        result = add_ingot({"gold_ingots": 2})
        self.assertEqual(result, {"gold_ingots": 3})
        self.assertEqual(mock_stdout.getvalue().strip(), "SQUEAK")

    @patch('sys.stdout', new_callable=StringIO)
    def test_all_functions_call_squeak(self, mock_stdout):
        empty({})
        get_ingot({"gold_ingots": 2})
        add_ingot({"gold_ingots": 1})

        output = mock_stdout.getvalue().strip().split('\n')
        self.assertEqual(output, ["SQUEAK", "SQUEAK", "SQUEAK"])


if __name__ == "__main__":
    unittest.main()