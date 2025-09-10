#!/usr/bin/env python3
"""
ビルド依存関係インストールスクリプト
PyInstallerとその他のビルドに必要なパッケージをインストール
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description=""):
    """コマンドを実行し、結果を表示"""
    if description:
        print(f"📦 {description}")
    
    print(f"実行中: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ エラー: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    print("🔧 ビルド依存関係インストールスクリプト")
    print("=" * 50)
    
    # プロジェクトルートディレクトリ
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    backend_dir = project_root / "src" / "backend"
    
    print(f"📁 プロジェクトルート: {project_root}")
    print(f"📁 バックエンドディレクトリ: {backend_dir}")
    
    # Python環境確認
    print(f"🐍 Python環境: {sys.executable}")
    print(f"🐍 Pythonバージョン: {sys.version}")
    
    # バックエンドディレクトリに移動
    os.chdir(backend_dir)
    
    # 基本の依存関係をインストール
    if not run_command([
        sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
    ], "基本依存関係をインストール中"):
        return False
    
    # ビルド用の依存関係をインストール
    build_deps = [
        "pyinstaller>=6.0.0",
        "pyinstaller-hooks-contrib",
        "altgraph"
    ]
    
    # プラットフォーム固有の依存関係
    if sys.platform == "win32":
        build_deps.extend([
            "pywin32>=306",
            "pywin32-ctypes"
        ])
    elif sys.platform == "darwin":
        build_deps.extend([
            "pyobjc-framework-Cocoa",
            "pyobjc-framework-Quartz"
        ])
    
    for dep in build_deps:
        if not run_command([
            sys.executable, "-m", "pip", "install", dep
        ], f"{dep} をインストール中"):
            print(f"⚠️  {dep} のインストールに失敗しましたが、続行します")
    
    # インストール済みパッケージの確認
    print("\n📋 インストール済みの主要パッケージ:")
    important_packages = [
        "fastapi", "uvicorn", "pandas", "pyinstaller", 
        "openpyxl", "PyPDF2", "pydantic"
    ]
    
    for package in important_packages:
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "show", package
            ], capture_output=True, text=True, check=True)
            
            # バージョン情報を抽出
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    version = line.split(':')[1].strip()
                    print(f"  ✅ {package}: {version}")
                    break
        except subprocess.CalledProcessError:
            print(f"  ❌ {package}: 未インストール")
    
    print("\n✅ ビルド依存関係の準備が完了しました！")
    print("\n次のステップ:")
    print("1. npm run build:backend  - バックエンドをビルド")
    print("2. npm run build:frontend - フロントエンドをビルド") 
    print("3. npm run build:electron - Electronアプリをビルド")
    print("4. npm run dist          - 配布用ファイルを生成")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)