import { copyFileSync, mkdirSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const rootDir = resolve(__dirname, '..');

// Copy skills.json as skills-data.json to public/ for client-side search
const src = resolve(rootDir, 'src/data/skills.json');
const publicDir = resolve(rootDir, 'public');
const dest = resolve(publicDir, 'skills-data.json');

if (!existsSync(src)) {
  console.error('Error: src/data/skills.json not found');
  process.exit(1);
}

mkdirSync(publicDir, { recursive: true });
copyFileSync(src, dest);
console.log('✓ Copied skills-data.json to public/');
