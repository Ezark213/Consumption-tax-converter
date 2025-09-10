from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
from typing import Optional
import os
import tempfile
import io
from parsers.factory import ParserFactory
from normalizer import TaxDataNormalizer
from csv_generator import CSVGenerator

app = FastAPI(title="Tax Table Converter API", version="1.0.0")

# CORS設定（Electronからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバル変数（セッション管理用）
processed_data = {}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    ファイルアップロード・解析エンドポイント
    """
    try:
        # ファイル拡張子チェック
        allowed_extensions = {'.pdf', '.xlsx', '.xls'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format: {file_extension}"
            )
        
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # 適切なパーサーを取得
            parser = ParserFactory.get_parser(tmp_file_path)
            if not parser:
                raise HTTPException(
                    status_code=400,
                    detail="Unknown file format. Supported formats: freee, MoneyForward, Yayoi"
                )
            
            print(f"Selected parser: {parser.__class__.__name__}")
            
            # データ解析
            raw_data = parser.parse(tmp_file_path)
            print(f"Raw data sales items: {len(raw_data.get('sales_items', []))}")
            print(f"Sales items: {raw_data.get('sales_items', [])}")
            
            # データ正規化
            normalizer = TaxDataNormalizer()
            normalized_data = normalizer.normalize(raw_data)
            print(f"Normalized data sales total: {normalized_data.get('taxable_sales_total', 0)}")
            
            # セッション保存（実際のアプリでは適切なセッション管理を実装）
            session_id = file.filename + "_processed"
            processed_data[session_id] = normalized_data
            
            # プレビューデータ生成
            preview = {
                "session_id": session_id,
                "filename": file.filename,
                "parser_type": parser.__class__.__name__,
                "taxable_sales": float(normalized_data.get('taxable_sales_total', 0)),
                "taxable_purchases": float(normalized_data.get('taxable_purchases_total', 0)),
                "warnings": normalized_data.get('warnings', []),
                "errors": normalized_data.get('errors', []),
                "sales_items_count": len(normalized_data.get('sales_items', [])),
                "purchase_items_count": len(normalized_data.get('purchase_items', [])),
                "encoding_info": {
                    "formats": ["Shift_JIS (Windows Excel用)", "UTF-8 (Mac/Google Sheets用)"],
                    "recommendation": "Windows Excelをお使いの場合はSJIS版ファイルをご使用ください"
                }
            }
            
            return preview
            
        finally:
            # 一時ファイル削除
            os.unlink(tmp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{session_id}")
async def download_csv(session_id: str):
    """
    CSV生成・ダウンロードエンドポイント
    """
    try:
        if session_id not in processed_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        data = processed_data[session_id]
        
        # CSV生成
        csv_generator = CSVGenerator()
        csv_content = csv_generator.generate_zip(data)
        
        # ZIPファイルとして返却（文字エンコーディング対応）
        headers = {
            "Content-Disposition": "attachment; filename*=UTF-8''tax_data_converted.zip",
            "Content-Type": "application/zip; charset=utf-8",
            "Cache-Control": "no-cache"
        }
        
        return StreamingResponse(
            io.BytesIO(csv_content),
            media_type="application/zip",
            headers=headers
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "ok", "version": "1.0.0"}

@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """セッションクリア"""
    if session_id in processed_data:
        del processed_data[session_id]
        return {"message": "Session cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

if __name__ == "__main__":
    import sys
    import multiprocessing
    
    # PyInstallerでのマルチプロセシング対応
    if getattr(sys, 'frozen', False):
        multiprocessing.freeze_support()
    
    # PyInstallerビルド時はreloadを無効化
    is_frozen = getattr(sys, 'frozen', False)
    
    uvicorn.run(
        "main:app" if not is_frozen else app, 
        host="127.0.0.1", 
        port=8000, 
        reload=False if is_frozen else True,
        log_level="info"
    )