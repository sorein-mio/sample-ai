import streamlit as st
import pandas as pd
import io
from openai import OpenAI
import time

# ==========================
#  OpenAI APIキーの設定
# ==========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

def load_csv(uploaded_file, encoding='utf-8', delimiter=',', nrows=None, use_chunks=False, chunk_size=10000):
    """CSVファイルを読み込む
    
    Args:
        uploaded_file: アップロードされたファイル
        encoding: エンコーディング
        delimiter: 区切り文字
        nrows: 読み込む行数（Noneの場合は全て）
        use_chunks: チャンク読み込みを使用するか
        chunk_size: チャンクサイズ
    """
    try:
        read_params = {
            'encoding': encoding,
            'sep': delimiter if delimiter != ',' else ','
        }
        
        # 行数制限がある場合
        if nrows is not None:
            read_params['nrows'] = nrows
        
        # チャンク読み込みの場合
        if use_chunks and nrows is None:
            chunks = []
            chunk_count = 0
            max_chunks = 100  # 最大100チャンク（メモリ保護）
            
            for chunk in pd.read_csv(uploaded_file, chunksize=chunk_size, **read_params):
                chunks.append(chunk)
                chunk_count += 1
                if chunk_count >= max_chunks:
                    st.warning(f"⚠️ ファイルが大きすぎるため、最初の{max_chunks * chunk_size:,}行のみ読み込みました。")
                    break
            
            if chunks:
                df = pd.concat(chunks, ignore_index=True)
            else:
                return None, "データが読み込めませんでした"
        else:
            # 通常の読み込み
            df = pd.read_csv(uploaded_file, **read_params)
        
        return df, None
    except UnicodeDecodeError:
        # UTF-8で失敗した場合、Shift-JISを試す
        try:
            uploaded_file.seek(0)  # ファイルポインタをリセット
            read_params['encoding'] = 'shift-jis'
            
            if use_chunks and nrows is None:
                chunks = []
                chunk_count = 0
                max_chunks = 100
                
                for chunk in pd.read_csv(uploaded_file, chunksize=chunk_size, **read_params):
                    chunks.append(chunk)
                    chunk_count += 1
                    if chunk_count >= max_chunks:
                        st.warning(f"⚠️ ファイルが大きすぎるため、最初の{max_chunks * chunk_size:,}行のみ読み込みました。")
                        break
                
                if chunks:
                    df = pd.concat(chunks, ignore_index=True)
                else:
                    return None, "データが読み込めませんでした"
            else:
                df = pd.read_csv(uploaded_file, **read_params)
            
            return df, None
        except Exception as e:
            return None, f"エンコーディングエラー: {str(e)}"
    except MemoryError:
        return None, "メモリ不足: ファイルが大きすぎます。サンプリング機能を使用してください。"
    except Exception as e:
        return None, f"CSV読み込みエラー: {str(e)}"

def display_statistics(df):
    """データフレームの統計情報を表示"""
    st.subheader("📊 統計情報")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("行数", len(df))
    with col2:
        st.metric("列数", len(df.columns))
    with col3:
        st.metric("欠損値", df.isnull().sum().sum())
    with col4:
        st.metric("重複行", df.duplicated().sum())
    
    # データ型情報
    st.markdown("### データ型情報")
    dtype_df = pd.DataFrame({
        '列名': df.columns,
        'データ型': df.dtypes.astype(str),
        '非欠損値数': df.count().values,
        '欠損値数': df.isnull().sum().values
    })
    st.dataframe(dtype_df, use_container_width=True)
    
    # 数値列の統計情報
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        st.markdown("### 数値列の統計情報")
        st.dataframe(df[numeric_cols].describe(), use_container_width=True)

