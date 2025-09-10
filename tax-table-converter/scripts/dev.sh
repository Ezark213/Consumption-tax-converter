#!/bin/bash

# 開発環境起動スクリプト

echo "税区分表変換ツール - 開発環境起動"
echo "=================================="

# 環境チェック
echo "環境チェック中..."

# Python環境チェック
if ! command -v python &> /dev/null; then
    echo "❌ Pythonが見つかりません"
    exit 1
fi
echo "✅ Python: $(python --version)"

# Node.js環境チェック
if ! command -v node &> /dev/null; then
    echo "❌ Node.jsが見つかりません"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

# npm環境チェック
if ! command -v npm &> /dev/null; then
    echo "❌ npmが見つかりません"
    exit 1
fi
echo "✅ npm: $(npm --version)"

# 依存関係のインストール
echo ""
echo "依存関係のインストール中..."

# Python依存関係
cd src/backend
if [ ! -d "venv" ]; then
    echo "Python仮想環境を作成中..."
    python -m venv venv
fi

source venv/bin/activate 2>/dev/null || source venv/Scripts/activate
pip install -r requirements.txt

cd ../..

# Node.js依存関係（ルート）
if [ ! -d "node_modules" ]; then
    echo "ルートディレクトリの依存関係をインストール中..."
    npm install
fi

# Node.js依存関係（フロントエンド）
cd src/frontend
if [ ! -d "node_modules" ]; then
    echo "フロントエンドの依存関係をインストール中..."
    npm install
fi

cd ../..

echo ""
echo "🚀 開発サーバーを起動しています..."
echo ""
echo "バックエンド: http://127.0.0.1:8000"
echo "フロントエンド: http://localhost:3000"
echo ""
echo "停止するには Ctrl+C を押してください"

# 開発サーバー起動
npm run dev