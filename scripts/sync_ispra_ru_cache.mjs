import { createWriteStream } from 'node:fs';
import { mkdir, stat } from 'node:fs/promises';
import path from 'node:path';
import { pipeline } from 'node:stream/promises';

const years = [2020, 2021, 2022, 2023, 2024];
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

for (const year of years) {
  const filename = `ispra_ru_base_${year}_clean.parquet`;
  const relativePath = path.join('.evidence', 'gcs-cache', 'ispra_ru_base', String(year), filename);
  const localPath = path.join(root, relativePath);
  const remoteUrl = `https://storage.googleapis.com/dataciviclab-clean/ispra_ru_base/${year}/${filename}`;

  if (!force && await fileExists(localPath)) {
    console.log(`cache hit ${relativePath}`);
    continue;
  }

  console.log(`downloading ${remoteUrl}`);
  await download(remoteUrl, localPath);
}