def filter_dataframe(df):
    """データフレームのフィルタリング機能"""
    st.subheader("🔍 データフィルタリング")
    
    # 列選択によるフィルタリング
    filter_cols = st.multiselect("表示する列を選択", df.columns.tolist(), default=df.columns.tolist())
    
    if len(filter_cols) > 0:
        filtered_df = df[filter_cols]
        
        # 数値列の範囲フィルタリング
        numeric_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) > 0:
            st.markdown("#### 数値範囲フィルタ")
            for col in numeric_cols[:5]:  # 最大5列まで
                col_min, col_max = float(filtered_df[col].min()), float(filtered_df[col].max())
                if col_min != col_max:
                    range_values = st.slider(
                        f"{col} の範囲",
                        min_value=col_min,
                        max_value=col_max,
                        value=(col_min, col_max),
                        key=f"filter_{col}"
                    )
                    filtered_df = filtered_df[
                        (filtered_df[col] >= range_values[0]) & 
                        (filtered_df[col] <= range_values[1])
                    ]
        
        # テキスト検索
        text_cols = filtered_df.select_dtypes(include=['object']).columns.tolist()
        if len(text_cols) > 0:
            st.markdown("#### テキスト検索")
            search_col = st.selectbox("検索する列", text_cols, key="search_col")
            search_term = st.text_input("検索語", key="search_term")
            if search_term:
                filtered_df = filtered_df[
                    filtered_df[search_col].astype(str).str.contains(search_term, case=False, na=False)
                ]
        
        return filtered_df
    else:
        st.warning("少なくとも1つの列を選択してください")
        return df

def analyze_with_ai(df, model_id, user_query, temperature=0.7, max_tokens=2000):
    """AIを使用してCSVデータを分析"""
    try:
        # データフレームの基本情報を取得
        df_info = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "head": df.head(10).to_dict('records'),
            "describe": df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else None
        }
        
        # プロンプトを作成
        system_prompt = """あなたはデータ分析の専門家です。提供されたCSVデータの情報を基に、ユーザーの質問に対して詳細で実用的な回答を提供してください。"""
        
        user_prompt = f"""
以下のCSVデータの情報を分析してください：

データ概要:
- 行数: {df_info['shape'][0]}
- 列数: {df_info['shape'][1]}
- 列名: {', '.join(df_info['columns'])}

データ型:
{df_info['dtypes']}

最初の10行のデータ:
{df_info['head']}

統計情報:
{df_info['describe'] if df_info['describe'] else '数値列なし'}

ユーザーの質問: {user_query}

上記の情報を基に、データの特徴、傾向、洞察を提供してください。
"""
        
        # モデル固有のパラメータ設定
        api_params = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        }
        
        # モデル固有のパラメータ設定
        if model_id.startswith("o1"):
            # o1系はtemperatureとmax_tokensを設定しない
            pass
        elif model_id.startswith("gpt-5"):
            # GPT-5系はパラメータ制限あり
            api_params["temperature"] = 1.0
            api_params["max_completion_tokens"] = max_tokens
        else:
            # その他のモデルは従来通り
            api_params["temperature"] = temperature
            api_params["max_tokens"] = max_tokens
        
        # API呼び出し
        response = client.chat.completions.create(**api_params)
        
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

