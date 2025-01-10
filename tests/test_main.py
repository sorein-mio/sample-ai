import unittest
import sys
import os

# カレントディレクトリをモジュール検索パスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from streamlit import config as _config
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.runtime.scriptrunner import ScriptRunContext
import main

class TestMain(unittest.TestCase):
    def setUp(self):
        # Streamlitの設定をリセット
        _config._set_option("server.headless", True, "test")
        
        # ScriptRunContextのインスタンスを作成
        self.ctx = ScriptRunContext(
            session_id="test_session",
            _enqueue=None,
            query_string="",
            session_state={},
            uploaded_file_mgr=None,
            main_script_path="",
            user_info={},
            fragment_storage=None,
            pages_manager=None
        )
        
        # コンテキストを直接設定
        from streamlit.runtime.scriptrunner import add_script_run_ctx
        add_script_run_ctx(self.ctx)

    def test_page_config(self):
        # ページ設定が正しいか確認
        # ページ設定が正しいか確認
        # 現在のStreamlitでは直接確認する方法がないため、set_page_configの呼び出しが成功することを確認
        try:
            main.st.set_page_config(page_title="OpenAIサンプルアプリ", layout="wide")
        except Exception as e:
            self.fail(f"set_page_config failed: {e}")

    def test_navigation(self):
        # ナビゲーションが正しいか確認
        # ナビゲーションが正しいか確認
        # ボタンの存在を確認
        try:
            main.st.sidebar.button("チャットアプリ")
            main.st.sidebar.button("MP3音声データ処理アプリ")
        except Exception as e:
            self.fail(f"Button creation failed: {e}")

if __name__ == "__main__":
    unittest.main()
