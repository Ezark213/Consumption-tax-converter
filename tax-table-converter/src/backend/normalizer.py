from typing import Dict, List, Any
import pandas as pd

class TaxDataNormalizer:
    """
    税区分データの正規化クラス
    """
    
    def __init__(self):
        # 税率の標準化マッピング
        self.tax_rate_mapping = {
            '10%': '10%',
            '10％': '10%',
            '標準10%': '10%',
            '標準': '10%',
            '8%': '軽減8%',
            '8％': '軽減8%',
            '軽減8%': '軽減8%',
            '軽減8％': '軽減8%',
            '軽減': '軽減8%',
            '非課税': '非課税',
            '不課税': '不課税',
            '輸出': '輸出売上',
            '輸出売上': '輸出売上',
            '免税': '輸出売上'
        }
        
        # 勘定科目の標準化マッピング
        self.account_mapping = {
            # 売上関連
            '売上': '売上高',
            '売上高': '売上高',
            '営業収入': '売上高',
            '事業収入': '売上高',
            '雑収入': '雑収入',
            '雑益': '雑収入',
            'その他収入': 'その他収入',
            
            # 仕入・費用関連
            '仕入': '仕入高',
            '仕入高': '仕入高',
            '商品仕入': '仕入高',
            '材料仕入': '仕入高',
            '外注費': '外注費',
            '外注工賃': '外注費',
            '業務委託費': '外注費',
            '広告宣伝費': '広告宣伝費',
            '接待交際費': '接待交際費',
            '旅費交通費': '旅費交通費',
            '通信費': '通信費',
            '水道光熱費': '水道光熱費',
            '消耗品費': '消耗品費',
            '事務用品費': '消耗品費',
            '租税公課': '租税公課',
            '地代家賃': '地代家賃',
            '賃借料': '地代家賃',
            '支払手数料': '支払手数料',
            '修繕費': '修繕費',
            '保険料': '保険料',
            '減価償却費': '減価償却費'
        }
    
    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生データを正規化する
        
        Args:
            raw_data: パーサーからの生データ
            
        Returns:
            Dict: 正規化されたデータ
        """
        try:
            normalized_data = raw_data.copy()
            
            # 売上データの正規化
            if 'sales_items' in raw_data:
                normalized_data['sales_items'] = self._normalize_items(raw_data['sales_items'])
            
            # 仕入データの正規化
            if 'purchase_items' in raw_data:
                normalized_data['purchase_items'] = self._normalize_items(raw_data['purchase_items'])
            
            # 集計値の再計算
            normalized_data.update(self._recalculate_totals(normalized_data))
            
            # バリデーション
            validation_results = self._validate_data(normalized_data)
            normalized_data['warnings'].extend(validation_results.get('warnings', []))
            normalized_data['errors'].extend(validation_results.get('errors', []))
            
            return normalized_data
            
        except Exception as e:
            return {
                **raw_data,
                'errors': raw_data.get('errors', []) + [f"Normalization error: {str(e)}"]
            }
    
    def _normalize_items(self, items: List[Dict]) -> List[Dict]:
        """
        アイテムリストを正規化
        """
        normalized_items = []
        
        for item in items:
            normalized_item = item.copy()
            
            # 勘定科目の正規化
            account_name = item.get('account_name', '')
            normalized_item['account_name'] = self._normalize_account_name(account_name)
            
            # 税率の正規化
            tax_rate = item.get('tax_rate', '')
            normalized_item['tax_rate'] = self._normalize_tax_rate(tax_rate)
            
            # 課税金額の再計算
            amount = item.get('amount', 0)
            normalized_tax_rate = normalized_item['tax_rate']
            normalized_item['taxable_amount'] = amount if self._is_taxable_rate(normalized_tax_rate) else 0
            
            normalized_items.append(normalized_item)
        
        return normalized_items
    
    def _normalize_account_name(self, account_name: str) -> str:
        """
        勘定科目名を正規化
        """
        if not account_name:
            return ""
        
        # 前後の空白除去
        account_name = account_name.strip()
        
        # マッピングテーブルから検索
        for key, value in self.account_mapping.items():
            if key in account_name:
                return value
        
        return account_name
    
    def _normalize_tax_rate(self, tax_rate: str) -> str:
        """
        税率を正規化
        """
        if not tax_rate:
            return "不明"
        
        # マッピングテーブルから検索
        normalized = self.tax_rate_mapping.get(tax_rate, tax_rate)
        return normalized
    
    def _is_taxable_rate(self, tax_rate: str) -> bool:
        """
        課税対象の税率かどうかを判定
        """
        taxable_rates = ['10%', '軽減8%']
        return tax_rate in taxable_rates
    
    def _recalculate_totals(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        集計値を再計算
        """
        totals = {}
        
        # 売上合計
        sales_items = data.get('sales_items', [])
        totals['taxable_sales_total'] = sum(
            item.get('taxable_amount', 0) for item in sales_items
        )
        totals['total_sales'] = sum(
            item.get('amount', 0) for item in sales_items
        )
        
        # 仕入合計
        purchase_items = data.get('purchase_items', [])
        totals['taxable_purchases_total'] = sum(
            item.get('taxable_amount', 0) for item in purchase_items
        )
        totals['total_purchases'] = sum(
            item.get('amount', 0) for item in purchase_items
        )
        
        # 税率別集計
        totals.update(self._calculate_by_tax_rate(sales_items, purchase_items))
        
        return totals
    
    def _calculate_by_tax_rate(self, sales_items: List[Dict], purchase_items: List[Dict]) -> Dict[str, Any]:
        """
        税率別の集計を計算
        """
        by_tax_rate = {
            'sales_by_tax_rate': {},
            'purchases_by_tax_rate': {}
        }
        
        # 売上の税率別集計
        for item in sales_items:
            tax_rate = item.get('tax_rate', '不明')
            amount = item.get('amount', 0)
            
            if tax_rate not in by_tax_rate['sales_by_tax_rate']:
                by_tax_rate['sales_by_tax_rate'][tax_rate] = 0
            by_tax_rate['sales_by_tax_rate'][tax_rate] += amount
        
        # 仕入の税率別集計
        for item in purchase_items:
            tax_rate = item.get('tax_rate', '不明')
            amount = item.get('amount', 0)
            
            if tax_rate not in by_tax_rate['purchases_by_tax_rate']:
                by_tax_rate['purchases_by_tax_rate'][tax_rate] = 0
            by_tax_rate['purchases_by_tax_rate'][tax_rate] += amount
        
        return by_tax_rate
    
    def _validate_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        データのバリデーション
        """
        warnings = []
        errors = []
        
        # 基本的なデータ存在チェック
        sales_items = data.get('sales_items', [])
        purchase_items = data.get('purchase_items', [])
        
        if not sales_items and not purchase_items:
            errors.append("売上データと仕入データの両方が空です")
        
        # 金額の妥当性チェック
        for item in sales_items + purchase_items:
            amount = item.get('amount', 0)
            if amount < 0:
                warnings.append(f"負の金額が検出されました: {item.get('account_name', '不明')} {amount}")
            
            if amount > 1000000000:  # 10億円
                warnings.append(f"非常に大きな金額が検出されました: {item.get('account_name', '不明')} {amount}")
        
        # 税率の妥当性チェック
        for item in sales_items + purchase_items:
            tax_rate = item.get('tax_rate', '')
            if tax_rate == '不明':
                warnings.append(f"税率が不明です: {item.get('account_name', '不明')}")
        
        return {'warnings': warnings, 'errors': errors}