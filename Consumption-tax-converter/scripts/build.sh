#!/bin/bash

# ビルドスクリプト

echo "税区分表変換ツール - ビルド"
echo "============================"

# クリーンアップ
echo "クリーンアップ中..."
npm run clean

# 環境チェック
echo "環境チェック中..."
if ! command -v python &> /dev/null; then
    echo "❌ Pythonが見つかりません"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.jsが見つかりません"
    exit 1
fi

# フロントエンドビルド
echo ""
echo "📦 フロントエンドをビルド中..."
cd src/frontend
npm run build
cd ../..

# バックエンドビルド
echo ""
echo "🐍 バックエンドをビルド中..."

# Pythonビルドスクリプトを実行
python scripts/build_backend.py

if [ $? -ne 0 ]; then
    echo "❌ バックエンドビルドに失敗しました"
    exit 1
fi

# Electronファイルをdistにコピー
echo ""
echo "⚡ Electronファイルをコピー中..."
mkdir -p dist/electron
cp -r src/electron/* dist/electron/

# フロントエンドビルドファイルをコピー
echo ""
echo "📋 フロントエンドビルドファイルをコピー中..."
mkdir -p dist/frontend
cp -r src/frontend/dist/* dist/frontend/

echo ""
echo "✅ ビルド完了!"
echo ""
echo "📁 出力ディレクトリ:"
echo "   - dist/frontend: フロントエンドファイル"
echo "   - dist/python: バックエンドファイル"
echo "   - dist/electron: Electronファイル"
echo ""
echo "🚀 実行可能ファイルを作成するには:"
echo "   npm run dist        # 全プラットフォーム"
echo "   npm run dist:win    # Windows"
echo "   npm run dist:mac    # macOS"
echo "   npm run dist:linux  # Linux"