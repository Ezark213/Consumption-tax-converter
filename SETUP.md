# セットアップガイド

## 前提条件

- **Python 3.11+** がインストールされていること
- **Node.js 18+** がインストールされていること
- **pip** が利用可能であること
- **npm** が利用可能であること

## クイックスタート

### 1. 依存関係のインストール

```bash
# プロジェクトディレクトリに移動
cd tax-table-converter

# Node.js依存関係をインストール
npm install

# バックエンド依存関係をインストール
cd src/backend
pip install -r requirements.txt
cd ../..

# フロントエンド依存関係をインストール
cd src/frontend
npm install
cd ../..
```

### 2. 開発環境での実行

```bash
# 開発サーバーを起動（バックエンド + フロントエンド + Electron）
npm run dev
```

### 3. 単一実行ファイルの作成

```bash
# Step 1: ビルド依存関係の準備
npm run prepare:build

# Step 2: アプリケーションのビルド
npm run build

# Step 3: 配布用実行ファイルの作成
npm run dist:win    # Windows
npm run dist:mac    # macOS
npm run dist:linux  # Linux
```

## ビルドプロセスの詳細

### バックエンドのビルド

PyInstallerを使用してPythonアプリケーションを単一実行ファイルにパッケージ化:

```bash
# 手動でバックエンドのみビルド
npm run build:backend
```

生成されるファイル:
- `dist/python/tax-converter-backend.exe` (Windows)
- `dist/python/tax-converter-backend` (macOS/Linux)

### フロントエンドのビルド

Viteを使用してReactアプリケーションをビルド:

```bash
# 手動でフロントエンドのみビルド
npm run build:frontend
```

生成されるファイル:
- `src/frontend/dist/` - 静的Webファイル

### Electronアプリのビルド

electron-builderを使用してデスクトップアプリケーションを作成:

```bash
# 手動でElectronアプリのみビルド
npm run build:electron
```

生成されるファイル:
- `dist-exe/` - インストーラーと実行ファイル

## トラブルシューティング

### Python関連の問題

**症状**: PyInstallerが見つからない
```bash
# 解決方法
pip install pyinstaller
```

**症状**: 隠れた依存関係のエラー
```bash
# 追加パッケージをインストール
pip install pyinstaller-hooks-contrib
```

### Node.js関連の問題

**症状**: フロントエンドの依存関係エラー
```bash
# node_modulesを削除して再インストール
cd src/frontend
rm -rf node_modules package-lock.json
npm install
```

### Electron関連の問題

**症状**: Electronのビルドエラー
```bash
# Electronキャッシュをクリア
npx electron-builder clean
```

### 権限の問題（macOS/Linux）

```bash
# スクリプトファイルに実行権限を付与
chmod +x scripts/*.sh
```

## 環境変数

必要に応じて以下の環境変数を設定:

```bash
# Python実行可能ファイルのパス（カスタムPython環境の場合）
export PYTHON_EXECUTABLE=/path/to/python

# Node.js環境（開発/本番の切り替え）
export NODE_ENV=development  # または production
```

## パフォーマンス最適化

### ビルド時間の短縮

```bash
# 並列ビルドの有効化
npm config set script-shell "bash"
```

### ファイルサイズの最適化

```bash
# PyInstallerでUPX圧縮を有効化（要UPXインストール）
# scripts/build_backend.py でupx=Trueに設定
```

## 検証

### 開発環境の確認

```bash
# バックエンドAPIの確認
curl http://127.0.0.1:8000/api/health

# フロントエンドの確認
curl http://localhost:3000
```

### ビルド結果の確認

```bash
# ファイルサイズの確認
ls -lh dist/python/
ls -lh dist-exe/

# 実行ファイルの動作確認
./dist/python/tax-converter-backend
```

## サポート

問題が発生した場合:

1. このガイドのトラブルシューティングセクションを確認
2. ログファイルを確認（`logs/` ディレクトリ）
3. GitHubのIssuesで報告