import unittest
from app import greet, farewell, shout


class TestApp(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet("DevOps"), "Hello, DevOps!")

    def test_farewell(self):
        self.assertEqual(farewell("DevOps"), "Goodbye, DevOps!")

    def test_shout(self):
        self.assertEqual(shout("DevOps automation"), "DEVOPS AUTOMATION")

    def test_empty_message(self):
        self.assertEqual(shout(""), "")


if __name__ == "__main__":
    unittest.main()
