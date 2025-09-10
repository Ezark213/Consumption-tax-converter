# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all

# 現在のディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__name__))

# 追加で収集する必要があるパッケージ
packages_to_collect = [
    'fastapi',
    'uvicorn',
    'pandas',
    'openpyxl',
    'PyPDF2',
    'pydantic',
    'python_multipart',
    'starlette',
    'jinja2',
    'python_dotenv'
]

# 隠れたインポートと追加データを収集
hiddenimports = []
datas = []
binaries = []

for package in packages_to_collect:
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(package)
        datas.extend(pkg_datas)
        binaries.extend(pkg_binaries)
        hiddenimports.extend(pkg_hiddenimports)
    except Exception as e:
        print(f"Warning: Could not collect {package}: {e}")

# 手動で追加する隠れたインポート
additional_hiddenimports = [
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.loops.auto',
    'uvicorn.loops.asyncio',
    'uvicorn.loops.uvloop',
    'multipart',
    'email.mime.multipart',
    'email.mime.text',
    'email.mime.base',
    'email.encoders',
]

hiddenimports.extend(additional_hiddenimports)

# メインスクリプトの解析
a = Analysis(
    ['main.py'],
    pathex=[current_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'numpy.distutils',
        'setuptools',
        'distutils'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 重複ファイルを除去
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 単一実行ファイルとして出力
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='tax-converter-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)