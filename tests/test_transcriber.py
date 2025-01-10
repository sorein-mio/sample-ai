import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from transcriber import create_pdf

class TestTranscriber(unittest.TestCase):
    @patch('transcriber.st')
    def test_create_pdf(self, mock_st):
        # Streamlitのシークレットをモック
        mock_st.secrets = {'your_secret_key': 'test_value'}
        
        content = "これはテストです。\n新しい行です。"
        pdf_buffer = create_pdf(content)
        
        # PDFの内容を確認するために、バッファのサイズを確認
        self.assertGreater(len(pdf_buffer.getvalue()), 0, "PDFが生成されていません。")

if __name__ == '__main__':
    unittest.main()
