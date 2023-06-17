import unittest
from gpt_engineer.chat_to_files import parse_chat


class TestParseChat(unittest.TestCase):

    def test_parse_chat_with_valid_messages(self):
        chat = "```path1.py\nline1\nline2```" \
               "```path2.css\nline3\nline4```"
        expected_output = [('path1.py', 'line1\nline2'), ('path2.css', 'line3\nline4')]

        output = parse_chat(chat)

        self.assertEqual(expected_output, output)

    def test_parse_chat_with_no_messages(self):
        chat = "This is a test string without any valid messages."
        expected_output = []

        output = parse_chat(chat)

        self.assertEqual(output, expected_output)
