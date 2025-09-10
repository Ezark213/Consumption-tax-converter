const { contextBridge, ipcRenderer } = require('electron')

// セキュアなAPIをレンダラープロセスに公開
contextBridge.exposeInMainWorld('electronAPI', {
  // アプリケーション情報
  getAppVersion: () => ipcRenderer.invoke('app-version'),
  
  // ファイルダイアログ
  showSaveDialog: () => ipcRenderer.invoke('show-save-dialog'),
  showOpenDialog: () => ipcRenderer.invoke('show-open-dialog'),
  
  // システム情報
  platform: process.platform,
  
  // イベントリスナー
  onMenuAction: (callback) => {
    ipcRenderer.on('menu-action', callback)
    return () => ipcRenderer.removeListener('menu-action', callback)
  }
})

// セキュリティ: Node.jsのAPIへの直接アクセスを防ぐ
window.addEventListener('DOMContentLoaded', () => {
  // レンダラープロセスでNode.jsのAPIが利用できないことを確認
  console.log('Preload script loaded')
  console.log('Node integration:', process.versions.node ? 'enabled' : 'disabled')
})