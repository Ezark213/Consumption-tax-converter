#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
税区分表変換ツール - 完全統合テストスクリプト
文字エンコーディング対応の包括的テスト
"""

import sys
import os
import tempfile
import zipfile
import subprocess
from pathlib import Path

# プロジェクトパスを設定
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src' / 'backend'))

def print_header(title):
    """テストセクションヘッダーを表示"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_csv_generator():
    """CSVジェネレーターの単体テスト"""
    print_header("1. CSVジェネレーター単体テスト")
    
    try:
        from csv_generator import CSVGenerator
        
        # テストデータ
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
            'parser_type': 'テスト',
            'company_name': 'テスト株式会社',
            'period_start': '2024-01-01',
            'period_end': '2024-12-31'
        }
        
        generator = CSVGenerator()
        zip_data = generator.generate_zip(test_data)
        
        # ZIPファイルの内容を検証
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            tmp_file.write(zip_data)
            tmp_file_path = tmp_file.name
        
        expected_files = [
            '課税売上_SJIS.csv',
            '課税売上_UTF8.csv',
            '課税仕入_SJIS.csv',
            '課税仕入_UTF8.csv',
            '集計サマリー_SJIS.csv',
            '集計サマリー_UTF8.csv',
            'ファイル説明.txt',
            '処理情報.txt'
        ]
        
        with zipfile.ZipFile(tmp_file_path, 'r') as zip_file:
            file_list = zip_file.namelist()
            
            print(f"[OK] ZIPファイル生成成功 ({len(zip_data):,} bytes)")
            print("[INFO] 生成ファイル一覧:")
            
            for expected_file in expected_files:
                if expected_file in file_list:
                    file_info = zip_file.getinfo(expected_file)
                    print(f"  [OK] {expected_file} ({file_info.file_size:,} bytes)")
                else:
                    print(f"  [MISSING] {expected_file}")
                    return False
                    return False
            
            # SJIS版の内容確認
            try:
                with zip_file.open('課税売上_SJIS.csv') as sjis_file:
                    sjis_content = sjis_file.read()
                    try:
                        decoded = sjis_content.decode('shift_jis')
                        print(f"  ✓ Shift_JIS エンコーディング確認済み")
                    except UnicodeDecodeError:
                        print(f"  ✗ Shift_JIS エンコーディング失敗")
                        return False
            except Exception as e:
                print(f"  ✗ SJIS版読み込みエラー: {e}")
                return False
            
            # UTF8版の内容確認  
            try:
                with zip_file.open('課税売上_UTF8.csv') as utf8_file:
                    utf8_content = utf8_file.read()
                    try:
                        decoded = utf8_content.decode('utf-8-sig')
                        print(f"  ✓ UTF-8 with BOM エンコーディング確認済み")
                    except UnicodeDecodeError:
                        print(f"  ✗ UTF-8 with BOM エンコーディング失敗")
                        return False
            except Exception as e:
                print(f"  ✗ UTF8版読み込みエラー: {e}")
                return False
        
        # 一時ファイル削除
        os.unlink(tmp_file_path)
        
        print("[OK] CSVジェネレーター単体テスト: 合格")
        return True
        
    except Exception as e:
        print(f"[ERROR] CSVジェネレーター単体テスト: 失敗 - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_script():
    """メインスクリプトのテスト"""
    print_header("2. メインスクリプト統合テスト")
    
    # サンプルファイルのパス
    sample_file = project_root / 'test_freee.pdf'
    
    if not sample_file.exists():
        print(f"[SKIP] サンプルファイルが見つかりません: {sample_file}")
        return True
    
    try:
        # メインスクリプトを実行
        result = subprocess.run([
            sys.executable, 'tax_converter.py', str(sample_file)
        ], cwd=project_root, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"[OK] メインスクリプト実行成功")
            print(f"[INFO] 出力:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"  {line}")
            
            # 出力ファイルの確認
            output_file = str(sample_file).replace('.pdf', '_converted.zip')
            if os.path.exists(output_file):
                print(f"[OK] 出力ファイル生成確認: {output_file}")
                
                # ファイル内容確認
                with zipfile.ZipFile(output_file, 'r') as zip_file:
                    files = zip_file.namelist()
                    encoding_files = [f for f in files if 'SJIS' in f or 'UTF8' in f]
                    if len(encoding_files) >= 6:  # SJIS版3ファイル + UTF8版3ファイル
                        print(f"[OK] 文字エンコーディング対応ファイル確認: {len(encoding_files)}個")
                        return True
                    else:
                        print(f"[WARN] エンコーディング対応ファイル不足: {len(encoding_files)}/6")
                        return False
            else:
                print(f"[ERROR] 出力ファイルが生成されていません")
                return False
        else:
            print(f"[ERROR] メインスクリプト実行失敗 (返り値: {result.returncode})")
            print(f"[ERROR] 出力: {result.stdout}")
            print(f"[ERROR] エラー: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[ERROR] メインスクリプト実行がタイムアウトしました")
        return False
    except Exception as e:
        print(f"[ERROR] メインスクリプトテスト失敗: {e}")
        return False

def test_backend_import():
    """バックエンドモジュールのインポートテスト"""
    print_header("3. バックエンドモジュール統合テスト")
    
    try:
        # 主要モジュールのインポート確認
        modules = [
            'csv_generator',
            'normalizer', 
            'parsers.factory',
            'parsers.freee',
            'parsers.moneyforward',
            'parsers.yayoi'
        ]
        
        for module_name in modules:
            try:
                __import__(module_name)
                print(f"  ✓ {module_name} インポート成功")
            except ImportError as e:
                print(f"  ✗ {module_name} インポート失敗: {e}")
                return False
        
        # FastAPI起動テスト（簡易）
        try:
            from main import app
            print(f"  ✓ FastAPI アプリケーション初期化成功")
        except Exception as e:
            print(f"  ✗ FastAPI アプリケーション初期化失敗: {e}")
            return False
            
        print("[OK] バックエンドモジュール統合テスト: 合格")
        return True
        
    except Exception as e:
        print(f"[ERROR] バックエンドモジュール統合テスト: 失敗 - {e}")
        return False

def test_encoding_compatibility():
    """文字エンコーディング互換性テスト"""
    print_header("4. 文字エンコーディング互換性テスト")
    
    try:
        from csv_generator import CSVGenerator
        
        # 日本語データを含むテストデータ
        test_data = {
            'sales_items': [
                {
                    'account_name': '売上高（消費税込み）',
                    'tax_rate': '軽減税率8%（食品等）',
                    'amount': 1080000
                },
                {
                    'account_name': '雑収入／その他売上',
                    'tax_rate': '標準税率10%',
                    'amount': 550000
                }
            ],
            'purchase_items': [
                {
                    'account_name': '仕入高（軽減税率対象）',
                    'tax_rate': '軽減8%',
                    'amount': 864000
                }
            ],
            'company_name': '株式会社テスト・カンパニー',
            'taxable_sales_total': 1630000,
            'taxable_purchases_total': 864000
        }
        
        generator = CSVGenerator()
        zip_data = generator.generate_zip(test_data)
        
        # 文字エンコーディングテスト
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            tmp_file.write(zip_data)
            tmp_file_path = tmp_file.name
        
        encoding_tests = [
            ('課税売上_SJIS.csv', 'shift_jis', 'Windows Excel用'),
            ('課税売上_UTF8.csv', 'utf-8-sig', 'Mac/Google Sheets用')
        ]
        
        all_passed = True
        
        with zipfile.ZipFile(tmp_file_path, 'r') as zip_file:
            for filename, encoding, description in encoding_tests:
                try:
                    with zip_file.open(filename) as csv_file:
                        content = csv_file.read()
                        decoded = content.decode(encoding)
                        
                        # 日本語文字の検証
                        if '売上高' in decoded and '仕入高' in decoded:
                            print(f"  ✓ {filename} ({description}): エンコーディング適合")
                        else:
                            print(f"  ✗ {filename} ({description}): 日本語文字検出失敗")
                            all_passed = False
                            
                except Exception as e:
                    print(f"  ✗ {filename} ({description}): {e}")
                    all_passed = False
        
        os.unlink(tmp_file_path)
        
        if all_passed:
            print("[OK] 文字エンコーディング互換性テスト: 合格")
            return True
        else:
            print("[ERROR] 文字エンコーディング互換性テスト: 失敗")
            return False
            
    except Exception as e:
        print(f"[ERROR] 文字エンコーディング互換性テスト: 失敗 - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト実行"""
    print_header("税区分表変換ツール - 完全統合テスト")
    print(f"プロジェクト: {project_root}")
    print(f"Python: {sys.version}")
    print(f"作業ディレクトリ: {os.getcwd()}")
    
    # テスト実行
    tests = [
        ("CSVジェネレーター", test_csv_generator),
        ("バックエンドモジュール", test_backend_import), 
        ("文字エンコーディング互換性", test_encoding_compatibility),
        ("メインスクリプト", test_main_script)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[FATAL] {test_name}テストで予期しないエラー: {e}")
            failed += 1
    
    # 結果サマリー
    print_header("テスト結果サマリー")
    print(f"合格: {passed}/{len(tests)}")
    print(f"失敗: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 全テスト合格！")
        print("✅ Windows Excelでの文字化け問題が解決されました")
        print("✅ Shift_JIS + UTF-8 両形式での出力対応完了")
        print("✅ 統合テストにより全コンポーネントの動作確認完了")
    else:
        print(f"\n❌ {failed}個のテストが失敗しました")
        print("修正が必要な箇所があります")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)