#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
税区分表変換ツール - 文字エンコーディング最終テスト
"""

import sys
import os
from pathlib import Path

# プロジェクトパスを設定
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src' / 'backend'))

def test_csv_encoding():
    """CSV文字エンコーディングテスト"""
    print("文字エンコーディング対応テスト開始...")
    
    try:
        from csv_generator import CSVGenerator
        
        # テストデータ（日本語文字を含む）
        test_data = {
            'sales_items': [
                {
                    'account_name': '売上高',
                    'tax_rate': '軽減税率8%',
                    'amount': 1000000
                }
            ],
            'purchase_items': [
                {
                    'account_name': '仕入高',
                    'tax_rate': '標準税率10%',
                    'amount': 800000
                }
            ],
            'company_name': 'テスト株式会社',
            'taxable_sales_total': 1000000,
            'taxable_purchases_total': 800000
        }
        
        generator = CSVGenerator()
        zip_data = generator.generate_zip(test_data)
        
        print(f"[OK] ZIPファイル生成成功 ({len(zip_data):,} bytes)")
        
        # ZIPファイルをテスト出力
        output_path = 'encoding_test_output.zip'
        with open(output_path, 'wb') as f:
            f.write(zip_data)
        
        import zipfile
        with zipfile.ZipFile(output_path, 'r') as zip_file:
            file_list = zip_file.namelist()
            print("\n生成されたファイル:")
            for filename in file_list:
                print(f"  - {filename}")
            
            # エンコーディング確認
            encoding_tests = [
                ('課税売上_SJIS.csv', 'shift_jis', 'Windows Excel用'),
                ('課税売上_UTF8.csv', 'utf-8-sig', 'Mac/Google Sheets用')
            ]
            
            for filename, encoding, description in encoding_tests:
                if filename in file_list:
                    try:
                        with zip_file.open(filename) as csv_file:
                            content = csv_file.read()
                            decoded = content.decode(encoding)
                            
                            if '売上高' in decoded:
                                print(f"[OK] {description}: 文字エンコーディング確認")
                            else:
                                print(f"[ERROR] {description}: 日本語文字確認失敗")
                                return False
                    except Exception as e:
                        print(f"[ERROR] {description}: {e}")
                        return False
                else:
                    print(f"[ERROR] {filename} が見つかりません")
                    return False
        
        print("\n[SUCCESS] 文字エンコーディング対応テスト完了!")
        print("\n使用方法:")
        print("1. Windows Excel → SJIS版ファイルを使用")
        print("2. Mac Excel/Google Sheets → UTF8版ファイルを使用")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_csv_encoding()
    if success:
        print("\n[RESULT] 文字化け対策: 完了")
    else:
        print("\n[RESULT] 文字化け対策: 失敗")
    
    sys.exit(0 if success else 1)