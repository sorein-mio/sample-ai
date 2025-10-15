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
    "GPT-4o (マルチモーダル)": {
        "id": "gpt-4o",
        "description": "テキスト、画像、音声の統合処理が可能なマルチモーダルモデル",
        "category": "最新モデル"
    },
    "GPT-4o-mini (高速・軽量)": {
        "id": "gpt-4o-mini",
        "description": "GPT-4oの軽量版。高速レスポンスとコスト効率を重視",
        "category": "軽量モデル"
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
            st.markdown(message["content"])
            if message["role"] == "assistant":
                # モデル情報を表示
                model_info = message.get("model_info", "")
                if model_info:
                    st.caption(f"🤖 {model_info}")

    # ユーザー入力
    if prompt := st.chat_input("メッセージを入力してください..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
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
                    "stream": True,
                }
                
                # o1系はtemperatureとmax_tokensを設定しない
                if not selected_model["id"].startswith("o1"):
                    api_params["temperature"] = temperature
                    api_params["max_tokens"] = max_tokens
                
                # API呼び出し
                response_stream = client.chat.completions.create(**api_params)
                
                for response in response_stream:
                    if response.choices[0].delta.content:
                        full_response += response.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                # メッセージにモデル情報を追加
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response,
                    "model_info": selected_model_name
                })
                
            except Exception as e:
                error_msg = f"❌ エラーが発生しました: {str(e)}"
                message_placeholder.error(error_msg)
                
                # モデルが存在しない場合の特別な処理
                if "does not exist" in str(e) or "model_not_found" in str(e):
                    st.warning(f"⚠️ モデル '{selected_model['id']}' が見つかりません。別のモデルを選択してください。")
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg,
                    "model_info": selected_model_name
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
                # 履歴をテキスト形式でエクスポート
                export_text = ""
                for msg in st.session_state.messages:
                    role = "ユーザー" if msg["role"] == "user" else "アシスタント"
                    export_text += f"{role}: {msg['content']}\n\n"
                
                st.download_button(
                    label="📥 ダウンロード",
                    data=export_text,
                    file_name=f"chat_history_{int(time.time())}.txt",
                    mime="text/plain"
                )

# スクリプトが直接実行された場合にmainを呼び出す
if __name__ == "__main__":
    main()
