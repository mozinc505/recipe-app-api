"""
Sample tests
"""

from django.test import SimpleTestCase

from app import calc

class CalcTests(SimpleTestCase):
    """Test the calc module."""

    """Test metoda se mora začeti z besedico test_"""
    def test_add_number(self):
        """Test adding numbers together."""
        res = calc.add(5, 6)

        self.assertEqual(res, 11)
        
    def test_subtract_numbers(self):
        """Test substracting numbers."""
        res = calc.subtract(10, 15)

        self.assertEqual(res, 5)
