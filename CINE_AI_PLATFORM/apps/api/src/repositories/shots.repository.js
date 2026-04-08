import fs from "node:fs/promises";
import path from "node:path";

const DATA_DIR = path.resolve(process.cwd(), "apps/api/data");
const SHOTS_FILE = path.join(DATA_DIR, "shots.json");

let writeQueue = Promise.resolve();

async function ensureDataFile() {
  await fs.mkdir(DATA_DIR, { recursive: true });

  try {
    await fs.access(SHOTS_FILE);
  } catch {
    await fs.writeFile(SHOTS_FILE, "[]\n", "utf8");
  }
}

async function readRawShots() {
  await ensureDataFile();
  const raw = await fs.readFile(SHOTS_FILE, "utf8");

  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (error) {
    throw new Error(`shots.json inválido: ${error.message}`);
  }

  if (!Array.isArray(parsed)) {
    throw new Error("shots.json inválido: el contenido raíz debe ser un array");
  }

  return parsed;
}

async function writeRawShots(shots) {
  const payload = `${JSON.stringify(shots, null, 2)}\n`;

  writeQueue = writeQueue.then(async () => {
    const tempFile = `${SHOTS_FILE}.tmp`;
    await fs.writeFile(tempFile, payload, "utf8");
    await fs.rename(tempFile, SHOTS_FILE);
  });

  return writeQueue;
}

export async function initShotsRepository() {
  await ensureDataFile();
  return readRawShots();
}

export async function getAllShots() {
  return readRawShots();
}

export async function getShotById(id) {
  const shots = await readRawShots();
  return shots.find((shot) => String(shot.id) === String(id)) ?? null;
}

export async function createShot(shot) {
  const shots = await readRawShots();
  shots.push(shot);
  await writeRawShots(shots);
  return shot;
}

export async function replaceShots(nextShots) {
  if (!Array.isArray(nextShots)) {
    throw new Error("replaceShots requiere un array");
  }

  await writeRawShots(nextShots);
  return nextShots;
}

export async function updateShot(id, updater) {
  const shots = await readRawShots();
  const index = shots.findIndex((shot) => String(shot.id) === String(id));

  if (index === -1) {
    return null;
  }

  const current = shots[index];
  const next =
    typeof updater === "function"
      ? await updater(structuredClone(current))
      : { ...current, ...updater };

  shots[index] = next;
  await writeRawShots(shots);
  return next;
}

export async function deleteShot(id) {
  const shots = await readRawShots();
  const index = shots.findIndex((shot) => String(shot.id) === String(id));

  if (index === -1) {
    return false;
  }

  shots.splice(index, 1);
  await writeRawShots(shots);
  return true;
}