import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const results = path.join(root, 'test-results');
const destination = path.resolve(root, '../docs/evidence/s3/fluxo-central.webm');

function filesUnder(directory) {
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(directory, entry.name);
    return entry.isDirectory() ? filesUnder(full) : [full];
  });
}

const videos = filesUnder(results).filter((file) => file.endsWith('.webm'));
if (!videos.length) throw new Error('Playwright não produziu vídeo do fluxo central.');
videos.sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
fs.mkdirSync(path.dirname(destination), { recursive: true });
fs.copyFileSync(videos[0], destination);
console.log(`Vídeo central copiado para ${destination}`);
