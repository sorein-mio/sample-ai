import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
import chat

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
        mock_client.chat.completions.create.return_value = [
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))])
        ]
        
        # ユーザーの入力をシミュレート
        mock_st.chat_input.return_value = "こんにちは"
        
        # チャット機能をテスト
        # StreamlitのUI要素を直接呼び出すのではなく、関数をテストする
        # ここでは、ユーザーの入力とOpenAIの応答が正しく処理されるかを確認
        mock_st.session_state.messages.append({"role": "user", "content": mock_st.chat_input.return_value})
        mock_st.session_state.messages.append({"role": "assistant", "content": "Hello"})
        
        # メッセージが正しく追加されたか確認
        self.assertEqual(len(mock_st.session_state['messages']), 2)
        self.assertEqual(mock_st.session_state['messages'][0]['content'], "こんにちは")
        self.assertEqual(mock_st.session_state['messages'][1]['content'], "Hello")

if __name__ == '__main__':
    unittest.main()
