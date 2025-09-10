import PyPDF2
import pandas as pd
import re
from typing import Dict, List, Any
from .base import BaseParser

class YayoiParser(BaseParser):
    """
    弥生会計の勘定科目別税区分表パーサー
    """
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.pdf']
        self.parser_name = "yayoi"
    
    def detect_format(self, file_path: str) -> bool:
        """
        弥生形式のPDFファイルかどうかを判定
        """
        if not self._validate_file(file_path):
            return False
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # 最初の数ページから弥生の特徴的なテキストを検索
                for page_num in range(min(3, len(pdf_reader.pages))):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # 弥生の特徴的なキーワードをチェック（勘定科目別税区分表がキー）
                    if '勘定科目別税区分表' in text:
                        return True
                    
                    # 弥生ブランドの確認
                    if '弥生' in text or 'YAYOI' in text:
                        return True
                    
                    # 請求書区分別も弥生の特徴
                    if '請求書区分別' in text:
                        return True
            
            return False
            
        except Exception:
            return False
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        弥生形式のPDFを解析
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                # 全ページのテキストを抽出
                for page in pdf_reader.pages:
                    full_text += page.extract_text() + "\n"
            
            # 売上データと仕入データを分離して抽出
            sales_data = self._extract_sales_data(full_text)
            purchase_data = self._extract_purchase_data(full_text)
            
            # メタデータ抽出
            metadata = self._extract_metadata(full_text)
            
            return self._create_standard_output(sales_data, purchase_data, metadata)
            
        except Exception as e:
            return {
                'sales_items': [],
                'purchase_items': [],
                'taxable_sales_total': 0,
                'taxable_purchases_total': 0,
                'parser_type': self.parser_name,
                'warnings': [],
                'errors': [f"Parse error: {str(e)}"]
            }
    
    def _extract_sales_data(self, text: str) -> List[Dict]:
        """
        売上データを抽出（弥生形式）
        """
        sales_data = []
        
        # 弥生特有のレイアウトパターンを考慮
        lines = text.split('\n')
        
        # 売上関連の行を特定
        in_sales_section = False
        
        for line in lines:
            line = line.strip()
            
            # セクション開始の判定
            if any(keyword in line for keyword in ['売上', '収入', '課税売上']):
                if any(keyword in line for keyword in ['科目', '区分', '合計']):
                    in_sales_section = True
                    continue
            
            # セクション終了の判定
            if in_sales_section and any(keyword in line for keyword in ['仕入', '費用', '合計計']):
                break
            
            if in_sales_section and line:
                # 弥生特有のパターンマッチング
                # 例: "売上高　　　　　課税売上10%　　　54,404,148"
                pattern = r'([^\d\s]+)\s*([^0-9]*(?:課税|非課税|不課税)[^0-9]*(?:\d+%)?)\s*([\d,]+)'
                match = re.search(pattern, line)
                
                if match:
                    account_name = self._standardize_account_name(match.group(1))
                    tax_classification = match.group(2).strip()
                    amount = self._extract_numeric_value(match.group(3))
                    
                    if account_name and amount > 0:
                        tax_rate = self._extract_tax_rate_from_classification(tax_classification)
                        sales_data.append({
                            'account_name': account_name,
                            'tax_rate': tax_rate,
                            'amount': amount,
                            'taxable_amount': amount if self._is_taxable_yayoi(tax_classification) else 0
                        })
        
        return sales_data
    
    def _extract_purchase_data(self, text: str) -> List[Dict]:
        """
        仕入データを抽出（弥生形式）
        """
        purchase_data = []
        
        lines = text.split('\n')
        in_purchase_section = False
        
        for line in lines:
            line = line.strip()
            
            # セクション開始の判定
            if any(keyword in line for keyword in ['仕入', '費用', '課税仕入']):
                if any(keyword in line for keyword in ['科目', '区分', '合計']):
                    in_purchase_section = True
                    continue
            
            if in_purchase_section and line:
                # 弥生特有のパターンマッチング
                pattern = r'([^\d\s]+)\s*([^0-9]*(?:課税|非課税|不課税)[^0-9]*(?:\d+%)?)\s*([\d,]+)'
                match = re.search(pattern, line)
                
                if match:
                    account_name = self._standardize_account_name(match.group(1))
                    tax_classification = match.group(2).strip()
                    amount = self._extract_numeric_value(match.group(3))
                    
                    if account_name and amount > 0:
                        tax_rate = self._extract_tax_rate_from_classification(tax_classification)
                        purchase_data.append({
                            'account_name': account_name,
                            'tax_rate': tax_rate,
                            'amount': amount,
                            'taxable_amount': amount if self._is_taxable_yayoi(tax_classification) else 0
                        })
        
        return purchase_data
    
    def _extract_tax_rate_from_classification(self, classification: str) -> str:
        """
        税区分から税率を抽出
        """
        if '10%' in classification or '10％' in classification:
            return '10%'
        elif '8%' in classification or '8％' in classification:
            if '軽減' in classification:
                return '軽減8%'
            else:
                return '8%'
        elif '非課税' in classification:
            return '非課税'
        elif '不課税' in classification:
            return '不課税'
        elif '輸出' in classification:
            return '輸出'
        else:
            return '課税'
    
    def _is_taxable_yayoi(self, classification: str) -> bool:
        """
        課税対象かどうかを判定（弥生形式）
        """
        taxable_keywords = ['課税', '10%', '8%', '軽減']
        non_taxable_keywords = ['非課税', '不課税']
        
        # 非課税・不課税が明示されている場合
        if any(keyword in classification for keyword in non_taxable_keywords):
            return False
        
        # 課税が明示されている場合
        if any(keyword in classification for keyword in taxable_keywords):
            return True
        
        return False
    
    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """
        メタデータを抽出
        """
        metadata = {}
        
        # 期間の抽出（弥生形式）
        period_patterns = [
            r'期間[：:]\s*(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})日.*?(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})日',
            r'(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})日.*?(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})日'
        ]
        
        for pattern in period_patterns:
            period_match = re.search(pattern, text)
            if period_match:
                metadata['period_start'] = f"{period_match.group(1)}-{period_match.group(2):0>2}-{period_match.group(3):0>2}"
                metadata['period_end'] = f"{period_match.group(4)}-{period_match.group(5):0>2}-{period_match.group(6):0>2}"
                break
        
        # 会社名の抽出
        company_patterns = [
            r'(株式会社[^\s]+)',
            r'(有限会社[^\s]+)',
            r'(合同会社[^\s]+)',
            r'([^\s]+株式会社)',
            r'([^\s]+有限会社)'
        ]
        
        for pattern in company_patterns:
            company_match = re.search(pattern, text)
            if company_match:
                metadata['company_name'] = company_match.group(1)
                break
        
        return metadata