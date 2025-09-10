const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const { spawn } = require('child_process')
const path = require('path')
const isDev = process.env.NODE_ENV === 'development'

let mainWindow
let pythonProcess

function createWindow() {
  // メインウィンドウを作成
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../assets/icon.png'), // アイコンファイルがある場合
    show: false // 初期化完了まで非表示
  })

  // ウィンドウの準備が完了したら表示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
    
    // 開発環境では開発者ツールを開く
    if (isDev) {
      mainWindow.webContents.openDevTools()
    }
  })

  // アプリケーションのロード
  if (isDev) {
    // 開発時はViteのdevサーバーから読み込み
    mainWindow.loadURL('http://localhost:3000')
  } else {
    // 本番時はビルドされたファイルから読み込み
    mainWindow.loadFile(path.join(__dirname, '../frontend/dist/index.html'))
  }

  // ウィンドウが閉じられた時の処理
  mainWindow.on('closed', () => {
    mainWindow = null
  })

  // 外部リンクをデフォルトブラウザで開く
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    require('electron').shell.openExternal(url)
    return { action: 'deny' }
  })
}

function startPythonBackend() {
  if (pythonProcess) {
    return
  }

  let pythonExecutable, pythonArgs

  if (isDev) {
    // 開発環境：Pythonスクリプトを直接実行
    pythonExecutable = 'python'
    pythonArgs = [path.join(__dirname, '../backend/main.py')]
  } else {
    // 本番環境：PyInstallerでビルドされた実行ファイルを使用
    const exeName = process.platform === 'win32' ? 'tax-converter-backend.exe' : 'tax-converter-backend'
    pythonExecutable = path.join(process.resourcesPath, 'python', exeName)
    pythonArgs = []
  }

  console.log('Starting Python backend:', pythonExecutable, pythonArgs)

  try {
    pythonProcess = spawn(pythonExecutable, pythonArgs, {
      stdio: ['ignore', 'pipe', 'pipe']
    })

    pythonProcess.stdout.on('data', (data) => {
      console.log('Python stdout:', data.toString())
    })

    pythonProcess.stderr.on('data', (data) => {
      console.log('Python stderr:', data.toString())
    })

    pythonProcess.on('close', (code) => {
      console.log(`Python process exited with code ${code}`)
      pythonProcess = null
    })

    pythonProcess.on('error', (err) => {
      console.error('Failed to start Python process:', err)
      
      // Python環境のエラーを表示
      dialog.showErrorBox(
        'Python環境エラー',
        'Pythonの実行環境が見つかりません。Pythonがインストールされていることを確認してください。'
      )
    })

  } catch (error) {
    console.error('Error starting Python backend:', error)
  }
}

function stopPythonBackend() {
  if (pythonProcess) {
    pythonProcess.kill()
    pythonProcess = null
  }
}

// アプリケーションの初期化
app.whenReady().then(() => {
  startPythonBackend()
  
  // Python起動の待機時間
  setTimeout(() => {
    createWindow()
  }, 2000)

  app.on('activate', () => {
    // macOSでDockアイコンがクリックされた時
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

// すべてのウィンドウが閉じられた時
app.on('window-all-closed', () => {
  stopPythonBackend()
  
  // macOS以外では終了
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// アプリケーション終了時
app.on('before-quit', () => {
  stopPythonBackend()
})

// セキュリティ: 新しいウィンドウの作成を制限
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (navigationEvent, navigationURL) => {
    navigationEvent.preventDefault()
    require('electron').shell.openExternal(navigationURL)
  })
})

// IPC handlers
ipcMain.handle('app-version', () => {
  return app.getVersion()
})

ipcMain.handle('show-save-dialog', async () => {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: 'tax_data_converted.zip',
    filters: [
      { name: 'ZIP Files (文字化け対策済み)', extensions: ['zip'] },
      { name: 'CSV Files', extensions: ['csv'] },
      { name: 'All Files', extensions: ['*'] }
    ],
    properties: ['createDirectory']
  })
  return result
})

ipcMain.handle('show-open-dialog', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Tax Files', extensions: ['pdf', 'xlsx', 'xls'] },
      { name: 'PDF Files', extensions: ['pdf'] },
      { name: 'Excel Files', extensions: ['xlsx', 'xls'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  })
  return result
})

// 未処理のエラーをキャッチ
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error)
})

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason)
})