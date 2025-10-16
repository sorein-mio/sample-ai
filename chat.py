import streamlit as st
from openai import OpenAI
import time

# ==========================
#  OpenAI APIキーの設定
# ==========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # ここにOpenAIのAPIキーを入力してください

# ==========================
#  モデル設定
# ==========================
MODELS = {
    "GPT-5 (最強・統合型)": {
        "id": "gpt-5",
        "description": "2025年8月リリースの最強モデル。GPTシリーズとoシリーズを統合",
        "category": "最強モデル"
    },
    "GPT-5 Mini (軽量版)": {
        "id": "gpt-5-mini",
        "description": "GPT-5の軽量版。高速処理とコスト効率を重視したモデル",
        "category": "最強モデル"
    },
    "GPT-5 Chat (対話特化)": {
        "id": "gpt-5-chat",
        "description": "対話型アプリケーション向けに最適化されたGPT-5モデル",
        "category": "最強モデル"
    },
    "GPT-4o (マルチモーダル)": {
        "id": "gpt-4o",
        "description": "テキスト、画像、音声の統合処理が可能なマルチモーダルモデル",
        "category": "最新モデル"
    },
    "o1-mini (推論特化)": {
        "id": "o1-mini",
        "description": "推論能力に特化したモデル。数学や科学の問題解決に優れる",
        "category": "推論特化"
    },
    "GPT-4-turbo (高性能)": {
        "id": "gpt-4-turbo",
        "description": "GPT-4の高性能版。複雑なタスクに優れた性能を発揮",
        "category": "高性能"
    },
    "GPT-3.5-turbo (従来型)": {
        "id": "gpt-3.5-turbo",
        "description": "安定した性能とコスト効率を提供する従来型モデル",
        "category": "従来型"
    }
}

