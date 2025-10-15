# 🤖 最新AIチャットアプリ

GPT-5とその派生モデルに対応した高機能なチャットアプリケーションです。

## ✨ 特徴

### 🏆 対応モデル
- **GPT-5 (最強・統合型)** - 2025年8月リリースの最強モデル
- **GPT-5 Standard (標準版)** - バランス型モデル
- **GPT-5 Mini (軽量版)** - 高速処理重視
- **GPT-5 Nano (超軽量版)** - リソース制限対応
- **GPT-5 Chat (対話特化)** - チャット最適化
- **GPT-4.1 (高性能)** - 2025年4月リリース
- **GPT-4o (マルチモーダル)** - マルチモーダル対応
- **GPT-4o-mini (高速・軽量)** - 軽量版
- **o1-preview (推論特化)** - 推論能力特化
- **o1-mini (推論軽量)** - 推論軽量版
- **o3-mini (次世代推論)** - 2025年1月リリース
- **GPT-3.5-turbo (従来型)** - 従来型モデル

### 🎯 機能
- 📁 カテゴリ別モデル選択
- 🔧 パラメータ調整（Temperature、最大トークン数）
- 💬 リアルタイムストリーミング
- 🗑️ チャット履歴管理
- 💾 履歴エクスポート機能
- ⚡ エラーハンドリング

## 🚀 デプロイ方法

### Streamlit Cloud
1. [Streamlit Cloud](https://share.streamlit.io/)にアクセス
2. GitHubリポジトリを選択
3. ブランチを`master`に設定
4. メインファイルを`main.py`に設定
5. デプロイ

### ローカル実行
```bash
# 依存関係のインストール
pip install -r requirements.txt

# アプリケーション起動
streamlit run main.py
```

## 🔑 環境変数設定

`.streamlit/secrets.toml`に以下を設定：

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

## 📱 使用方法

1. サイドバーでモデルを選択
2. 必要に応じてパラメータを調整
3. チャット入力欄にメッセージを入力
4. AIの応答を確認

## 🛠️ 技術スタック

- **Python 3.8+**
- **Streamlit** - Webアプリケーションフレームワーク
- **OpenAI Python Library** - AI API
- **GitHub** - バージョン管理
- **Streamlit Cloud** - デプロイメント

## 📄 ライセンス

MIT License
