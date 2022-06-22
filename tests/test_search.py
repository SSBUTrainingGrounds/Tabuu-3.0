import unittest

from discord.app_commands import Choice

from utils.search import autocomplete_choices


class TestSearch(unittest.TestCase):
    def test_autocomplete_choices(self):
        query = "test"

        available_choices = [
            # Some normal choices
            "test",
            "test2",
            "tabuu 3.0",
            "whatever",
            "some strings",
            "!!!!",
            "not sure",
            "some more strings",
            "test - a long string with the word test in it",
            "a long string without the word in it",
            "eh",
            "the test",
            # Similar words to "test" in different alpabets.
            "テスト",
            "τεστ?",
            "юст тестинг",
        ]

        results = [
            Choice(name="test", value="test"),
            Choice(name="test2", value="test2"),
            Choice(name="τεστ?", value="τεστ?"),
            Choice(name="the test", value="the test"),
            Choice(name="юст тестинг", value="юст тестинг"),
            Choice(name="テスト", value="テスト"),
            Choice(
                name="test - a long string with the word test in it",
                value="test - a long string with the word test in it",
            ),
            Choice(name="some strings", value="some strings"),
            Choice(name="some more strings", value="some more strings"),
            Choice(name="whatever", value="whatever"),
        ]

        autocomplete_choices(query, available_choices)

        self.assertEqual(autocomplete_choices(query, available_choices), results)
