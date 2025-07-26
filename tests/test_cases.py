import unittest
import student_script

class TestStudentFunctions(unittest.TestCase):

    def test_add_two(self):
        try:
            result = student_script.add_two(1, 1)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail("Function add_two crashed: " + str(e))
