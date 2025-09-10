#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
税区分表変換ツール - スタンドアロンGUIアプリ
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from pathlib import Path

# バックエンドモジュールをインポート
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.parsers.factory import ParserFactory
from backend.normalizer import TaxDataNormalizer
from backend.csv_generator import CSVGenerator

class TaxConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("税区分表変換ツール v1.0")
        self.root.geometry("800x600")
        
        # 変数
        self.selected_file = tk.StringVar()
        self.processed_data = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIのセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="税区分表変換ツール", 
                               font=("", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # ファイル選択セクション
        file_frame = ttk.LabelFrame(main_frame, text="ファイル選択", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(file_frame, text="対応形式: freee (PDF), マネーフォワード (PDF/Excel), 弥生 (PDF)").grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Label(file_frame, text="選択ファイル:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(file_frame, textvariable=self.selected_file, 
                 foreground="blue").grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        ttk.Button(file_frame, text="ファイルを選択", 
                  command=self.select_file).grid(row=2, column=0, pady=(10, 0))
        ttk.Button(file_frame, text="解析実行", 
                  command=self.process_file).grid(row=2, column=1, padx=(10, 0), pady=(10, 0))
        
        # 結果表示セクション
        result_frame = ttk.LabelFrame(main_frame, text="解析結果", padding="10")
        result_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=20, width=80)
        self.result_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # CSV出力セクション
        output_frame = ttk.LabelFrame(main_frame, text="CSV出力", padding="10")
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(output_frame, text="CSVファイル保存", 
                  command=self.save_csv).grid(row=0, column=0)
        
        # グリッド設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        file_frame.columnconfigure(1, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
    
    def select_file(self):
        """ファイル選択"""
        file_path = filedialog.askopenfilename(
            title="税区分表ファイルを選択",
            filetypes=[
                ("サポートファイル", "*.pdf *.xlsx *.xls"),
                ("PDFファイル", "*.pdf"),
                ("Excelファイル", "*.xlsx *.xls"),
                ("全てのファイル", "*.*")
            ]
        )
        
        if file_path:
            self.selected_file.set(file_path)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"ファイルが選択されました: {os.path.basename(file_path)}\n\n")
    
    def process_file(self):
        """ファイル処理を別スレッドで実行"""
        if not self.selected_file.get():
            messagebox.showwarning("警告", "ファイルを選択してください")
            return
        
        # 処理をバックグラウンドで実行
        threading.Thread(target=self._process_file_thread, daemon=True).start()
    
    def _process_file_thread(self):
        """ファイル処理の実際の処理"""
        try:
            file_path = self.selected_file.get()
            
            # UI更新（メインスレッドから）
            self.root.after(0, lambda: self.result_text.insert(tk.END, "解析を開始しています...\n"))
            
            # パーサー選択
            parser = ParserFactory.get_parser(file_path)
            if not parser:
                self.root.after(0, lambda: messagebox.showerror("エラー", 
                    "サポートされていないファイル形式です。freee、マネーフォワード、弥生の税区分表を選択してください。"))
                return
            
            self.root.after(0, lambda: self.result_text.insert(tk.END, 
                f"検出システム: {parser.__class__.__name__.replace('Parser', '')}\n"))
            
            # データ解析
            self.root.after(0, lambda: self.result_text.insert(tk.END, "データを解析中...\n"))
            raw_data = parser.parse(file_path)
            
            # データ正規化
            normalizer = TaxDataNormalizer()
            self.processed_data = normalizer.normalize(raw_data)
            
            # 結果表示
            self.root.after(0, self.display_results)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{str(e)}"))
    
    def display_results(self):
        """解析結果を表示"""
        if not self.processed_data:
            return
        
        self.result_text.insert(tk.END, "\n" + "="*50 + "\n")
        self.result_text.insert(tk.END, "解析結果\n")
        self.result_text.insert(tk.END, "="*50 + "\n\n")
        
        # 売上データ
        sales_items = self.processed_data.get('sales_items', [])
        if sales_items:
            self.result_text.insert(tk.END, "【売上データ】\n")
            for item in sales_items:
                account = item.get('account_name', '不明')
                tax_rate = item.get('tax_rate', '不明')
                amount = item.get('amount', 0)
                self.result_text.insert(tk.END, f"  {account}: ¥{amount:,} ({tax_rate})\n")
            
            taxable_total = self.processed_data.get('taxable_sales_total', 0)
            self.result_text.insert(tk.END, f"\n課税売上合計: ¥{taxable_total:,}\n\n")
        
        # 警告・エラー
        warnings = self.processed_data.get('warnings', [])
        errors = self.processed_data.get('errors', [])
        
        if warnings:
            self.result_text.insert(tk.END, "【警告】\n")
            for warning in warnings:
                self.result_text.insert(tk.END, f"  ⚠️ {warning}\n")
            self.result_text.insert(tk.END, "\n")
        
        if errors:
            self.result_text.insert(tk.END, "【エラー】\n")
            for error in errors:
                self.result_text.insert(tk.END, f"  ❌ {error}\n")
            self.result_text.insert(tk.END, "\n")
        
        self.result_text.insert(tk.END, "解析完了！CSVファイル保存ボタンからファイルを出力できます。\n")
        self.result_text.see(tk.END)
    
    def save_csv(self):
        """CSV保存"""
        if not self.processed_data:
            messagebox.showwarning("警告", "まずファイルを解析してください")
            return
        
        try:
            # 保存先選択
            file_path = filedialog.asksaveasfilename(
                title="CSVファイル保存",
                defaultextension=".zip",
                filetypes=[("ZIPファイル", "*.zip"), ("全てのファイル", "*.*")]
            )
            
            if file_path:
                # CSV生成
                csv_generator = CSVGenerator()
                zip_content = csv_generator.generate_zip(self.processed_data)
                
                # ファイル保存
                with open(file_path, 'wb') as f:
                    f.write(zip_content)
                
                messagebox.showinfo("成功", f"CSVファイルが保存されました:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("エラー", f"CSV保存中にエラーが発生しました:\n{str(e)}")

def main():
    """メイン関数"""
    root = tk.Tk()
    app = TaxConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()