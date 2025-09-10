#!/usr/bin/env python3
"""
バックエンドビルドスクリプト
PyInstallerを使用してPythonアプリケーションを単一実行ファイルにパッケージ化
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🐍 バックエンドビルドスクリプト")
    print("=" * 40)
    
    # ディレクトリ設定
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    backend_dir = project_root / "src" / "backend"
    dist_dir = project_root / "dist" / "python"
    build_dir = project_root / "build"
    
    # 作業ディレクトリを変更
    os.chdir(backend_dir)
    
    print(f"📁 作業ディレクトリ: {backend_dir}")
    print(f"📦 出力ディレクトリ: {dist_dir}")
    
    # 出力ディレクトリをクリーンアップ
    if dist_dir.exists():
        print("🧹 出力ディレクトリをクリーンアップ中...")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True)
    
    # ビルドディレクトリをクリーンアップ
    if build_dir.exists():
        print("🧹 ビルドディレクトリをクリーンアップ中...")
        shutil.rmtree(build_dir)
    
    # PyInstallerの存在確認
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
        print("✅ PyInstallerが利用可能")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstallerが見つかりません")
        print("pip install pyinstaller でインストールしてください")
        return False
    
    # ビルドコマンド構築
    build_cmd = [
        "pyinstaller",
        "--specpath", str(build_dir),
        "--workpath", str(build_dir / "work"),
        "--distpath", str(dist_dir),
        "--onefile",  # 単一実行ファイル
        "--name", "tax-converter-backend",
        "--console",  # コンソールアプリケーション
        "--clean",  # 前回のビルドファイルをクリア
        # 隠れたインポートを追加
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "uvicorn.lifespan.off", 
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "multipart",
        "--hidden-import", "email.mime.multipart",
        "--hidden-import", "email.mime.text",
        "--hidden-import", "pydantic.validators",
        "--hidden-import", "pydantic.types",
        # 除外するモジュール
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "scipy",
        "--exclude-module", "setuptools",
        # メインスクリプト
        "main.py"
    ]
    
    print("🔨 PyInstallerビルドを実行中...")
    print(f"コマンド: {' '.join(build_cmd)}")
    
    try:
        # ビルド実行
        result = subprocess.run(build_cmd, check=True, capture_output=True, text=True)
        print("✅ ビルド成功!")
        
        # ビルド結果の確認
        exe_name = "tax-converter-backend.exe" if sys.platform == "win32" else "tax-converter-backend"
        exe_path = dist_dir / exe_name
        
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"📄 実行ファイル: {exe_path}")
            print(f"📏 ファイルサイズ: {file_size:.1f} MB")
        else:
            print("⚠️  実行ファイルが見つかりません")
            return False
            
        # 追加ファイルのコピー
        print("📋 追加ファイルをコピー中...")
        
        # requirementsファイルをコピー（参考用）
        shutil.copy2("requirements.txt", dist_dir / "requirements.txt")
        
        # READMEファイルを作成
        readme_content = f"""# 税区分表変換ツール - バックエンド

## 実行方法

### Windows
```
{exe_name}
```

### macOS/Linux
```
./{exe_name}
```

サーバーは http://127.0.0.1:8000 で起動します。

## 終了方法
Ctrl+C でサーバーを停止できます。

ビルド日時: {subprocess.run(['date'], capture_output=True, text=True, shell=True).stdout.strip()}
"""
        
        with open(dist_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print("✅ バックエンドビルド完了!")
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ ビルドエラー:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)