def main():
    # タイトル
    st.title("🤖 最新AIチャットアプリ")
    st.markdown("---")
    
    # チャットメッセージの表示を改善するCSS
    st.markdown("""
    <style>
    /* 全体のコンテナ設定 */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
        margin: 0 !important;
    }
    
    /* チャットメッセージ全体の設定 */
    .stChatMessage {
        word-wrap: break-word !important;
        white-space: pre-wrap !important;
        overflow-wrap: break-word !important;
        max-width: 100% !important;
        overflow: visible !important;
        word-break: break-word !important;
        width: 100% !important;
        box-sizing: border-box !important;
        margin: 0 !important;
        padding: 0.5rem !important;
    }
    
    /* メッセージコンテナの設定 */
    .stChatMessage .stMarkdown {
        word-wrap: break-word !important;
        white-space: pre-wrap !important;
        overflow-wrap: break-word !important;
        max-width: 100% !important;
        overflow: visible !important;
        word-break: break-word !important;
        width: 100% !important;
        box-sizing: border-box !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* 段落の設定 */
    .stChatMessage .stMarkdown p {
        word-wrap: break-word !important;
        white-space: pre-wrap !important;
        overflow-wrap: break-word !important;
        max-width: 100% !important;
        overflow: visible !important;
        word-break: break-word !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    
    /* チャットコンテナの設定 */
    .stChatMessageContainer {
        max-width: 100% !important;
        overflow: visible !important;
        width: 100% !important;
        box-sizing: border-box !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* チャット入力エリアの設定 */
    .stChatInput {
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* サイドバーの設定 */
    .stSidebar {
        max-width: 20% !important;
    }
    
    /* メインエリアの設定 */
    .main .block-container > div {
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* コードブロックの設定 */
    .stChatMessage pre {
        word-wrap: break-word !important;
        white-space: pre-wrap !important;
        overflow-wrap: break-word !important;
        max-width: 100% !important;
        overflow: visible !important;
        word-break: break-word !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    
    /* すべてのテキスト要素 */
    .stChatMessage * {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
        max-width: 100% !important;
        overflow: visible !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # サイドバーでモデル選択
    with st.sidebar:
        st.header("⚙️ モデル設定")
        
        # シンプルなモデル選択
        model_options = list(MODELS.keys())
        selected_model_name = st.selectbox(
        "会話に使用するモデルを選択してください",
            model_options,
            index=0,  # デフォルトでGPT-5を選択
            help="各モデルの特徴を確認してから選択してください"
        )
        
        selected_model = MODELS[selected_model_name]
        
        # モデル情報表示
        st.markdown("---")
        st.subheader("📋 選択中のモデル")
        st.info(f"**{selected_model_name}**\n\n{selected_model['description']}")
        
        # 追加設定
        st.markdown("---")
        st.subheader("🔧 追加設定")
        
        # GPT-5系ではtemperatureを固定値に
        if selected_model["id"].startswith("gpt-5"):
            st.info("🤖 GPT-5系では創造性は固定値(1.0)です")
            temperature = 1.0
        else:
            temperature = st.slider("創造性 (Temperature)", 0.0, 2.0, 0.7, 0.1)
        
        max_tokens = st.slider("最大トークン数", 100, 4000, 1000, 100)

    # メインエリア
    st.subheader("💬 チャット")

    # セッション状態の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # チャット履歴の表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # メッセージを完全に表示
            content = message["content"]
            
            # メッセージを複数の方法で表示（確実に完全表示）
            st.markdown(content)
            
            # すべてのメッセージにプレーンテキスト表示を追加（確実に完全表示）
            with st.expander("📄 完全なテキストを表示", expanded=False):
                st.text(content)
                # さらに確実にするため、生のテキストも表示
                st.code(content, language=None)
            
            if message["role"] == "assistant":
                # モデル情報を表示
                model_info = message.get("model_info", "")
                if model_info:
                    st.caption(f"🤖 {model_info}")

    # ユーザー入力
    if prompt := st.chat_input("メッセージを入力してください..."):
        # 入力メッセージにタイムスタンプを付与
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "ts": int(time.time())
        })
        with st.chat_message("user"):
            st.markdown(prompt)

        # OpenAI APIを使用して応答を生成
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # モデル固有のパラメータ設定
                api_params = {
                    "model": selected_model["id"],
                    "messages": [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                }
                
                # ストリーミング設定
                api_params["stream"] = True
                
                # モデル固有のパラメータ設定
                if selected_model["id"].startswith("o1"):
                    # o1系はtemperatureとmax_tokensを設定しない
                    pass
                elif selected_model["id"].startswith("gpt-5"):
                    # GPT-5系はパラメータ制限あり
                    api_params["temperature"] = 1.0
                    api_params["max_completion_tokens"] = max_tokens
                else:
                    # その他のモデルは従来通り
                    api_params["temperature"] = temperature
                    api_params["max_tokens"] = max_tokens
                
                # API呼び出し
                response_stream = client.chat.completions.create(**api_params)
                
                for response in response_stream:
                    if response.choices[0].delta.content:
                        full_response += response.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                # メッセージにモデル情報・利用パラメータ・タイムスタンプを追加
                used_params = {
                    "model": selected_model["id"],
                    # GPT-5系はmax_completion_tokens、それ以外はmax_tokensを採用
                    "temperature": 1.0 if selected_model["id"].startswith("gpt-5") else (
                        None if selected_model["id"].startswith("o1") else temperature
                    ),
                    "max_tokens": None if selected_model["id"].startswith("gpt-5") else (
                        None if selected_model["id"].startswith("o1") else max_tokens
                    ),
                    "max_completion_tokens": max_tokens if selected_model["id"].startswith("gpt-5") else None,
                }

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "model_info": selected_model_name,
                    "params": used_params,
                    "ts": int(time.time())
                })
                
            except Exception as e:
                error_msg = f"❌ エラーが発生しました: {str(e)}"
                message_placeholder.error(error_msg)
                
                # モデルが存在しない場合の特別な処理
                if "does not exist" in str(e) or "model_not_found" in str(e):
                    st.warning(f"⚠️ モデル '{selected_model['id']}' が見つかりません。別のモデルを選択してください。")
                    st.info("💡 推奨モデル: GPT-4o, GPT-4o-mini, o1-mini, GPT-4-turbo, GPT-3.5-turbo")
                elif "rate_limit" in str(e).lower():
                    st.warning("⚠️ レート制限に達しました。しばらく待ってから再試行してください。")
                elif "insufficient_quota" in str(e).lower():
                    st.warning("⚠️ APIクォータが不足しています。アカウント設定を確認してください。")
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg,
                    "model_info": selected_model_name,
                    "params": {"model": selected_model["id"]},
                    "ts": int(time.time())
                })

    # チャット履歴管理
    if st.session_state.messages:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🗑️ 履歴をクリア"):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("💾 履歴をエクスポート"):
                # エクスポート形式選択を表示
                export_format = st.selectbox("エクスポート形式", ["CSV", "JSONL"], index=0, key="export_format")
                
                if export_format == "CSV":
                    # 比較しやすい縦持ちCSV: index,ts,role,model,temperature,max_tokens,max_completion_tokens,content
                    import csv
                    from io import StringIO
                    buffer = StringIO()
                    writer = csv.writer(buffer)
                    writer.writerow(["index", "ts", "role", "model", "temperature", "max_tokens", "max_completion_tokens", "content"])
                    for i, msg in enumerate(st.session_state.messages):
                        params = msg.get("params", {})
                        model = params.get("model", msg.get("model_info", ""))
                        writer.writerow([
                            i,
                            msg.get("ts", ""),
                            msg.get("role", ""),
                            model,
                            params.get("temperature", ""),
                            params.get("max_tokens", ""),
                            params.get("max_completion_tokens", ""),
                            msg.get("content", "").replace("\n", " ")
                        ])
                    data = buffer.getvalue()
                    st.download_button(
                        label="📥 CSVダウンロード",
                        data=data,
                        file_name=f"chat_history_{int(time.time())}.csv",
                        mime="text/csv"
                    )
                else:
                    # JSONL: 1行1メッセージ（比較のための完全情報）
                    import json
                    lines = []
                    for i, msg in enumerate(st.session_state.messages):
                        record = {
                            "index": i,
                            "ts": msg.get("ts"),
                            "role": msg.get("role"),
                            "model_info": msg.get("model_info"),
                            "params": msg.get("params"),
                            "content": msg.get("content"),
                        }
                        lines.append(json.dumps(record, ensure_ascii=False))
                    data = "\n".join(lines)
                    st.download_button(
                        label="📥 JSONLダウンロード",
                        data=data,
                        file_name=f"chat_history_{int(time.time())}.jsonl",
                        mime="application/jsonl"
                    )

# スクリプトが直接実行された場合にmainを呼び出す
if __name__ == "__main__":
    main()
