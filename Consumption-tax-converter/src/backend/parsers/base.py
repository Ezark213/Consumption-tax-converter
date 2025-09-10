from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List, Any
import os

class BaseParser(ABC):
    """
    税区分表パーサーの基底クラス
    """
    
    def __init__(self):
        self.supported_extensions = []
        self.parser_name = ""
    
    @abstractmethod
    def detect_format(self, file_path: str) -> bool:
        """
        ファイル形式を判定する
        
        Args:
            file_path: 解析対象ファイルのパス
            
        Returns:
            bool: このパーサーで処理可能な場合True
        """
        pass
    
    @abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        データを標準形式に変換する
        
        Args:
            file_path: 解析対象ファイルのパス
            
        Returns:
            Dict: 正規化されたデータ
        """
        pass
    
    def _validate_file(self, file_path: str) -> bool:
        """
        ファイルの基本的な検証
        
        Args:
            file_path: ファイルパス
            
        Returns:
            bool: ファイルが有効な場合True
        """
        if not os.path.exists(file_path):
            return False
        
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in self.supported_extensions
    
    def _extract_numeric_value(self, text: str) -> float:
        """
        テキストから数値を抽出する共通処理
        
        Args:
            text: 数値を含むテキスト
            
        Returns:
            float: 抽出された数値
        """
        if pd.isna(text) or text is None:
            return 0.0
        
        # 文字列に変換
        text = str(text)
        
        # カンマと円マークを除去
        text = text.replace(',', '').replace('¥', '').replace('￥', '')
        
        # 数値以外の文字を除去（負号は保持）
        import re
        numeric_text = re.sub(r'[^\d.-]', '', text)
        
        try:
            return float(numeric_text) if numeric_text else 0.0
        except ValueError:
            return 0.0
    
    def _standardize_account_name(self, account_name: str) -> str:
        """
        勘定科目名を標準化する
        
        Args:
            account_name: 勘定科目名
            
        Returns:
            str: 標準化された勘定科目名
        """
        if pd.isna(account_name) or account_name is None:
            return ""
        
        # 前後の空白を除去
        account_name = str(account_name).strip()
        
        # 全角・半角の統一
        account_name = account_name.replace('（', '(').replace('）', ')')
        
        return account_name
    
    def _create_standard_output(self, sales_data: List[Dict], purchase_data: List[Dict], 
                              metadata: Dict = None) -> Dict[str, Any]:
        """
        標準出力形式を作成する
        
        Args:
            sales_data: 売上データリスト
            purchase_data: 仕入データリスト
            metadata: メタデータ
            
        Returns:
            Dict: 標準化されたデータ
        """
        result = {
            'sales_items': sales_data,
            'purchase_items': purchase_data,
            'taxable_sales_total': sum(item.get('taxable_amount', 0) for item in sales_data),
            'taxable_purchases_total': sum(item.get('taxable_amount', 0) for item in purchase_data),
            'parser_type': self.parser_name,
            'warnings': [],
            'errors': []
        }
        
        if metadata:
            result.update(metadata)
        
        return result