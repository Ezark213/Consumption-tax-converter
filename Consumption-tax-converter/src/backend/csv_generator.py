import pandas as pd
import io
import zipfile
from typing import Dict, List, Any

class CSVGenerator:
    """
    正規化されたデータからCSVファイルを生成するクラス
    """
    
    def __init__(self):
        # 出力用のカラム定義
        self.sales_columns = [
            '勘定科目',
            '軽減8%',
            '10%',
            '輸出売上',
            '非課税',
            '不課税'
        ]
        
        self.purchase_columns = [
            '勘定科目',
            '軽減8%_経過',
            '軽減8%_適格',
            '10%_経過',
            '10%_適格',
            '非課税',
            '不課税'
        ]
    
    def generate_zip(self, data: Dict[str, Any]) -> bytes:
        """
        ZIPファイル形式でCSVを生成
        
        Args:
            data: 正規化されたデータ
            
        Returns:
            bytes: ZIPファイルのバイナリデータ
        """
        # メモリ上でZIPファイルを作成
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 課税売上CSVを追加（Shift_JIS版とUTF-8版の両方）
            sales_csv_sjis = self._generate_sales_csv(data, encoding='shift_jis')
            sales_csv_utf8 = self._generate_sales_csv(data, encoding='utf-8-sig')
            zip_file.writestr('課税売上_SJIS.csv', sales_csv_sjis)
            zip_file.writestr('課税売上_UTF8.csv', sales_csv_utf8)
            
            # 課税仕入CSVを追加（Shift_JIS版とUTF-8版の両方）
            purchases_csv_sjis = self._generate_purchases_csv(data, encoding='shift_jis')
            purchases_csv_utf8 = self._generate_purchases_csv(data, encoding='utf-8-sig')
            zip_file.writestr('課税仕入_SJIS.csv', purchases_csv_sjis)
            zip_file.writestr('課税仕入_UTF8.csv', purchases_csv_utf8)
            
            # サマリーCSVを追加（Shift_JIS版とUTF-8版の両方）
            summary_csv_sjis = self._generate_summary_csv(data, encoding='shift_jis')
            summary_csv_utf8 = self._generate_summary_csv(data, encoding='utf-8-sig')
            zip_file.writestr('集計サマリー_SJIS.csv', summary_csv_sjis)
            zip_file.writestr('集計サマリー_UTF8.csv', summary_csv_utf8)
            
            # メタデータファイルを追加（UTF-8で保存）
            metadata_txt = self._generate_metadata_txt(data)
            zip_file.writestr('処理情報.txt', metadata_txt.encode('utf-8'))
            
            # 使用説明書を追加
            readme_content = self._generate_readme_txt()
            zip_file.writestr('ファイル説明.txt', readme_content.encode('utf-8'))
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def _generate_sales_csv(self, data: Dict[str, Any], encoding: str = 'utf-8-sig') -> bytes:
        """
        課税売上のCSVを生成
        
        Args:
            data: 正規化されたデータ
            encoding: 文字エンコーディング ('utf-8-sig', 'shift_jis')
        
        Returns:
            bytes: CSVファイルのバイナリデータ
        """
        sales_items = data.get('sales_items', [])
        
        # 勘定科目ごとに税率別の金額を集計
        account_summary = {}
        
        for item in sales_items:
            account_name = item.get('account_name', '不明')
            tax_rate = item.get('tax_rate', '不明')
            amount = item.get('amount', 0)
            
            if account_name not in account_summary:
                account_summary[account_name] = {
                    '軽減8%': 0,
                    '10%': 0,
                    '輸出売上': 0,
                    '非課税': 0,
                    '不課税': 0
                }
            
            # 税率に応じて適切な列に金額を加算
            if tax_rate == '軽減8%' or tax_rate == '課対仕入8%（軽）':
                account_summary[account_name]['軽減8%'] += amount
            elif tax_rate == '10%' or tax_rate == '課税売上10%':
                account_summary[account_name]['10%'] += amount
            elif tax_rate == '輸出売上' or tax_rate == '輸出売上0%':
                account_summary[account_name]['輸出売上'] += amount
            elif tax_rate == '非課税' or tax_rate == '非課売上':
                account_summary[account_name]['非課税'] += amount
            else:
                account_summary[account_name]['不課税'] += amount
        
        # DataFrameを作成（データがない場合も空のDataFrameを作成）
        if not account_summary:
            df = pd.DataFrame(columns=self.sales_columns)
        else:
            rows = []
            for account_name, amounts in account_summary.items():
                row = {'勘定科目': account_name}
                row.update(amounts)
                rows.append(row)
            
            df = pd.DataFrame(rows, columns=self.sales_columns)
            
            # 金額でソート（降順）
            df['total'] = df[['軽減8%', '10%', '輸出売上', '非課税', '不課税']].sum(axis=1)
            df = df.sort_values('total', ascending=False).drop('total', axis=1)
        
        # エンコーディングに応じたCSV生成
        try:
            if encoding == 'shift_jis':
                # Shift_JISで出力（日本のExcel標準）
                csv_content = df.to_csv(index=False, lineterminator='\r\n', quoting=1)
                return csv_content.encode('shift_jis', errors='replace')
            else:
                # UTF-8 with BOM（BOM付きUTF-8）
                csv_content = df.to_csv(index=False, lineterminator='\r\n', quoting=1)
                return csv_content.encode('utf-8-sig')
        except UnicodeEncodeError:
            # Shift_JISでエンコードできない文字がある場合はUTF-8にフォールバック
            csv_content = df.to_csv(index=False, lineterminator='\r\n', quoting=1)
            return csv_content.encode('utf-8-sig')
    
    def _generate_purchases_csv(self, data: Dict[str, Any], encoding: str = 'utf-8-sig') -> bytes:
        """
        課税仕入のCSVを生成
        
        Args:
            data: 正規化されたデータ
            encoding: 文字エンコーディング ('utf-8-sig', 'shift_jis')
        
        Returns:
            bytes: CSVファイルのバイナリデータ
        """
        purchase_items = data.get('purchase_items', [])
        
        # 勘定科目ごとに税率別の金額を集計
        account_summary = {}
        
        for item in purchase_items:
            account_name = item.get('account_name', '不明')
            tax_rate = item.get('tax_rate', '不明')
            amount = item.get('amount', 0)
            
            if account_name not in account_summary:
                account_summary[account_name] = {
                    '軽減8%_経過': 0,
                    '軽減8%_適格': 0,
                    '10%_経過': 0,
                    '10%_適格': 0,
                    '非課税': 0,
                    '不課税': 0
                }
            
            # 税率に応じて適切な列に金額を加算
            # 注: 経過措置・適格請求書の区別は実際のデータ構造に応じて調整が必要
            if tax_rate == '軽減8%':
                account_summary[account_name]['軽減8%_適格'] += amount
            elif tax_rate == '10%':
                account_summary[account_name]['10%_適格'] += amount
            elif tax_rate == '非課税':
                account_summary[account_name]['非課税'] += amount
            else:
                account_summary[account_name]['不課税'] += amount
        
        # DataFrameを作成
        rows = []
        for account_name, amounts in account_summary.items():
            row = {'勘定科目': account_name}
            row.update(amounts)
            rows.append(row)
        
        df = pd.DataFrame(rows, columns=self.purchase_columns)
        
        # 金額でソート（降順）
        df['total'] = df[['軽減8%_経過', '軽減8%_適格', '10%_経過', '10%_適格', '非課税', '不課税']].sum(axis=1)
        df = df.sort_values('total', ascending=False).drop('total', axis=1)
        
        # エンコーディングに応じたCSV生成
        try:
            if encoding == 'shift_jis':
                # Shift_JISで出力（日本のExcel標準）
                csv_content = df.to_csv(index=False, lineterminator='\r\n', quoting=1)
                return csv_content.encode('shift_jis', errors='replace')
            else:
                # UTF-8 with BOM（BOM付きUTF-8）
                csv_content = df.to_csv(index=False, lineterminator='\r\n', quoting=1)
                return csv_content.encode('utf-8-sig')
        except UnicodeEncodeError:
            # Shift_JISでエンコードできない文字がある場合はUTF-8にフォールバック
            csv_content = df.to_csv(index=False, lineterminator='\r\n', quoting=1)
            return csv_content.encode('utf-8-sig')
    
    def _generate_summary_csv(self, data: Dict[str, Any], encoding: str = 'utf-8-sig') -> bytes:
        """
        集計サマリーのCSVを生成
        
        Args:
            data: 正規化されたデータ
            encoding: 文字エンコーディング ('utf-8-sig', 'shift_jis')
        
        Returns:
            bytes: CSVファイルのバイナリデータ
        """
        summary_data = [
            {
                '項目': '課税売上合計',
                '金額': data.get('taxable_sales_total', 0),
                '内容': '10%および軽減8%の売上合計'
            },
            {
                '項目': '課税仕入合計',
                '金額': data.get('taxable_purchases_total', 0),
                '内容': '10%および軽減8%の仕入合計'
            },
            {
                '項目': '総売上',
                '金額': data.get('total_sales', 0),
                '内容': '全税率の売上合計'
            },
            {
                '項目': '総仕入',
                '金額': data.get('total_purchases', 0),
                '内容': '全税率の仕入合計'
            }
        ]
        
        # 税率別サマリーを追加
        sales_by_tax = data.get('sales_by_tax_rate', {})
        for tax_rate, amount in sales_by_tax.items():
            summary_data.append({
                '項目': f'売上_{tax_rate}',
                '金額': amount,
                '内容': f'{tax_rate}の売上'
            })
        
        purchases_by_tax = data.get('purchases_by_tax_rate', {})
        for tax_rate, amount in purchases_by_tax.items():
            summary_data.append({
                '項目': f'仕入_{tax_rate}',
                '金額': amount,
                '内容': f'{tax_rate}の仕入'
            })
        
        df = pd.DataFrame(summary_data)
        # エンコーディングに応じたCSV生成
        try:
            if encoding == 'shift_jis':
                # Shift_JISで出力（日本のExcel標準）
                csv_content = df.to_csv(index=False, lineterminator='\r\n', quoting=1)
                return csv_content.encode('shift_jis', errors='replace')
            else:
                # UTF-8 with BOM（BOM付きUTF-8）
                csv_content = df.to_csv(index=False, lineterminator='\r\n', quoting=1)
                return csv_content.encode('utf-8-sig')
        except UnicodeEncodeError:
            # Shift_JISでエンコードできない文字がある場合はUTF-8にフォールバック
            csv_content = df.to_csv(index=False, lineterminator='\r\n', quoting=1)
            return csv_content.encode('utf-8-sig')
    
    def _generate_metadata_txt(self, data: Dict[str, Any]) -> str:
        """
        処理情報のテキストファイルを生成
        """
        lines = [
            "# 税区分表変換処理情報",
            "",
            f"解析システム: {data.get('parser_type', '不明')}",
            f"処理日時: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 処理結果",
            f"売上項目数: {len(data.get('sales_items', []))}件",
            f"仕入項目数: {len(data.get('purchase_items', []))}件",
            f"課税売上合計: ¥{data.get('taxable_sales_total', 0):,}",
            f"課税仕入合計: ¥{data.get('taxable_purchases_total', 0):,}",
            ""
        ]
        
        # 警告があれば追加
        warnings = data.get('warnings', [])
        if warnings:
            lines.append("## 警告")
            for warning in warnings:
                lines.append(f"- {warning}")
            lines.append("")
        
        # エラーがあれば追加
        errors = data.get('errors', [])
        if errors:
            lines.append("## エラー")
            for error in errors:
                lines.append(f"- {error}")
            lines.append("")
        
        # メタデータがあれば追加
        if 'period_start' in data or 'period_end' in data:
            lines.append("## 期間情報")
            if 'period_start' in data and 'period_end' in data:
                lines.append(f"対象期間: {data['period_start']} ～ {data['period_end']}")
            lines.append("")
        
        if 'company_name' in data:
            lines.append("## 会社情報")
            lines.append(f"会社名: {data['company_name']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_readme_txt(self) -> str:
        """
        ファイル説明書を生成
        """
        lines = [
            "# 税区分表変換ツール - 出力ファイル説明",
            "",
            "## ファイル一覧",
            "",
            "### CSVファイル（2つの形式で提供）",
            "",
            "#### Shift_JIS版（推奨）",
            "- 課税売上_SJIS.csv",
            "- 課税仕入_SJIS.csv", 
            "- 集計サマリー_SJIS.csv",
            "",
            "**使用方法**: 日本語版Excel環境で文字化けせずに開けます",
            "**対象**: Windows Excel 2013以降（日本語環境）",
            "",
            "#### UTF-8版（互換性用）",
            "- 課税売上_UTF8.csv",
            "- 課税仕入_UTF8.csv",
            "- 集計サマリー_UTF8.csv", 
            "",
            "**使用方法**: BOM付きUTF-8形式です",
            "**対象**: 新しいExcel、Google Sheets、その他のツール",
            "",
            "## 使い分けガイド",
            "",
            "1. **日本語Windows Excel**: SJIS版をご使用ください",
            "2. **Mac Excel**: UTF8版をお試しください",
            "3. **Google Sheets**: UTF8版を推奨します",
            "4. **その他ツール**: UTF8版から試してください",
            "",
            "## 文字化けが発生した場合",
            "",
            "1. 別の形式（SJIS⇔UTF8）をお試しください",
            "2. Excel「データ」タブ→「テキストファイル」から手動でエンコーディングを指定",
            "3. テキストエディタで開いて内容を確認",
            "",
            "## その他のファイル",
            "",
            "- **処理情報.txt**: 変換処理の詳細情報",
            "- **ファイル説明.txt**: このファイル（使用方法説明）",
            "",
            "## サポート情報",
            "",
            "生成日時: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            "ツール: 税区分表変換ツール v1.0",
            ""
        ]
        
        return "\n".join(lines)