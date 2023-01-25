"""
Test custom Django management commands.
"""
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2OpError

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    # POZOR: Vrstni red parametrov je pomemben. Najprej "notranje"
    #    (direktno na metodi), nato zunanje (od class-a)
    #    Inside-out sistem.
    #    PRIMER:

    #    @patch('time.sleep') ... ta je 2-jka
    #    @patch('time.sleep')
    #    def test_wait_for_db_delay(self, patched_sleep,
    #       patched_sleep2, patched_check):

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""

        """Razlaga:
            * 2 --> pomeni: first two times when this
                    happens raise Psycopg2Error
            * 3 --> pomeni: next three times when this happens
                     raise OperationalError
            [True] --> pomeni: šestič vrnemo TRUE (kot, da je vse okej)
            S tem simuliramo (mock) kako dejansko vrne baza napako,
                    ko se postavlja in še ni pripravljena za povezavo.
        """
        patched_check.side_effect = [Psycopg2OpError] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
