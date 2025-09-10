import { FC, useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, AlertCircle, CheckCircle } from 'lucide-react'
import axios from 'axios'
import { PreviewData, ProcessingStep } from '../types'

interface FileUploadProps {
  onFileProcessed: (data: PreviewData) => void;
  onStepUpdate: (stepIndex: number, status: ProcessingStep['status'], progress?: number) => void;
}

const FileUpload: FC<FileUploadProps> = ({ onFileProcessed, onStepUpdate }) => {
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState<string>('')

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setUploading(true)
    setUploadStatus('idle')
    setErrorMessage('')

    try {
      // ステップ1: ファイル選択完了
      onStepUpdate(0, 'completed')
      onStepUpdate(1, 'current', 0)

      const formData = new FormData()
      formData.append('file', file)

      // プログレス表示の更新
      onStepUpdate(1, 'current', 30)

      const response = await axios.post('http://127.0.0.1:8000/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            onStepUpdate(1, 'current', Math.min(percentCompleted, 90))
          }
        },
      })

      // ステップ2: データ解析完了
      onStepUpdate(1, 'completed')
      onStepUpdate(2, 'current', 50)

      // データ正規化の処理
      await new Promise(resolve => setTimeout(resolve, 1000)) // 視覚的な効果のための待機
      onStepUpdate(2, 'current', 100)

      setUploadStatus('success')
      onFileProcessed(response.data)

    } catch (error) {
      console.error('Upload error:', error)
      setUploadStatus('error')
      
      if (axios.isAxiosError(error) && error.response) {
        setErrorMessage(error.response.data.detail || 'アップロードに失敗しました')
      } else {
        setErrorMessage('ネットワークエラーが発生しました')
      }
      
      onStepUpdate(1, 'error')
    } finally {
      setUploading(false)
    }
  }, [onFileProcessed, onStepUpdate])

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: false,
    disabled: uploading
  })

  const getRejectionMessage = () => {
    if (fileRejections.length > 0) {
      const rejection = fileRejections[0]
      if (rejection.errors.some(e => e.code === 'file-too-large')) {
        return 'ファイルサイズが50MBを超えています'
      }
      if (rejection.errors.some(e => e.code === 'file-invalid-type')) {
        return 'サポートされていないファイル形式です（PDF, Excel のみ）'
      }
      return 'ファイルが無効です'
    }
    return null
  }

  const rejectionMessage = getRejectionMessage()

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-blue-400 bg-blue-50' 
            : uploading 
              ? 'border-gray-300 bg-gray-50 cursor-not-allowed' 
              : uploadStatus === 'success'
                ? 'border-green-400 bg-green-50'
                : uploadStatus === 'error'
                  ? 'border-red-400 bg-red-50'
                  : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
          }
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          {uploading ? (
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          ) : uploadStatus === 'success' ? (
            <CheckCircle className="h-12 w-12 text-green-600" />
          ) : uploadStatus === 'error' ? (
            <AlertCircle className="h-12 w-12 text-red-600" />
          ) : (
            <Upload className="h-12 w-12 text-gray-400" />
          )}
          
          <div>
            {uploading ? (
              <p className="text-lg font-medium text-gray-600">
                ファイルを処理中...
              </p>
            ) : uploadStatus === 'success' ? (
              <p className="text-lg font-medium text-green-600">
                アップロード完了！
              </p>
            ) : uploadStatus === 'error' ? (
              <p className="text-lg font-medium text-red-600">
                エラーが発生しました
              </p>
            ) : isDragActive ? (
              <p className="text-lg font-medium text-blue-600">
                ファイルをドロップしてください
              </p>
            ) : (
              <div>
                <p className="text-lg font-medium text-gray-700">
                  ファイルをドラッグ&ドロップ
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  またはクリックして選択
                </p>
              </div>
            )}
            
            {!uploading && uploadStatus === 'idle' && (
              <p className="text-xs text-gray-400 mt-2">
                PDF, Excel (xlsx, xls) - 最大50MB
              </p>
            )}
          </div>
        </div>
      </div>

      {rejectionMessage && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <p className="text-sm text-red-800">{rejectionMessage}</p>
            </div>
          </div>
        </div>
      )}

      {errorMessage && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <p className="text-sm text-red-800">{errorMessage}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default FileUpload