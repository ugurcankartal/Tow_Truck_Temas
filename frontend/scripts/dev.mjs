/**
 * backend/.env içindeki DEV_PORT ile Astro dev sunucusunu başlatır.
 */
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const backendEnvPath = resolve(__dirname, '../../backend/.env');

function readEnvValue(key, fallback) {
  if (!existsSync(backendEnvPath)) return fallback;
  const content = readFileSync(backendEnvPath, 'utf8');
  const match = content.match(new RegExp(`^${key}=(.+)$`, 'm'));
  return match?.[1]?.trim() || fallback;
}

const devPort = readEnvValue('DEV_PORT', '8000');
const frontendDevPort = readEnvValue('FRONTEND_DEV_PORT', '4321');

process.env.PUBLIC_API_URL = `http://127.0.0.1:${devPort}`;
if (!process.env.PUBLIC_SITE_URL) {
  process.env.PUBLIC_SITE_URL = `http://localhost:${frontendDevPort}`;
}
if (!process.env.SITE_URL) {
  process.env.SITE_URL = process.env.PUBLIC_SITE_URL;
}

const child = spawn(
  'npx',
  ['astro', 'dev', '--port', frontendDevPort],
  { stdio: 'inherit', shell: true, env: process.env },
);

child.on('exit', (code) => process.exit(code ?? 0));
