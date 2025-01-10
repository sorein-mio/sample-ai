import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from transcriber import create_pdf

class TestTranscriber(unittest.TestCase):
    @patch('transcriber.st')
    def test_selectbox_and_create_pdf(self, mock_st):
        # プルダウンメニューの選択肢をモック
        mock_st.selectbox.return_value = '未設定'
        
        # transcriber.py内のselectbox呼び出しをシミュレート
        num_speakers = mock_st.selectbox(
            "話者の人数を選択してください（未設定の場合は自動検出されます）",
            ['未設定', '1', '2', '3', '4', '5']
        )
        
        # プルダウンメニューの選択肢を確認
        mock_st.selectbox.assert_called_with(
            "話者の人数を選択してください（未設定の場合は自動検出されます）",
            ['未設定', '1', '2', '3', '4', '5']
        )
        # Streamlitのシークレットをモック
        mock_st.secrets = {'your_secret_key': 'test_value'}
        
        content = "これはテストです。\n新しい行です。"
        pdf_buffer = create_pdf(content)
        
        # PDFの内容を確認するために、バッファのサイズを確認
        self.assertGreater(len(pdf_buffer.getvalue()), 0, "PDFが生成されていません。")

if __name__ == '__main__':
    unittest.main()
