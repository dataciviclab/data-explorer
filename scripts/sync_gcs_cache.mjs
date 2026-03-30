import { createWriteStream } from 'node:fs';
import { mkdir, stat } from 'node:fs/promises';
import path from 'node:path';
import { pipeline } from 'node:stream/promises';
import cachePlan from './gcs-cache-plan.json' with { type: 'json' };

const force = process.env.FORCE_GCS_SYNC === '1';
const root = process.cwd();

async function fileExists(filePath) {
  try {
    const info = await stat(filePath);
    return info.isFile() && info.size > 0;
  } catch {
    return false;
  }
}

async function download(url, destination) {
  const response = await fetch(url);
  if (!response.ok || !response.body) {
    throw new Error(`Download failed for ${url}: HTTP ${response.status}`);
  }

  await mkdir(path.dirname(destination), { recursive: true });
  await pipeline(response.body, createWriteStream(destination));
}

for (const dataset of cachePlan) {
  for (const file of dataset.files) {
    const localPath = path.join(root, file.relativePath);

    if (!force && await fileExists(localPath)) {
      console.log(`cache hit ${file.relativePath}`);
      continue;
    }

    console.log(`downloading ${file.remoteUrl}`);
    await download(file.remoteUrl, localPath);
  }
}
