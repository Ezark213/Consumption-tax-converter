#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
税区分表変換ツール - メインエントリーポイント
実行ファイル: python tax_converter.py
"""

import sys
import os
from pathlib import Path

# Windows環境でのUnicodeエラーを回避
if sys.platform == 'win32':
    import codecs
    # コンソール出力のエンコーディングを強制的にUTF-8に設定
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

# プロジェクトのsrcディレクトリをパスに追加
project_root = Path(__file__).parent
src_path = project_root / "src"
backend_path = src_path / "backend"

sys.path.insert(0, str(src_path))
sys.path.insert(0, str(backend_path))

def main():
    """メイン関数"""
    print("=== Tax Classification Table Converter v1.0 ===")
    print("Convert freee, MoneyForward, Yayoi tax tables to CSV format\n")
    
    # コマンドライン引数でファイルが指定された場合
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            process_file_cli(file_path)
        else:
            print(f"Error: File not found: {file_path}")
            return
    else:
        # GUIモードで起動
        try:
            from standalone_app import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"GUI startup failed: {e}")
            print("Using command line version...")
            interactive_mode()

def process_file_cli(file_path):
    """コマンドライン版のファイル処理"""
    try:
        from backend.parsers.factory import ParserFactory
        from backend.normalizer import TaxDataNormalizer
        from backend.csv_generator import CSVGenerator
        
        print(f"Processing file: {file_path}")
        
        # パーサー選択
        parser = ParserFactory.get_parser(file_path)
        if not parser:
            print("Error: Unsupported file format")
            print("Supported: freee (PDF), MoneyForward (PDF/Excel), Yayoi (PDF)")
            return
        
        print(f"Detected system: {parser.__class__.__name__.replace('Parser', '')}")
        
        # データ解析
        raw_data = parser.parse(file_path)
        
        # データ正規化
        normalizer = TaxDataNormalizer()
        processed_data = normalizer.normalize(raw_data)
        
        # 結果表示
        sales_items = processed_data.get('sales_items', [])
        print(f"\n=== Analysis Result ===")
        print(f"Sales items count: {len(sales_items)}")
        
        if sales_items:
            print("\nSales data:")
            for item in sales_items:
                account = item.get('account_name', 'Unknown')
                tax_rate = item.get('tax_rate', 'Unknown')
                amount = item.get('amount', 0)
                print(f"  {account}: ¥{amount:,} ({tax_rate})")
            
            taxable_total = processed_data.get('taxable_sales_total', 0)
            print(f"\nTaxable sales total: ¥{taxable_total:,}")
        
        # CSV出力
        output_path = file_path.replace('.pdf', '_converted.zip').replace('.xlsx', '_converted.zip')
        
        csv_generator = CSVGenerator()
        zip_content = csv_generator.generate_zip(processed_data)
        
        with open(output_path, 'wb') as f:
            f.write(zip_content)
        
        print(f"\nCSV file generated: {output_path}")
        
        # 警告・エラー表示
        warnings = processed_data.get('warnings', [])
        errors = processed_data.get('errors', [])
        
        if warnings:
            print("\n=== Warnings ===")
            for warning in warnings:
                print(f"  [Warning] {warning}")
        
        if errors:
            print("\n=== Errors ===")
            for error in errors:
                print(f"  [Error] {error}")
        
    except Exception as e:
        print(f"Error occurred: {e}")

def interactive_mode():
    """対話モード"""
    print("\nRunning in interactive mode.")
    print("Enter file path to process:")
    
    while True:
        file_path = input("> ").strip().strip('"\'')
        
        if not file_path:
            print("Exiting.")
            break
        
        if os.path.exists(file_path):
            process_file_cli(file_path)
            print("\nEnter another file path to process, or press Enter to exit:")
        else:
            print(f"File not found: {file_path}")
            print("Please enter a valid file path:")

if __name__ == "__main__":
    main()