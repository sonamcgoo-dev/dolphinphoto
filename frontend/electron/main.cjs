const { app, BrowserWindow, ipcMain, Menu, Tray, dialog, shell } = require("electron");
const path = require("path");
const http = require("http");
const { spawn } = require("child_process");
const { pathToFileURL } = require("url");

let mainWindow = null;
let splashWindow = null;
let tray = null;
let backendProcess = null;

const isDev = !app.isPackaged;
const APP_NAME = "DolphinPhoto AI Studio";
const BACKEND_URL = "http://127.0.0.1:7777/health";

function publicAssetPath(filename) {
  return isDev
    ? path.join(__dirname, "..", "public", filename)
    : path.join(process.resourcesPath, "public", filename);
}

function backendDirPath() {
  return isDev
    ? path.join(__dirname, "..", "..", "backend")
    : path.join(process.resourcesPath, "backend");
}

function createSplashWindow() {
  const dolphinUrl = pathToFileURL(publicAssetPath("dolphin-laugh.png")).href;
  const logoUrl = pathToFileURL(publicAssetPath("dolphinphoto-logo.png")).href;

  const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>${APP_NAME}</title>
    <style>
      :root { color-scheme: dark; }
      body {
        margin: 0;
        background: radial-gradient(circle at top, #181826 0%, #090910 65%);
        font-family: Inter, Segoe UI, sans-serif;
        color: #dffcff;
        display: grid;
        place-items: center;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
      }
      .wrap { text-align: center; }
      .logo {
        width: 320px;
        max-width: 72vw;
        margin-bottom: 16px;
        filter: drop-shadow(0 0 14px rgba(0, 212, 255, 0.35));
      }
      .dolphin {
        width: 240px;
        max-width: 56vw;
        border-radius: 20px;
        animation: laugh 1s ease-in-out infinite;
        box-shadow: 0 0 30px rgba(255, 0, 170, 0.35);
      }
      .label {
        margin-top: 18px;
        font-size: 14px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #84ebff;
        animation: pulse 1.2s ease-in-out infinite;
      }
      @keyframes laugh {
        0%, 100% { transform: translateY(0px) rotate(0deg) scale(1); }
        20% { transform: translateY(-6px) rotate(-1.2deg) scale(1.02); }
        40% { transform: translateY(2px) rotate(1.4deg) scale(1.01); }
        60% { transform: translateY(-4px) rotate(-1deg) scale(1.03); }
        80% { transform: translateY(1px) rotate(1deg) scale(1.01); }
      }
      @keyframes pulse {
        0%, 100% { opacity: 0.55; }
        50% { opacity: 1; }
      }
    </style>
  </head>
  <body>
    <div class="wrap">
      <img class="logo" src="${logoUrl}" alt="DolphinPhoto" />
      <img class="dolphin" src="${dolphinUrl}" alt="Laughing dolphin loading" />
      <div class="label">Loading DolphinPhoto...</div>
    </div>
  </body>
</html>`;

  splashWindow = new BrowserWindow({
    width: 760,
    height: 540,
    frame: false,
    transparent: false,
    resizable: false,
    movable: true,
    alwaysOnTop: true,
    show: true,
    icon: publicAssetPath("icon.png"),
  });

  splashWindow.loadURL(`data:text/html;charset=UTF-8,${encodeURIComponent(html)}`);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    backgroundColor: "#0a0a0f",
    icon: publicAssetPath("icon.png"),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.cjs"),
    },
    titleBarStyle: "hiddenInset",
    titleBarOverlay: {
      color: "#12121a",
      symbolColor: "#00d4ff",
      height: 40,
    },
    show: false,
  });

  if (isDev) {
    mainWindow.loadURL("http://localhost:5173");
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, "..", "dist", "index.html"));
  }

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
    if (splashWindow && !splashWindow.isDestroyed()) {
      splashWindow.close();
      splashWindow = null;
    }
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });

  const menuTemplate = [
    {
      label: "DolphinPhoto",
      submenu: [
        { label: "About", click: () => showAbout() },
        { type: "separator" },
        {
          label: "Preferences",
          accelerator: "CmdOrCtrl+,",
          click: () => mainWindow?.webContents.send("open-settings"),
        },
        { type: "separator" },
        { role: "quit" },
      ],
    },
    {
      label: "File",
      submenu: [
        { label: "Open Image", accelerator: "CmdOrCtrl+O", click: () => openFile("image") },
        { label: "Open Video", accelerator: "CmdOrCtrl+Shift+O", click: () => openFile("video") },
        { type: "separator" },
        { label: "Export", accelerator: "CmdOrCtrl+E", click: () => mainWindow?.webContents.send("export") },
        { type: "separator" },
        { role: "close" },
      ],
    },
    {
      label: "Edit",
      submenu: [
        { role: "undo" },
        { role: "redo" },
        { type: "separator" },
        { role: "cut" },
        { role: "copy" },
        { role: "paste" },
        { role: "delete" },
        { type: "separator" },
        { role: "selectAll" },
      ],
    },
    {
      label: "View",
      submenu: [
        { role: "reload" },
        { role: "forceReload" },
        { role: "toggleDevTools" },
        { type: "separator" },
        { role: "resetZoom" },
        { role: "zoomIn" },
        { role: "zoomOut" },
        { type: "separator" },
        { role: "togglefullscreen" },
      ],
    },
    {
      label: "Tools",
      submenu: [
        { label: "AI Studio", accelerator: "CmdOrCtrl+1", click: () => mainWindow?.webContents.send("navigate", "/studio") },
        { label: "Dream Video", accelerator: "CmdOrCtrl+2", click: () => mainWindow?.webContents.send("navigate", "/dream-video") },
        { label: "Glowup", accelerator: "CmdOrCtrl+3", click: () => mainWindow?.webContents.send("navigate", "/glowup") },
        { label: "Filters", accelerator: "CmdOrCtrl+4", click: () => mainWindow?.webContents.send("navigate", "/filters") },
        { type: "separator" },
        { label: "Models", accelerator: "CmdOrCtrl+M", click: () => mainWindow?.webContents.send("navigate", "/models") },
        { label: "MCP Hub", accelerator: "CmdOrCtrl+Shift+M", click: () => mainWindow?.webContents.send("navigate", "/mcp") },
      ],
    },
    {
      label: "Window",
      submenu: [{ role: "minimize" }, { role: "zoom" }, { type: "separator" }, { role: "front" }],
    },
    {
      label: "Help",
      submenu: [
        { label: "Documentation", click: () => shell.openExternal("https://dolphinphoto.ai/docs") },
        { label: "Report Issue", click: () => shell.openExternal("https://github.com/sonamcgoo-dev/dolphinphoto/issues") },
        { type: "separator" },
        { label: "About", click: () => showAbout() },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);
}

function waitForBackendReady(timeoutMs = 15 * 60 * 1000) {
  const deadline = Date.now() + timeoutMs;

  return new Promise((resolve, reject) => {
    const tryPing = () => {
      const request = http.get(BACKEND_URL, (response) => {
        response.resume();
        if (response.statusCode === 200) {
          resolve();
          return;
        }

        if (Date.now() > deadline) {
          reject(new Error(`Backend health check failed with status ${response.statusCode}`));
          return;
        }
        setTimeout(tryPing, 1000);
      });

      request.on("error", () => {
        if (Date.now() > deadline) {
          reject(new Error("Backend startup timeout"));
          return;
        }
        setTimeout(tryPing, 1000);
      });
    };

    tryPing();
  });
}

function spawnProcess(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, options);
    let resolved = false;

    child.once("spawn", () => {
      resolved = true;
      resolve(child);
    });

    child.once("error", (err) => {
      if (!resolved) {
        reject(err);
      }
    });
  });
}

async function startBackend() {
  if (isDev) {
    backendProcess = spawn("python", [path.join(backendDirPath(), "main.py")], {
      cwd: backendDirPath(),
      stdio: "pipe",
      shell: true,
    });
    backendProcess.stdout.on("data", (data) => console.log(`Backend: ${data}`));
    backendProcess.stderr.on("data", (data) => console.error(`Backend Error: ${data}`));
    await waitForBackendReady(120000);
    return;
  }

  const backendDir = backendDirPath();
  const bootstrapScript = path.join(backendDir, "bootstrap_runtime.py");
  const runtimeDir = path.join(app.getPath("userData"), "runtime");
  const workspaceDir = path.join(app.getPath("home"), ".dolphinphoto");
  const pullDefaultModel = process.env.DOLPHINPHOTO_SKIP_MODEL_PULL !== "1";

  const commonArgs = [
    bootstrapScript,
    "--backend-dir",
    backendDir,
    "--runtime-dir",
    runtimeDir,
    "--workspace",
    workspaceDir,
    "--launch-backend",
  ];
  if (pullDefaultModel) {
    commonArgs.push("--pull-default-model");
  }

  const candidates = process.platform === "win32"
    ? [
        { cmd: "py", prefix: ["-3"] },
        { cmd: "python", prefix: [] },
      ]
    : [
        { cmd: "python3", prefix: [] },
        { cmd: "python", prefix: [] },
      ];

  let lastError = null;
  for (const candidate of candidates) {
    try {
      backendProcess = await spawnProcess(candidate.cmd, [...candidate.prefix, ...commonArgs], {
        cwd: backendDir,
        stdio: "pipe",
      });

      backendProcess.stdout.on("data", (data) => console.log(`Backend: ${data}`));
      backendProcess.stderr.on("data", (data) => console.error(`Backend Error: ${data}`));
      backendProcess.on("close", (code) => console.log(`Backend process exited with code ${code}`));
      await waitForBackendReady();
      return;
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError || new Error("Python runtime not found for backend bootstrap");
}

async function openFile(type) {
  const filters = type === "image"
    ? [{ name: "Images", extensions: ["png", "jpg", "jpeg", "webp", "gif"] }]
    : [{ name: "Videos", extensions: ["mp4", "webm", "mov", "avi"] }];

  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ["openFile"],
    filters,
  });

  if (!result.canceled && result.filePaths.length > 0) {
    mainWindow?.webContents.send("file-opened", { path: result.filePaths[0], type });
  }
}

function showAbout() {
  dialog.showMessageBox(mainWindow, {
    type: "info",
    title: "About DolphinPhoto AI Studio",
    message: "DolphinPhoto AI Studio",
    detail: "Version 1.0.0\n\nThe Ultimate AI Creative Studio\n\nBuilt by Black Tiger Computing\nLead Developer: Sona McGoo",
  });
}

function createTray() {
  tray = new Tray(publicAssetPath("icon.png"));

  const contextMenu = Menu.buildFromTemplate([
    { label: "Show DolphinPhoto", click: () => mainWindow?.show() },
    { type: "separator" },
    { label: "AI Studio", click: () => { mainWindow?.show(); mainWindow?.webContents.send("navigate", "/studio"); } },
    { label: "Dream Video", click: () => { mainWindow?.show(); mainWindow?.webContents.send("navigate", "/dream-video"); } },
    { label: "Glowup", click: () => { mainWindow?.show(); mainWindow?.webContents.send("navigate", "/glowup"); } },
    { type: "separator" },
    { label: "Quit", click: () => app.quit() },
  ]);

  tray.setToolTip(APP_NAME);
  tray.setContextMenu(contextMenu);
  tray.on("click", () => mainWindow?.show());
}

ipcMain.handle("select-directory", async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ["openDirectory"],
  });
  return result.canceled ? null : result.filePaths[0];
});

ipcMain.handle("show-save-dialog", async (_event, options) => dialog.showSaveDialog(mainWindow, options));
ipcMain.handle("get-app-path", () => app.getPath("userData"));

app.whenReady().then(async () => {
  createSplashWindow();
  let backendError = null;
  try {
    await startBackend();
  } catch (error) {
    backendError = error;
  }

  createWindow();
  if (!isDev) {
    createTray();
  }

  if (backendError) {
    dialog.showMessageBox({
      type: "warning",
      title: "Backend Startup Warning",
      message: "DolphinPhoto launched, but backend setup did not fully complete.",
      detail: String(backendError),
    });
  }
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    if (backendProcess) {
      backendProcess.kill();
    }
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on("before-quit", () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});
