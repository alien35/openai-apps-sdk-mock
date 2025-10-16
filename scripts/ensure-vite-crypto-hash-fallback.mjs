import { promises as fs } from "node:fs";
import path from "node:path";

const projectRoot = process.cwd();
const pnpmDir = path.join(projectRoot, "node_modules", ".pnpm");

async function findViteChunkFile() {
  let entries;
  try {
    entries = await fs.readdir(pnpmDir, { withFileTypes: true });
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") {
      return null;
    }
    throw error;
  }

  const viteDir = entries.find(
    (entry) => entry.isDirectory() && entry.name.startsWith("vite@")
  );

  if (!viteDir) return null;

  const chunksDir = path.join(
    pnpmDir,
    viteDir.name,
    "node_modules",
    "vite",
    "dist",
    "node",
    "chunks"
  );

  let chunkEntries;
  try {
    chunkEntries = await fs.readdir(chunksDir, { withFileTypes: true });
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") {
      return null;
    }
    throw error;
  }

  const candidate = chunkEntries
    .filter((entry) => entry.isFile() && entry.name.startsWith("dep-") && entry.name.endsWith(".js"))
    .map((entry) => path.join(chunksDir, entry.name))
    .find((filePath) => filePath.includes("dep-eRCq8YxU.js"));

  return candidate ?? null;
}

async function ensureFallback() {
  const targetFile = await findViteChunkFile();
  if (!targetFile) return;

  const snapshot = await fs.readFile(targetFile, "utf-8");

  if (snapshot.includes("typeof crypto.hash === \"function\"")) {
    return;
  }

  const marker = "\tconst h$2 = crypto.hash(\"sha256\", text, \"hex\").substring(0, length);";

  if (!snapshot.includes(marker)) {
    return;
  }

  const replacement = snapshot.replace(
    marker,
    [
      "\tconst hashHex = typeof crypto.hash === \"function\"",
      "\t\t? crypto.hash(\"sha256\", text, \"hex\")",
      "\t\t: crypto.createHash(\"sha256\").update(text).digest(\"hex\");",
      "\tconst h$2 = hashHex.substring(0, length);",
    ].join("\n")
  );

  if (replacement === snapshot) return;

  await fs.writeFile(targetFile, replacement, "utf-8");

  const relativeTarget = path.relative(projectRoot, targetFile);
  console.info(`Patched Vite crypto.hash fallback in ${relativeTarget}`);
}

ensureFallback().catch((error) => {
  console.error("Failed to ensure Vite crypto.hash fallback", error);
  process.exitCode = 1;
});
