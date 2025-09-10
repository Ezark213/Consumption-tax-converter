import { FC, useState } from 'react'
import { Download, FileArchive, Loader2 } from 'lucide-react'
import axios from 'axios'

interface DownloadSectionProps {
  sessionId: string;
  onDownloadReady: () => void;
}

const DownloadSection: FC<DownloadSectionProps> = ({ sessionId, onDownloadReady }) => {
  const [downloading, setDownloading] = useState(false)
  const [downloadError, setDownloadError] = useState<string>('')

  const handleDownload = async () => {
    setDownloading(true)
    setDownloadError('')

    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/download/${sessionId}`, {
        responseType: 'blob',
      })

      // ファイルをダウンロード
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      
      // ファイル名を設定（Content-Dispositionヘッダーから取得するか、デフォルト名を使用）
      const disposition = response.headers['content-disposition']
      let filename = 'tax_data.zip'
      if (disposition) {
        const filenameMatch = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '')
        }
      }
      
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      onDownloadReady()

    } catch (error) {
      console.error('Download error:', error)
      if (axios.isAxiosError(error) && error.response) {
        setDownloadError(error.response.data?.detail || 'ダウンロードに失敗しました')
      } else {
        setDownloadError('ネットワークエラーが発生しました')
      }
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center mb-3">
          <FileArchive className="h-5 w-5 text-gray-600 mr-2" />
          <h3 className="font-medium text-gray-900">生成されるファイル</h3>
        </div>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• 課税売上.csv - 売上データの税率別集計</li>
          <li>• 課税仕入.csv - 仕入データの税率別集計</li>
          <li>• 集計サマリー.csv - 全体の集計情報</li>
          <li>• 処理情報.txt - 変換処理の詳細情報</li>
        </ul>
      </div>

      <button
        onClick={handleDownload}
        disabled={downloading}
        className={`
          w-full flex items-center justify-center px-4 py-3 border border-transparent 
          text-sm font-medium rounded-md text-white transition-colors
          ${downloading 
            ? 'bg-gray-400 cursor-not-allowed' 
            : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
          }
        `}
      >
        {downloading ? (
          <Loader2 className="h-5 w-5 mr-2 animate-spin" />
        ) : (
          <Download className="h-5 w-5 mr-2" />
        )}
        {downloading ? 'ダウンロード中...' : 'CSVファイルをダウンロード'}
      </button>

      {downloadError && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-800">{downloadError}</p>
        </div>
      )}

      <div className="text-xs text-gray-500 text-center">
        ZIPファイルとしてダウンロードされます
      </div>
    </div>
  )
}

export default DownloadSection