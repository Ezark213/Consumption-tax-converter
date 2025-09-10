from typing import Optional
from .base import BaseParser
from .freee import FreeeParser
from .moneyforward import MoneyforwardParser
from .yayoi import YayoiParser

class ParserFactory:
    """
    適切なパーサーを選択するファクトリークラス
    """
    
    @staticmethod
    def get_parser(file_path: str) -> Optional[BaseParser]:
        """
        ファイルに適したパーサーを取得
        
        Args:
            file_path: 解析対象ファイルのパス
            
        Returns:
            BaseParser: 適切なパーサーインスタンス。見つからない場合はNone
        """
        # 利用可能なパーサーのリスト
        parsers = [
            FreeeParser(),
            MoneyforwardParser(),
            YayoiParser()
        ]
        
        # 各パーサーの判定メソッドを試行
        for parser in parsers:
            try:
                if parser.detect_format(file_path):
                    return parser
            except Exception:
                # 判定でエラーが発生した場合は次のパーサーを試行
                continue
        
        return None
    
    @staticmethod
    def get_supported_formats() -> dict:
        """
        サポートされているファイル形式の一覧を取得
        
        Returns:
            dict: パーサー名とサポート形式のマッピング
        """
        return {
            'freee': ['.pdf'],
            'moneyforward': ['.xlsx', '.xls'],
            'yayoi': ['.pdf']
        }