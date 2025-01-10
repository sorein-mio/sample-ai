import streamlit as st
import os
import tempfile
from openai import OpenAI
from pyannote.audio import Pipeline
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import fonts

# PyAnnoteの設定
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",
                                    use_auth_token=st.secrets["HUGGING_FACE_TOKEN"])

# フォントの登録
pdfmetrics.registerFont(TTFont('NotoSansJP', 'NotoSansJP-Regular.ttf'))

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
import re

import markdown
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Paragraph, Spacer, ListFlowable, ListItem
from xml.etree import ElementTree as ET
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

def create_pdf(content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # 日本語フォントの登録
    pdfmetrics.registerFont(TTFont('NotoSansJP', 'NotoSansJP-Regular.ttf'))
    
    # カスタムスタイルの定義
    styles.add(ParagraphStyle(name='Japanese', 
                              fontName='NotoSansJP', 
                              fontSize=10, 
                              leading=14))

    # コンテンツを段落に分割
    paragraphs = []
    for line in content.split('\n'):
        if line.strip():
            p = Paragraph(line, styles['Japanese'])
            paragraphs.append(p)
            paragraphs.append(Spacer(1, 6))  # 段落間のスペース

    # PDFの生成
    doc.build(paragraphs)
    buffer.seek(0)
    return buffer

# ==========================
#  OpenAI APIキーの設定
# ==========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

# ファイル形式の選択オプションを追加
output_format = st.selectbox(
    "出力ファイル形式を選択してください",
    ['TXT', 'PDF']
)

# 話者人数の選択
num_speakers = st.selectbox(
    "話者の人数を選択してください（未設定の場合は自動検出されます）",
    ['未設定', '1', '2', '3', '4', '5']
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
                # 話者の人数を指定して話者分離を実行
                if num_speakers != '未設定':
                    diarization = pipeline(tmp_filename, num_speakers=int(num_speakers))
                else:
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
                #  話者分離と文字起こしの結合
                # ==========================

                st.subheader("話者分離と文字起こしの結合結果")

                # 話者の発言を時間順にソート
                sorted_turns = sorted(diarization.itertracks(yield_label=True), key=lambda x: x[0].start)

                # 文字起こしテキストを単語に分割
                words = transcript_text.split()
                word_count = len(words)

                combined_text = ""
                current_word = 0

                # 全体の長さを計算（最後のセグメントの終了時間）
                total_duration = max(turn.end for turn, _, _ in sorted_turns)

                for turn, _, speaker in sorted_turns:
                    # この発言の単語数を推定（全体の長さに対する比率で）
                    turn_duration = turn.end - turn.start
                    estimated_words = int((turn_duration / total_duration) * word_count)

                    # 発言テキストを取得
                    turn_text = " ".join(words[current_word:current_word + estimated_words])
                    current_word += estimated_words

                    # 結合テキストに追加
                    combined_text += f"{speaker}: {turn_text}\n\n"

                try:
                    st.text_area("話者分離と文字起こしの結合結果", combined_text, height=300)
                except Exception as e:
                    st.error(f"話者分離と文字起こしの結合中にエラーが発生しました: {e}")
                    combined_text = "エラーにより結合結果を生成できませんでした。"



                # ==========================
                #  要約 (GPT API)
                # ==========================
                st.subheader("要約結果")
                try:
                    if not transcript_text.strip():
                        st.warning("文字起こし結果が空です。要約できる内容がありません。")
                        summary = "要約できる内容がありません。"
                    else:
                        # 議事録の形式で要約を要求する日本語のプロンプトに変更
                        prompt = f"以下のテキストを議事録の形式で要約してください。\n\n{transcript_text}"
                        completion = client.chat.completions.create(
                            model=select_model,  # ご使用のモデル名に置き換えてください
                            messages=[
                                {"role": "system", "content": "議事録の形式で要約してください。"},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        # 定義に応じて適切にメッセージコンテンツを取得
                        summary = completion.choices[0].message.content
                    st.markdown("### 議事録形式の要約\n" + summary)
                except Exception as e:
                    st.error(f"要約中にエラーが発生しました: {e}")

                # ==========================
                #  結果の出力
                # ==========================
                output_text = f"=== 話者分離と文字起こしの結合結果 ===\n{combined_text}\n\n=== 要約 ===\n{summary}"

                # 出力ボタンの作成
                if output_format == 'TXT':
                    st.download_button(
                        label="結果をTXTファイルとしてダウンロード",
                        data=output_text,
                        file_name="result.txt",
                        mime="text/plain",
                    )
                elif output_format == 'PDF':
                    pdf_buffer = create_pdf(output_text)
                    st.download_button(
                        label="結果をPDFファイルとしてダウンロード",
                        data=pdf_buffer,
                        file_name="result.pdf",
                        mime="application/pdf",
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
                        # 議事録の形式で要約を要求する日本語のプロンプトに変更
                        prompt = f"以下のテキストをマークダウン記法を用いて、議事録の形式で要約してください。\n\n{transcript_text}"
                        completion = client.chat.completions.create(
                            model=select_model,  # ご使用のモデル名に置き換えてください
                            messages=[
                                {"role": "system", "content": "マークダウン記法を用いて議事録の形式で要約してください。"},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        # 定義に応じて適切にメッセージコンテンツを取得
                        summary = completion.choices[0].message.content
                    st.markdown("### 議事録\n" + summary)
                except Exception as e:
                    st.error(f"要約中にエラーが発生しました: {e}")

                # ==========================
                #  結果の出力
                # ==========================
                output_text = f"### === 文字起こし ===\n{transcript_text}\n\n ### === 要約 ===\n{summary}"

                # 出力ボタンの作成
                if output_format == 'TXT':
                    st.download_button(
                        label="結果をTXTファイルとしてダウンロード",
                        data=output_text,
                        file_name="result.txt",
                        mime="text/plain",
                    )
                elif output_format == 'PDF':
                    pdf_buffer = create_pdf(output_text)
                    st.download_button(
                        label="結果をPDFファイルとしてダウンロード",
                        data=pdf_buffer,
                        file_name="result.pdf",
                        mime="application/pdf",
                    )
            except Exception as general_e:
                st.error(f"処理中にエラーが発生しました: {general_e}")
            finally:
                # クリーンアップのため一時ファイルを削除
                if os.path.exists(tmp_filename):
                    os.remove(tmp_filename)
