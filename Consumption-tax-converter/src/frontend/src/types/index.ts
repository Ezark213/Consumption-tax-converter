export interface ProcessingStep {
  name: string;
  status: 'pending' | 'current' | 'completed' | 'error';
  progress?: number;
}

export interface PreviewData {
  session_id: string;
  filename: string;
  parser_type: string;
  taxable_sales: number;
  taxable_purchases: number;
  warnings: string[];
  errors: string[];
  sales_items_count: number;
  purchase_items_count: number;
}

export interface TaxItem {
  account_name: string;
  tax_rate: string;
  amount: number;
  taxable_amount: number;
}