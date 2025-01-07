import streamlit as st
import os
import tempfile
from openai import OpenAI
from pyannote.audio import Pipeline

# PyAnnoteの設定
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
                                    use_auth_token=st.secrets["HUGGING_FACE_TOKEN"])


# ==========================
#  OpenAI APIキーの設定
# ==========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # ここにOpenAIのAPIキーを入力してください


# タイトル
st.title("MP3音声データ処理アプリ")

# 説明
st.markdown("""
このアプリケーションでは、MP3形式の音声ファイルをアップロードすると、以下の処理を行います：
- **文字起こし**
- **要約**
- **結果のテキストファイルとしてのダウンロード**
""")

# ファイルアップロード
uploaded_file = st.file_uploader("MP3ファイルをアップロードしてください", type=["mp3"])

select_model = st.selectbox(
    "要約に使用するモデルを選択してください",
    ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo']
)

if st.button('話者分離する'):
    if uploaded_file is not None:
        with st.spinner("音声ファイルを処理中..."):
            try:
                # 一時ファイルに保存
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_filename = tmp_file.name

                # ==========================
                #  話者分離 (PyAnnote)
                # ==========================
                st.subheader("話者分離結果")
                diarization = pipeline(tmp_filename)

                # 話者分離結果の表示
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    st.write(f"[{turn.start:.1f}s -> {turn.end:.1f}s] {speaker}")

                # ==========================
                #  文字起こし (Whisper API)
                # ==========================
                st.subheader("文字起こし結果")
                with open(tmp_filename, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="ja"
                    )

                transcript_text = transcription.text
                st.text_area("Transcription with Speaker Separation", transcript_text, height=300)

                # ==========================
                #  要約 (GPT API)
                # ==========================
                st.subheader("要約結果")
                try:
                    if not transcript_text.strip():
                        st.warning("文字起こし結果が空です。要約できる内容がありません。")
                        summary = "要約できる内容がありません。"
                    else:
                        prompt = f"以下のテキストを要約してください。\n\n{transcript_text}"
                        completion = client.chat.completions.create(
                            model=select_model,  # ご使用のモデル名に置き換えてください
                            messages=[
                                {"role": "system", "content": "重要なポイントがわかるように文構造を整えてください"},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        # 定義に応じて適切にメッセージコンテンツを取得
                        summary = completion.choices[0].message.content
                    st.text_area("Summary", summary, height=200)
                except Exception as e:
                    st.error(f"要約中にエラーが発生しました: {e}")

                # ==========================
                #  txtとして出力
                # ==========================
                output_text = f"=== 文字起こし ===\n{transcript_text}\n\n=== 要約 ===\n{summary}"
                st.download_button(
                    label="結果をTXTファイルとしてダウンロード",
                    data=output_text,
                    file_name="result.txt",
                    mime="text/plain",
                )
            except Exception as general_e:
                st.error(f"処理中にエラーが発生しました: {general_e}")
            finally:
                # クリーンアップのため一時ファイルを削除
                if os.path.exists(tmp_filename):
                    os.remove(tmp_filename)

if st.button('文字起こし・要約のみ行う'):
    if uploaded_file is not None:
        with st.spinner("音声ファイルを処理中..."):
            try:
                # 一時ファイルに保存
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_filename = tmp_file.name


                # ==========================
                #  文字起こし (Whisper API)
                # ==========================
                st.subheader("文字起こし結果")
                with open(tmp_filename, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="ja"
                    )

                transcript_text = transcription.text
                st.text_area("Transcription with Speaker Separation", transcript_text, height=300)

                # ==========================
                #  要約 (GPT API)
                # ==========================
                st.subheader("要約結果")
                try:
                    if not transcript_text.strip():
                        st.warning("文字起こし結果が空です。要約できる内容がありません。")
                        summary = "要約できる内容がありません。"
                    else:
                        prompt = f"以下のテキストを要約してください。\n\n{transcript_text}"
                        completion = client.chat.completions.create(
                            model=select_model,  # ご使用のモデル名に置き換えてください
                            messages=[
                                {"role": "system", "content": "重要なポイントがわかるように文構造を整えてください"},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        # 定義に応じて適切にメッセージコンテンツを取得
                        summary = completion.choices[0].message.content
                    st.text_area("Summary", summary, height=200)
                except Exception as e:
                    st.error(f"要約中にエラーが発生しました: {e}")

                # ==========================
                #  txtとして出力
                # ==========================
                output_text = f"=== 文字起こし ===\n{transcript_text}\n\n=== 要約 ===\n{summary}"
                st.download_button(
                    label="結果をTXTファイルとしてダウンロード",
                    data=output_text,
                    file_name="result.txt",
                    mime="text/plain",
                )
            except Exception as general_e:
                st.error(f"処理中にエラーが発生しました: {general_e}")
            finally:
                # クリーンアップのため一時ファイルを削除
                if os.path.exists(tmp_filename):
                    os.remove(tmp_filename)

