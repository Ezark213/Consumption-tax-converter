# 税区分表変換ツール

日本の主要会計ソフト（freee・マネーフォワード・弥生）の税区分表から、消費税申告用の標準化されたCSVデータを生成するデスクトップアプリケーションです。

## 特徴

- **多形式対応**: freee (PDF)、マネーフォワード (Excel)、弥生 (PDF) の税区分表を自動判別・解析
- **標準化出力**: 統一されたCSV形式で課税売上・課税仕入データを出力
- **デスクトップアプリ**: Windows/Mac/Linux対応のスタンドアロンアプリケーション
- **直感的UI**: ドラッグ&ドロップによるファイルアップロードとリアルタイムプレビュー

## システム要件

- **Python 3.11+** (バックエンド処理用)
- **Node.js 18+** (フロントエンド・Electron用)
- **Windows 10+** / **macOS 10.15+** / **Ubuntu 20.04+**

## インストール

### 開発環境セットアップ

1. リポジトリをクローン:
```bash
git clone <repository-url>
cd tax-table-converter
```

2. 依存関係をインストール:
```bash
# ルートディレクトリで
npm install

# バックエンド依存関係
cd src/backend
pip install -r requirements.txt

# フロントエンド依存関係  
cd ../frontend
npm install
```

3. 開発サーバー起動:
```bash
# ルートディレクトリで
npm run dev

# または
./scripts/dev.sh
```

### 実行可能ファイルの作成

```bash
# ビルド依存関係の準備
npm run prepare:build

# ビルド
npm run build

# 実行可能ファイル作成
npm run dist:win    # Windows .exe
npm run dist:mac    # macOS .app  
npm run dist:linux  # Linux AppImage
```

## 使用方法

1. **ファイル選択**: 税区分表ファイル（PDF/Excel）をドラッグ&ドロップまたはクリックで選択
2. **自動解析**: ファイル形式を自動判別し、データを解析・正規化
3. **プレビュー確認**: 解析結果と集計情報をプレビューで確認
4. **CSV出力**: 標準化されたCSVファイル（ZIP形式）をダウンロード

## 出力ファイル

- `課税売上.csv`: 売上データの税率別集計
- `課税仕入.csv`: 仕入データの税率別集計  
- `集計サマリー.csv`: 全体の集計情報
- `処理情報.txt`: 変換処理の詳細情報

## アーキテクチャ

```
┌─────────────────┐
│   Electron      │ ← デスクトップアプリ
├─────────────────┤
│ React Frontend  │ ← ユーザーインターフェース
├─────────────────┤  
│ FastAPI Backend │ ← データ処理・API
└─────────────────┘
```

- **フロントエンド**: React 18 + TypeScript + Vite + Tailwind CSS
- **バックエンド**: Python 3.11 + FastAPI + pandas
- **デスクトップ**: Electron + IPC通信

## 開発

### ディレクトリ構成

```
tax-table-converter/
├── src/
│   ├── frontend/          # React フロントエンド
│   ├── backend/           # Python FastAPI バックエンド
│   └── electron/          # Electron メインプロセス
├── scripts/               # ビルド・開発スクリプト
├── tests/                 # テストファイル
└── sample_data/           # サンプルデータ
```

### スクリプト

- `npm run dev`: 開発環境起動（フロントエンド + バックエンド + Electron）
- `npm run build`: プロダクションビルド
- `npm run dist`: 配布用実行ファイル作成
- `npm run clean`: ビルドファイル削除

### 新しいパーサーの追加

1. `src/backend/parsers/` に新しいパーサークラスを作成
2. `BaseParser` を継承し、`detect_format()` と `parse()` を実装
3. `factory.py` にパーサーを登録

## 対応形式

| 会計ソフト | ファイル形式 | 対応状況 |
|-----------|------------|---------|
| freee会計 | PDF | ✅ 対応済み |
| マネーフォワード | Excel (.xlsx/.xls) | ✅ 対応済み |
| 弥生会計 | PDF | ✅ 対応済み |

## トラブルシューティング

### よくある問題

1. **Pythonが見つからない**
   - Python 3.11+がインストールされていることを確認
   - PATHが正しく設定されていることを確認

2. **依存関係エラー**
   - `npm install` と `pip install -r requirements.txt` を再実行

3. **ファイル解析エラー**
   - ファイルが破損していないか確認
   - 対応形式（PDF/Excel）かどうか確認

## ライセンス

MIT License

## 貢献

1. Forkしてください
2. 機能ブランチを作成してください (`git checkout -b feature/AmazingFeature`)
3. 変更をコミットしてください (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュしてください (`git push origin feature/AmazingFeature`)  
5. Pull Requestを作成してください