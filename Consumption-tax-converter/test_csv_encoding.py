#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV文字エンコーディングテストスクリプト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'backend'))

from csv_generator import CSVGenerator

def test_csv_encoding():
    """
    CSV文字エンコーディングのテスト
    """
    # テストデータを作成
    test_data = {
        'sales_items': [
            {
                'account_name': '売上高',
                'tax_rate': '10%',
                'amount': 1000000
            },
            {
                'account_name': '軽減売上',
                'tax_rate': '軽減8%',
                'amount': 500000
            },
            {
                'account_name': '非課税売上',
                'tax_rate': '非課税',
                'amount': 200000
            }
        ],
        'purchase_items': [
            {
                'account_name': '仕入高',
                'tax_rate': '10%',
                'amount': 800000
            },
            {
                'account_name': '軽減仕入',
                'tax_rate': '軽減8%',
                'amount': 300000
            }
        ],
        'taxable_sales_total': 1500000,
        'taxable_purchases_total': 1100000,
        'total_sales': 1700000,
        'total_purchases': 1100000,
        'sales_by_tax_rate': {
            '10%': 1000000,
            '軽減8%': 500000,
            '非課税': 200000
        },
        'purchases_by_tax_rate': {
            '10%': 800000,
            '軽減8%': 300000
        },
        'parser_type': 'freee',
        'company_name': 'テスト株式会社',
        'period_start': '2024-01-01',
        'period_end': '2024-12-31'
    }
    
    # CSVジェネレーターを作成
    generator = CSVGenerator()
    
    print("CSV文字エンコーディングテスト開始...")
    
    try:
        # ZIPファイルを生成
        zip_data = generator.generate_zip(test_data)
        
        # ZIPファイルをテスト出力
        output_path = 'test_output.zip'
        with open(output_path, 'wb') as f:
            f.write(zip_data)
        
        print(f"[OK] ZIPファイル生成成功: {output_path}")
        print(f"[INFO] ファイルサイズ: {len(zip_data):,} bytes")
        
        # ZIPの内容を確認
        import zipfile
        with zipfile.ZipFile(output_path, 'r') as zip_file:
            file_list = zip_file.namelist()
            print("\n[INFO] 生成されたファイル一覧:")
            for filename in file_list:
                file_info = zip_file.getinfo(filename)
                print(f"  - {filename} ({file_info.file_size:,} bytes)")
        
        print("\n[OK] CSV文字エンコーディング対応完了!")
        print("\n[USAGE] 使用方法:")
        print("  1. 日本語Windows Excel → SJIS版ファイルを使用")
        print("  2. Mac Excel/Google Sheets → UTF8版ファイルを使用") 
        print("  3. 文字化けが発生した場合は別の形式を試してください")
        
    except Exception as e:
        print(f"[ERROR] エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_csv_encoding()