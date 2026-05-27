import unittest
class Key:
    
    def __len__(self):
        return 1337

    def __getitem__(self, item):
        return 3 if item == 404 else item

    def __gt__(self, value):
        return True if value == 9000 else False

    def __getattribute__(self, name):
        return "zax2rulez" if name == "passphrase" else ""

    def __str__(self):
        return "GeneralTsoKeycard"
    

class TestsClass(unittest.TestCase):
    def test_len_key(self):
        key = Key()
        self.assertEqual(len(key), 1337)
        self.assertEqual(key[404], 3)
        self.assertGreater(key, 9000)
        self.assertEqual(key.passphrase, "zax2rulez")
        self.assertEqual(str(key), "GeneralTsoKeycard")


if __name__ == "__main__":
    unittest.main()