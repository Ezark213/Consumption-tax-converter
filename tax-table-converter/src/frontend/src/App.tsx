import { useState } from 'react'
import FileUpload from './components/FileUpload'
import ProgressIndicator from './components/ProgressIndicator'
import DataPreview from './components/DataPreview'
import DownloadSection from './components/DownloadSection'
import { ProcessingStep, PreviewData } from './types'

function App() {
  const [steps, setSteps] = useState<ProcessingStep[]>([
    { name: 'ファイル選択', status: 'pending' },
    { name: 'データ解析', status: 'pending' },
    { name: 'データ正規化', status: 'pending' },
    { name: 'CSV生成', status: 'pending' }
  ])
  
  const [previewData, setPreviewData] = useState<PreviewData | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)

  const updateStep = (stepIndex: number, status: ProcessingStep['status'], progress?: number) => {
    setSteps(prev => prev.map((step, index) => 
      index === stepIndex ? { ...step, status, progress } : step
    ))
  }

  const handleFileProcessed = (data: PreviewData) => {
    setPreviewData(data)
    setSessionId(data.session_id)
    
    // ステップを完了状態に更新
    setSteps(prev => prev.map((step, index) => 
      index <= 2 ? { ...step, status: 'completed' } : step
    ))
  }

  const handleDownloadReady = () => {
    updateStep(3, 'completed')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            税区分表変換ツール
          </h1>
          <p className="text-gray-600">
            freee・マネーフォワード・弥生の税区分表を標準CSVに変換
          </p>
        </header>

        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">ファイルアップロード</h2>
                <FileUpload 
                  onFileProcessed={handleFileProcessed}
                  onStepUpdate={updateStep}
                />
              </div>

              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">処理状況</h2>
                <ProgressIndicator steps={steps} />
              </div>
            </div>

            <div className="space-y-6">
              {previewData && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h2 className="text-xl font-semibold mb-4">データプレビュー</h2>
                  <DataPreview data={previewData} />
                </div>
              )}

              {sessionId && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h2 className="text-xl font-semibold mb-4">ダウンロード</h2>
                  <DownloadSection 
                    sessionId={sessionId}
                    onDownloadReady={handleDownloadReady}
                  />
                </div>
              )}
            </div>
          </div>
        </div>

        <footer className="text-center mt-12 text-gray-500 text-sm">
          <p>対応形式: freee (PDF), マネーフォワード (Excel), 弥生 (PDF)</p>
        </footer>
      </div>
    </div>
  )
}

export default App