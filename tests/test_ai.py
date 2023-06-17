import unittest
from unittest.mock import patch, MagicMock
from gpt_engineer.ai import AI  # replace with the actual path to your AI class

class TestAI(unittest.TestCase):
    @patch('openai.Model.retrieve')
    @patch('openai.ChatCompletion.create')
    def test_start(self, mock_chat, mock_model):
        # Mock the response from the OpenAI API
        mock_model.side_effect = print("Model gpt-4 not available for provided api key reverting to gpt-3.5.turbo")
        mock_chat.return_value = iter([{'choices': [{'delta': {'content': 'Hello, how can I assist you today?'}}]}])

        # Initialize the AI class
        ai = AI()

        # Test the start method
        messages = ai.start("Welcome to the AI.", "Hello AI!")
        self.assertEqual(messages[-1]['content'], 'Hello, how can I assist you today?')

    @patch('openai.Model.retrieve')
    @patch('openai.ChatCompletion.create')
    def test_next(self, mock_chat, mock_model):
        # Mock the response from the OpenAI API
        mock_model.return_value = None
        mock_chat.return_value = iter([{'choices': [{'delta': {'content': 'Sure, I can do that.'}}]}])

        # Initialize the AI class
        ai = AI()

        # Test the next method
        messages = ai.next([ai.fsystem("Welcome to the AI."), ai.fuser("Can you help me with something?")])
        self.assertEqual(messages[-1]['content'], 'Sure, I can do that.')

if __name__ == '__main__':
    unittest.main()
