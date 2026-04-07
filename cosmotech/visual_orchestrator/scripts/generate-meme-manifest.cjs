#!/usr/bin/env node
/**
 * Scans public/memes/ for .gif files and writes src/memeList.json.
 * Runs automatically via prestart / prebuild npm hooks so that
 * adding a new .gif to public/memes/ is all that's needed.
 *
 * Names are stored WITHOUT the .gif extension (the code appends it).
 */
const fs = require("fs");
const path = require("path");

const memesDir = path.resolve(__dirname, "..", "public", "memes");
const outFile = path.resolve(__dirname, "..", "src", "memeList.json");

const gifs = fs
  .readdirSync(memesDir)
  .filter((f) => f.endsWith(".gif"))
  .map((f) => f.replace(/\.gif$/, ""))
  .sort();

fs.writeFileSync(outFile, JSON.stringify(gifs, null, 2) + "\n");
console.log(`memeList.json generated with ${gifs.length} gif(s): ${gifs.join(", ")}`);
