import streamlit as st

st.set_page_config(page_title="OpenAIサンプルアプリ", layout="wide")

# サイドバーにナビゲーションを追加
page = st.sidebar.radio("ページを選択", ["チャットアプリ", "MP3音声データ処理アプリ"])

# 選択されたページに基づいてスクリプトを実行
if page == "チャットアプリ":
    exec(open("chat.py", encoding='utf-8').read())
elif page == "MP3音声データ処理アプリ":
    exec(open("transcriber.py", encoding='utf-8').read())