def main():
    # タイトル
    st.title("📊 CSV解析アプリ")
    st.markdown("---")
    
    # サイドバーでモデル選択
    with st.sidebar:
        st.header("⚙️ モデル設定")
        
        # シンプルなモデル選択
        model_options = list(MODELS.keys())
        selected_model_name = st.selectbox(
            "AI分析に使用するモデルを選択してください",
            model_options,
            index=0,
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
        
        max_tokens = st.slider("最大トークン数", 100, 4000, 2000, 100)
    
    # ファイルアップロード
    st.subheader("📁 CSVファイルのアップロード")
    uploaded_file = st.file_uploader(
        "CSVファイルをアップロードしてください",
        type=['csv'],
        help="UTF-8またはShift-JISエンコーディングのCSVファイルをサポートしています（最大1GB）"
    )
    
    # エンコーディングとデリミタの設定
    col1, col2 = st.columns(2)
    with col1:
        encoding = st.selectbox("エンコーディング", ["utf-8", "shift-jis"], index=0)
    with col2:
        delimiter = st.selectbox("区切り文字", [",", ";", "\t"], index=0)
    
    # セッション状態の初期化
    if "csv_data" not in st.session_state:
        st.session_state.csv_data = None
    if "csv_filename" not in st.session_state:
        st.session_state.csv_filename = None
    if "file_size_mb" not in st.session_state:
        st.session_state.file_size_mb = 0
    
    # CSVファイルの読み込み
    if uploaded_file is not None:
        # ファイルサイズを取得（MB単位）
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.session_state.file_size_mb = file_size_mb
        
        # ファイルサイズの表示
        if file_size_mb > 1:
            st.info(f"📦 ファイルサイズ: {file_size_mb:.2f} MB")
        
        # 大きいファイルの場合の警告とオプション
        use_sampling = False
        sample_rows = None
        use_chunks = False
        
        if file_size_mb > 100:
            st.error("⚠️ 非常に大きなファイル（100MB超）が検出されました。メモリ不足を防ぐため、サンプリング機能の使用を強く推奨します。")
            use_sampling = st.checkbox("📊 サンプリングを使用（最初のN行のみ読み込む）", value=True, key="use_sampling")
            if use_sampling:
                sample_rows = st.number_input(
                    "読み込む行数",
                    min_value=100,
                    max_value=1000000,
                    value=min(10000, int(500000 / max(file_size_mb, 1))),
                    step=1000,
                    help="大きいファイルの場合、最初のN行のみ読み込むことで処理を高速化できます"
                )
        elif file_size_mb > 10:
            st.warning("⚠️ 大きなファイルが検出されました。メモリ不足を防ぐため、サンプリング機能の使用を推奨します。")
            use_sampling = st.checkbox("📊 サンプリングを使用（最初のN行のみ読み込む）", value=True, key="use_sampling")
            if use_sampling:
                sample_rows = st.number_input(
                    "読み込む行数",
                    min_value=100,
                    max_value=1000000,
                    value=min(10000, int(1000000 / max(file_size_mb, 1))),
                    step=1000,
                    help="大きいファイルの場合、最初のN行のみ読み込むことで処理を高速化できます"
                )
        elif file_size_mb > 5:
            st.info("💡 ファイルがやや大きいため、必要に応じてサンプリング機能を使用できます。")
            use_sampling = st.checkbox("📊 サンプリングを使用（最初のN行のみ読み込む）", value=False, key="use_sampling")
            if use_sampling:
                sample_rows = st.number_input(
                    "読み込む行数",
                    min_value=100,
                    max_value=100000,
                    value=10000,
                    step=1000,
                    help="最初のN行のみ読み込むことで処理を高速化できます"
                )
        
        if st.session_state.csv_filename != uploaded_file.name or (
            st.session_state.csv_filename == uploaded_file.name and 
            st.session_state.get("load_params") != (encoding, delimiter, sample_rows, use_chunks)
        ):
            with st.spinner("CSVファイルを読み込み中..."):
                df, error = load_csv(
                    uploaded_file, 
                    encoding=encoding, 
                    delimiter=delimiter,
                    nrows=sample_rows if use_sampling else None,
                    use_chunks=use_chunks,
                    chunk_size=10000
                )
                if error:
                    st.error(error)
                    st.session_state.csv_data = None
                else:
                    st.session_state.csv_data = df
                    st.session_state.csv_filename = uploaded_file.name
                    st.session_state.load_params = (encoding, delimiter, sample_rows, use_chunks)
                    if use_sampling and sample_rows:
                        st.success(f"✅ {uploaded_file.name} の最初 {sample_rows:,} 行を読み込みました！")
                    else:
                        st.success(f"✅ {uploaded_file.name} を読み込みました！")
        
        df = st.session_state.csv_data
        
        if df is not None:
            # サンプリングが使用されている場合の警告
            if st.session_state.get("load_params") and st.session_state.load_params[2] is not None:
                st.info(f"ℹ️ 現在、データの最初 {len(df):,} 行のみが読み込まれています。全データを読み込むには、サンプリングを無効にしてください。")
            
            # タブで機能を分ける
            tab1, tab2, tab3, tab4 = st.tabs(["📋 データ表示", "📊 統計情報", "🔍 フィルタリング", "🤖 AI分析"])
            
            with tab1:
                st.subheader("📋 データ表示")
                st.dataframe(df, use_container_width=True, height=400)
                
                # ダウンロードボタン
                csv_string = df.to_csv(index=False)
                st.download_button(
                    label="📥 フィルタ済みデータをダウンロード",
                    data=csv_string,
                    file_name=f"filtered_{st.session_state.csv_filename}",
                    mime="text/csv"
                )
            
            with tab2:
                display_statistics(df)
            
            with tab3:
                filtered_df = filter_dataframe(df)
                st.markdown("### フィルタリング結果")
                st.dataframe(filtered_df, use_container_width=True, height=400)
                
                # フィルタ済みデータのダウンロード
                if len(filtered_df) < len(df):
                    csv_string = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📥 フィルタ済みデータをダウンロード",
                        data=csv_string,
                        file_name=f"filtered_{st.session_state.csv_filename}",
                        mime="text/csv",
                        key="download_filtered"
                    )
            
            with tab4:
                st.subheader("🤖 AIによるデータ分析")
                st.markdown("CSVデータについて質問してください。AIがデータを分析して回答します。")
                
                # よくある質問の例
                st.markdown("### 💡 よくある質問の例")
                example_queries = [
                    "このデータの基本的な特徴を教えてください",
                    "数値列の相関関係を分析してください",
                    "データに欠損値や異常値はありますか？",
                    "データの傾向やパターンを説明してください",
                    "このデータから分かる洞察を教えてください"
                ]
                
                # セッション状態で選択されたクエリを管理
                if "selected_query" not in st.session_state:
                    st.session_state.selected_query = ""
                
                for i, query in enumerate(example_queries):
                    if st.button(f"📌 {query}", key=f"example_{i}"):
                        st.session_state.selected_query = query
                        st.rerun()
                
                st.markdown("---")
                
                # 選択されたクエリをテキストエリアに反映
                if st.session_state.selected_query:
                    analysis_query = st.text_area(
                        "分析したい内容を入力してください",
                        value=st.session_state.selected_query,
                        height=100,
                        key="analysis_query_input"
                    )
                    st.session_state.selected_query = ""  # 使用後はクリア
                else:
                    analysis_query = st.text_area(
                        "分析したい内容を入力してください",
                        placeholder="例: このデータの特徴を教えてください / 売上と利益の関係を分析してください / 異常値はありますか？",
                        height=100,
                        key="analysis_query_input"
                    )
                
                if st.button("🔍 分析を実行", type="primary"):
                    if analysis_query:
                        with st.spinner("AIがデータを分析中..."):
                            result, error = analyze_with_ai(
                                df, 
                                selected_model["id"], 
                                analysis_query,
                                temperature=temperature,
                                max_tokens=max_tokens
                            )
                            if error:
                                st.error(f"❌ エラーが発生しました: {error}")
                                # モデルが存在しない場合の特別な処理
                                if "does not exist" in error or "model_not_found" in error:
                                    st.warning(f"⚠️ モデル '{selected_model['id']}' が見つかりません。別のモデルを選択してください。")
                                    st.info("💡 推奨モデル: GPT-4o, GPT-4o-mini, o1-mini, GPT-4-turbo, GPT-3.5-turbo")
                                elif "rate_limit" in error.lower():
                                    st.warning("⚠️ レート制限に達しました。しばらく待ってから再試行してください。")
                                elif "insufficient_quota" in error.lower():
                                    st.warning("⚠️ APIクォータが不足しています。アカウント設定を確認してください。")
                            else:
                                st.markdown("### 分析結果")
                                st.markdown(result)
                    else:
                        st.warning("分析したい内容を入力してください")
    else:
        st.info("👆 CSVファイルをアップロードしてください")
        st.markdown("""
        ### 📝 使い方
        1. サイドバーでAI分析に使用するモデルを選択
        2. CSVファイルをアップロード
        3. 以下の機能を使用できます：
           - **データ表示**: アップロードしたCSVデータをテーブル形式で表示
           - **統計情報**: データの基本統計情報を表示
           - **フィルタリング**: 列の選択、数値範囲、テキスト検索によるフィルタリング
           - **AI分析**: AIを使用してデータを分析し、質問に回答
        """)

if __name__ == "__main__":
    main()

