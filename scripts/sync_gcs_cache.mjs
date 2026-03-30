import { createWriteStream } from 'node:fs';
import { mkdir, stat } from 'node:fs/promises';
import path from 'node:path';
import { pipeline } from 'node:stream/promises';

const force = process.env.FORCE_GCS_SYNC === '1';
const root = process.cwd();

const cachePlan = [
  {
    slug: 'ispra_ru_base',
    files: [2020, 2021, 2022, 2023, 2024].map((year) => ({
      remoteUrl: `https://storage.googleapis.com/dataciviclab-clean/ispra_ru_base/${year}/ispra_ru_base_${year}_clean.parquet`,
      relativePath: path.join('.evidence', 'gcs-cache', 'ispra_ru_base', String(year), `ispra_ru_base_${year}_clean.parquet`)
    }))
  },
  {
    slug: 'civile_flussi_2014_2024',
    files: [
      {
        remoteUrl: 'https://storage.googleapis.com/dataciviclab-clean/civile_flussi_2014_2024/2024/civile_flussi_2014_2024_2024_clean.parquet',
        relativePath: path.join('.evidence', 'gcs-cache', 'civile_flussi_2014_2024', '2024', 'civile_flussi_2014_2024_2024_clean.parquet')
      }
    ]
  }
];

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
