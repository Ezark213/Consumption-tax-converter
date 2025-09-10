# 税区分表変換ツール - ローカル版

日本の会計ソフト（freee、マネーフォワード、弥生）の税区分表をCSVに変換するローカルアプリケーションです。

## 使用方法

### GUI版（推奨）

```bash
python tax_converter.py
```

tkinterベースの直感的なGUIでファイルを選択し、CSVに変換できます。

### コマンドライン版

特定ファイルを直接処理:
```bash
python tax_converter.py "ファイルパス"
```

対話モード:
```bash
python tax_converter.py
# GUIが起動できない場合は自動的に対話モードに切り替わります
```

## 対応ファイル形式

- **freee**: PDF形式の消費税区分別表
- **マネーフォワード**: PDF/Excel形式の税区分表  
- **弥生**: PDF形式の勘定科目別税区分表

## 出力ファイル

変換後のZIPファイルには以下が含まれます：

- **課税売上.csv** - 売上データの税率別集計
- **課税仕入.csv** - 仕入データの税率別集計  
- **集計サマリー.csv** - 全体の集計情報
- **処理情報.txt** - 変換処理の詳細情報

## 特徴

- ✅ 文字化け対応済み（Windows Excel互換）
- ✅ 自動パーサー検出
- ✅ エラー・警告表示
- ✅ 日本語・英語両対応のコンソール出力
- ✅ GUI/CLI両対応

## 技術仕様

- Python 3.7+
- tkinter（GUI）
- pandas（データ処理）
- PyPDF2（PDF解析）
- openpyxl（Excel処理）

## 注意事項

CSV出力はWindows Excel用にBOM付きUTF-8でエンコードされています。