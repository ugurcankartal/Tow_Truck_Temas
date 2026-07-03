#!/usr/bin/env node
/**
 * Astro rebuild webhook dinleyicisi.
 *
 * Kullanım:
 *   WEBHOOK_SECRET=your-secret node scripts/webhook-rebuild.mjs
 *   # veya
 *   npm run webhook:rebuild
 *
 * Django .env:
 *   ASTRO_REBUILD_WEBHOOK_URL=http://127.0.0.1:9876/rebuild
 *   ASTRO_REBUILD_WEBHOOK_SECRET=your-secret
 */

import http from 'node:http';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const PORT = Number(process.env.WEBHOOK_PORT || 9876);
const SECRET = process.env.WEBHOOK_SECRET || process.env.ASTRO_REBUILD_WEBHOOK_SECRET || '';
const BUILD_SCRIPT = process.env.ASTRO_BUILD_SCRIPT || 'build';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

let building = false;

function runBuild() {
  return new Promise((resolve, reject) => {
    const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';
    const child = spawn(npm, ['run', BUILD_SCRIPT], {
      cwd: ROOT,
      stdio: 'inherit',
      shell: process.platform === 'win32',
    });
    child.on('close', (code) => (code === 0 ? resolve() : reject(new Error(`build exit ${code}`))));
  });
}

const server = http.createServer(async (req, res) => {
  if (req.method === 'POST' && req.url === '/rebuild') {
    if (SECRET && req.headers['x-webhook-secret'] !== SECRET) {
      res.writeHead(403, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ detail: 'Yetkisiz' }));
      return;
    }

    if (building) {
      res.writeHead(409, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ detail: 'Build zaten çalışıyor' }));
      return;
    }

    building = true;
    res.writeHead(202, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ detail: 'Astro rebuild başlatıldı' }));

    try {
      console.log(`[webhook] npm run ${BUILD_SCRIPT} başlıyor...`);
      await runBuild();
      console.log('[webhook] Build tamamlandı');
    } catch (err) {
      console.error('[webhook] Build hatası:', err.message);
    } finally {
      building = false;
    }
    return;
  }

  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', building }));
    return;
  }

  res.writeHead(404);
  res.end();
});

server.listen(PORT, () => {
  console.log(`[webhook] Dinleniyor: http://127.0.0.1:${PORT}/rebuild`);
  console.log(`[webhook] Health: http://127.0.0.1:${PORT}/health`);
  console.log(`[webhook] Build script: ${BUILD_SCRIPT}`);
});
