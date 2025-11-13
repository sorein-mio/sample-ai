import streamlit as st

st.set_page_config(
    page_title="最新AIチャットアプリ",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# サイドバーにナビゲーションを追加
page = st.sidebar.radio("ページを選択", ["チャットアプリ", "MP3音声データ処理アプリ", "CSV解析アプリ"])

# 選択されたページに基づいてスクリプトを実行
if page == "チャットアプリ":
    from chat import main as chat_main
    chat_main()
elif page == "MP3音声データ処理アプリ":
    exec(open("transcriber.py", encoding='utf-8').read())
elif page == "CSV解析アプリ":
    from csv_analyzer import main as csv_main
    csv_main()
