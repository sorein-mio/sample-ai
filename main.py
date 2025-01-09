import streamlit as st

st.set_page_config(page_title="OpenAIサンプルアプリ", layout="wide")

pg = st.navigation([st.Page("chat.py", title="チャットアプリ"),
                    st.Page("transcriber.py", title="MP3音声データ処理アプリ")])
pg.run()
