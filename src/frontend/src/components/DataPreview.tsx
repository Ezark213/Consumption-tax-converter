import { FC } from 'react'
import { TrendingUp, TrendingDown, FileText, AlertTriangle, CheckCircle } from 'lucide-react'
import { PreviewData } from '../types'

interface DataPreviewProps {
  data: PreviewData;
}

const DataPreview: FC<DataPreviewProps> = ({ data }) => {
  const formatCurrency = (amount: number) => {
    return `¥${amount.toLocaleString()}`
  }

  const getParserDisplayName = (parserType: string) => {
    switch (parserType) {
      case 'freee':
        return 'freee会計'
      case 'moneyforward':
        return 'マネーフォワード'
      case 'yayoi':
        return '弥生会計'
      default:
        return parserType
    }
  }

  return (
    <div className="space-y-6">
      {/* ファイル情報 */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-medium text-gray-900 mb-2">ファイル情報</h3>
        <div className="space-y-1 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">ファイル名:</span>
            <span className="font-medium">{data.filename}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">解析システム:</span>
            <span className="font-medium">{getParserDisplayName(data.parser_type)}</span>
          </div>
        </div>
      </div>

      {/* 金額サマリー */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-800">課税売上合計</p>
              <p className="text-2xl font-bold text-green-900">
                {formatCurrency(data.taxable_sales)}
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-600" />
          </div>
          <p className="text-xs text-green-700 mt-1">
            {data.sales_items_count}件の売上項目
          </p>
        </div>

        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-800">課税仕入合計</p>
              <p className="text-2xl font-bold text-blue-900">
                {formatCurrency(data.taxable_purchases)}
              </p>
            </div>
            <TrendingDown className="h-8 w-8 text-blue-600" />
          </div>
          <p className="text-xs text-blue-700 mt-1">
            {data.purchase_items_count}件の仕入項目
          </p>
        </div>
      </div>

      {/* 処理結果 */}
      <div>
        <h3 className="font-medium text-gray-900 mb-3 flex items-center">
          <FileText className="h-5 w-5 mr-2" />
          処理結果
        </h3>
        
        <div className="space-y-3">
          {data.errors.length === 0 && data.warnings.length === 0 ? (
            <div className="flex items-center p-3 bg-green-50 border border-green-200 rounded-md">
              <CheckCircle className="h-5 w-5 text-green-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-green-800">
                  処理が正常に完了しました
                </p>
                <p className="text-xs text-green-700">
                  データの変換とバリデーションが成功しました<br/>
                  文字化け対策: Shift_JIS + UTF-8 両形式で出力
                </p>
              </div>
            </div>
          ) : (
            <>
              {data.errors.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3">
                  <div className="flex items-start">
                    <AlertTriangle className="h-5 w-5 text-red-400 mt-0.5 mr-3" />
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-red-800 mb-1">
                        エラー ({data.errors.length}件)
                      </h4>
                      <ul className="text-xs text-red-700 space-y-1">
                        {data.errors.map((error, index) => (
                          <li key={index}>• {error}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {data.warnings.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                  <div className="flex items-start">
                    <AlertTriangle className="h-5 w-5 text-yellow-400 mt-0.5 mr-3" />
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-yellow-800 mb-1">
                        警告 ({data.warnings.length}件)
                      </h4>
                      <ul className="text-xs text-yellow-700 space-y-1">
                        {data.warnings.map((warning, index) => (
                          <li key={index}>• {warning}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default DataPreview