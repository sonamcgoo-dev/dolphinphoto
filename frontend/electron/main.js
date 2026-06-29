const { app, BrowserWindow, ipcMain, Menu, Tray, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow = null;
let tray = null;
let backendProcess = null;

const isDev = !app.isPackaged;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    backgroundColor: '#0a0a0f',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    titleBarStyle: 'hiddenInset',
    titleBarOverlay: {
      color: '#12121a',
      symbolColor: '#00d4ff',
      height: 40,
    },
    show: false,
  });

  // Load the app
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Create application menu
  const menuTemplate = [
    {
      label: 'DolphinPhoto',
      submenu: [
        { label: 'About', click: () => showAbout() },
        { type: 'separator' },
        { label: 'Preferences', accelerator: 'CmdOrCtrl+,', click: () => mainWindow?.webContents.send('open-settings') },
        { type: 'separator' },
        { role: 'quit' },
      ],
    },
    {
      label: 'File',
      submenu: [
        { label: 'Open Image', accelerator: 'CmdOrCtrl+O', click: () => openFile('image') },
        { label: 'Open Video', accelerator: 'CmdOrCtrl+Shift+O', click: () => openFile('video') },
        { type: 'separator' },
        { label: 'Export', accelerator: 'CmdOrCtrl+E', click: () => mainWindow?.webContents.send('export') },
        { type: 'separator' },
        { role: 'close' },
      ],
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'delete' },
        { type: 'separator' },
        { role: 'selectAll' },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },
    {
      label: 'Tools',
      submenu: [
        { label: 'AI Studio', accelerator: 'CmdOrCtrl+1', click: () => mainWindow?.webContents.send('navigate', '/studio') },
        { label: 'Dream Video', accelerator: 'CmdOrCtrl+2', click: () => mainWindow?.webContents.send('navigate', '/dream-video') },
        { label: 'Glowup', accelerator: 'CmdOrCtrl+3', click: () => mainWindow?.webContents.send('navigate', '/glowup') },
        { label: 'Filters', accelerator: 'CmdOrCtrl+4', click: () => mainWindow?.webContents.send('navigate', '/filters') },
        { type: 'separator' },
        { label: 'Models', accelerator: 'CmdOrCtrl+M', click: () => mainWindow?.webContents.send('navigate', '/models') },
        { label: 'MCP Hub', accelerator: 'CmdOrCtrl+Shift+M', click: () => mainWindow?.webContents.send('navigate', '/mcp') },
      ],
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'zoom' },
        { type: 'separator' },
        { role: 'front' },
      ],
    },
    {
      label: 'Help',
      submenu: [
        { label: 'Documentation', click: () => shell.openExternal('https://dolphinphoto.ai/docs') },
        { label: 'Report Issue', click: () => shell.openExternal('https://github.com/dolphinphoto/issues') },
        { type: 'separator' },
        { label: 'About', click: () => showAbout() },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);
}

async function openFile(type) {
  const filters = type === 'image' 
    ? [{ name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'webp', 'gif'] }]
    : [{ name: 'Videos', extensions: ['mp4', 'webm', 'mov', 'avi'] }];

  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters,
  });

  if (!result.canceled && result.filePaths.length > 0) {
    mainWindow?.webContents.send('file-opened', { path: result.filePaths[0], type });
  }
}

function showAbout() {
  dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: 'About DolphinPhoto AI Studio',
    message: 'DolphinPhoto AI Studio',
    detail: 'Version 1.0.0\n\nThe Ultimate AI Creative Studio\n\nBuilt by Black Tiger Computing\nLead Developer: Sona McGoo',
  });
}

function createTray() {
  // Note: In production, you'd use an actual tray icon
  // tray = new Tray(path.join(__dirname, 'icon.png'));
  
  tray = new (require('electron').Tray)(path.join(__dirname, '../public/icon.png').replace('app.asar', 'app.asar.unpacked'));
  
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show DolphinPhoto', click: () => mainWindow?.show() },
    { type: 'separator' },
    { label: 'AI Studio', click: () => { mainWindow?.show(); mainWindow?.webContents.send('navigate', '/studio'); } },
    { label: 'Dream Video', click: () => { mainWindow?.show(); mainWindow?.webContents.send('navigate', '/dream-video'); } },
    { label: 'Glowup', click: () => { mainWindow?.show(); mainWindow?.webContents.send('navigate', '/glowup'); } },
    { type: 'separator' },
    { label: 'Quit', click: () => app.quit() },
  ]);

  tray.setToolTip('DolphinPhoto AI Studio');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    mainWindow?.show();
  });
}

// Start backend server
function startBackend() {
  const backendPath = path.join(__dirname, '../backend/main.py');
  backendProcess = spawn('python', [backendPath], {
    stdio: 'pipe',
    shell: true,
  });

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
  });
}

// IPC Handlers
ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
  });
  return result.canceled ? null : result.filePaths[0];
});

ipcMain.handle('show-save-dialog', async (event, options) => {
  return dialog.showSaveDialog(mainWindow, options);
});

ipcMain.handle('get-app-path', () => {
  return app.getPath('userData');
});

// App lifecycle
app.whenReady().then(() => {
  // startBackend(); // Uncomment to auto-start backend
  createWindow();

  if (!isDev) {
    createTray();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (backendProcess) {
      backendProcess.kill();
    }
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});
