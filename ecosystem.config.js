// PM2 process definitions for running EPD-Hub backend directly on Windows,
// without Docker. Mirrors the pattern already used for payment-server and
// ismp-zero-line on this host.
//
// Prereqs on this machine:
//   - Memurai (Redis-compatible) installed as a Windows service, port 6379
//   - Python deps installed for Python314 (see requirements.txt, minus
//     psycopg2-binary which isn't needed - DATABASE_URL below uses SQLite)
//   - C:\epd-hub\.env holds NOTEBOOKLM_NOTEBOOK_URL (never committed)
//
// Start with: pm2 start ecosystem.config.js
// Persist across reboots: pm2 save

const fs = require("fs");
const path = require("path");

const PYTHON = "C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python314\\python.exe";
const CWD = "C:\\epd-hub\\backend";

// Minimal .env parser (no dotenv dependency) - reads secrets out of the
// gitignored C:\epd-hub\.env file so they never need to live in this file.
function loadDotEnv(envPath) {
  const out = {};
  if (!fs.existsSync(envPath)) return out;
  for (const line of fs.readFileSync(envPath, "utf8").split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq === -1) continue;
    out[trimmed.slice(0, eq).trim()] = trimmed.slice(eq + 1).trim();
  }
  return out;
}

const dotEnv = loadDotEnv(path.join(__dirname, ".env"));

const sharedEnv = {
  DATABASE_URL: "sqlite:///C:/epd-hub/epd_hub.db",
  CELERY_BROKER_URL: "redis://localhost:6379/0",
  CELERY_RESULT_BACKEND: "redis://localhost:6379/0",
  NOTEBOOKLM_NOTEBOOK_URL: dotEnv.NOTEBOOKLM_NOTEBOOK_URL || "",
  NOTEBOOKLM_STATE_DIR: "C:\\epd-hub\\notebooklm_state",
  ASK_CACHE_TTL_SECONDS: dotEnv.ASK_CACHE_TTL_SECONDS || "3600",
  DEBUG: "false",
  LOG_LEVEL: "INFO",
};

module.exports = {
  apps: [
    {
      name: "epd-hub-backend",
      script: PYTHON,
      args: "-m uvicorn app.main:app --host 0.0.0.0 --port 8010",
      cwd: CWD,
      interpreter: "none",
      env: sharedEnv,
      autorestart: true,
      max_restarts: 10,
    },
    {
      name: "epd-hub-celery",
      script: PYTHON,
      // -A app.celery_app:celery_app - the Celery instance lives there, not in app.tasks
      //   (celery_app now has include=["app.tasks"] so tasks still register).
      // --pool=solo: Celery's default prefork pool needs fork(), unavailable on Windows.
      args: "-m celery -A app.celery_app:celery_app worker --loglevel=info --pool=solo",
      cwd: CWD,
      interpreter: "none",
      env: sharedEnv,
      autorestart: true,
      max_restarts: 10,
    },
  ],
};
