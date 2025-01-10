import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from chat import main as chat_main

class TestChat(unittest.TestCase):
    @patch('chat.st')
    @patch('chat.OpenAI')
    def test_chat_functionality(self, mock_openai, mock_st):
        # Streamlitのセッション状態をモック
        mock_st.session_state = MagicMock()
        mock_st.session_state.messages = []
        mock_st.secrets = {'OPENAI_API_KEY': 'test_key'}
        
        # OpenAIのクライアントをモック
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="こんにちは！何かお手伝いできることがあれば教えてください。"))]
        )
        
        # ユーザーの入力をシミュレート
        mock_st.chat_input.return_value = "こんにちは"
        
        # Streamlitのselectboxの戻り値を設定
        mock_st.selectbox.return_value = "gpt-4o"

        chat_main()
        
        # メッセージが正しく追加されたか確認
        self.assertEqual(len(mock_st.session_state.messages), 2)
        self.assertEqual(mock_st.session_state.messages[0]['content'], "こんにちは")
        self.assertTrue(len(mock_st.session_state.messages[1]['content']) > 0)

if __name__ == '__main__':
    unittest.main()
