// Driver for the ai-excited-01 entry: places the entry image where the
// harness expects it. The image itself lives in this repository as
// entry.png; this program only copies it, so every run writes the same
// bytes. Standard library only, no network.
import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = dirname(fileURLToPath(import.meta.url));
const sourceImage = join(repoRoot, "entry.png");
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const targetImage = join(outputDir, "entry.png");

if (!existsSync(sourceImage)) {
  console.error(`entry image not found: ${sourceImage}`);
  process.exit(1);
}

mkdirSync(outputDir, { recursive: true });
copyFileSync(sourceImage, targetImage);
const bytes = statSync(targetImage).size;
console.log(`wrote ${targetImage} (${bytes} bytes)`);
