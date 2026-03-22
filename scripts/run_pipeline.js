/**
 * run_pipeline.js
 * ---------------
 * Reads promptList.txt line by line (format: "Title, Topic"),
 * runs the Playwright crossword generator for each entry at 3 difficulty levels,
 * then runs the Python CSV parser on each output HTML.
 *
 * Usage (from scripts/ directory):
 *   node run_pipeline.js
 */

const { execSync } = require('child_process');
const fs   = require('fs');
const path = require('path');

// ── Config ────────────────────────────────────────────────────────────────────
const PROMPT_FILE    = path.join(__dirname, 'promptList.txt');
const RAW_HTML_DIR   = path.join(__dirname, 'rawhtmls');
const PARSED_CSV_DIR = path.join(__dirname, 'parsedCSVs');
const PYTHON_SCRIPT  = path.join(__dirname, 'parse_crossword.py');
const PYTHON_CMD     = process.platform === 'win32' ? 'python' : 'python3';

const DIFFICULTIES = [
  { name: 'easy',   spec: 'playwright/easycrossword.spec.ts'   },
  { name: 'medium', spec: 'playwright/mediumcrossword.spec.ts' },
  { name: 'hard',   spec: 'playwright/hardcrossword.spec.ts'   },
];
// ─────────────────────────────────────────────────────────────────────────────

console.log('Pipeline starting...');

function ensureDirs() {
  for (const diff of DIFFICULTIES) {
    const htmlDir = path.join(RAW_HTML_DIR, diff.name);
    const csvDir  = path.join(PARSED_CSV_DIR, diff.name);
    for (const dir of [htmlDir, csvDir]) {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        console.log(`Created folder: ${dir}`);
      }
    }
  }
}

function loadPrompts() {
  if (!fs.existsSync(PROMPT_FILE)) {
    throw new Error(`'${PROMPT_FILE}' not found.`);
  }

  const lines = fs.readFileSync(PROMPT_FILE, 'utf-8')
    .split('\n')
    .map(l => l.trim())
    .filter(l => l.length > 0 && !l.startsWith('#'));

  return lines.map((line, i) => {
    const commaIndex = line.indexOf(',');
    if (commaIndex === -1) {
      throw new Error(`Line ${i + 1} malformed: "${line}" — expected format: Title, Topic`);
    }
    return {
      title: line.slice(0, commaIndex).trim(),
      topic: line.slice(commaIndex + 1).trim(),
    };
  });
}

function runPlaywright(title, topic, specFile, htmlDir, htmlFilename) {
  const env = {
    ...process.env,
    PUZZLE_TITLE: title,
    PUZZLE_TOPIC: topic,
    OUTPUT_DIR:   htmlDir,
    OUTPUT_FILE:  htmlFilename,
  };

  const diffLabel = path.basename(specFile, '.spec.ts').replace('crossword', '').trim() || 'medium';
  console.log(`  ▶ Playwright [${diffLabel}]: "${title}"`);

  try {
    execSync(
      `npx playwright test ${specFile} --project=chromium --reporter=line`,
      { env, stdio: 'inherit', timeout: 120000, cwd: __dirname }
    );
  } catch (err) {
    // Chromium may still have succeeded even if exit code is non-zero
  }
}

function runPythonParser(htmlPath, csvPath) {
  console.log(`  ▶ Parsing: ${path.basename(htmlPath)} → ${path.basename(csvPath)}`);
  try {
    execSync(
      `${PYTHON_CMD} "${PYTHON_SCRIPT}" "${htmlPath}" "${csvPath}"`,
      { stdio: 'inherit', timeout: 30000, cwd: __dirname }
    );
    return true;
  } catch (err) {
    console.error(`  ✗ Python parser failed for: ${htmlPath}`);
    return false;
  }
}

function main() {
  ensureDirs();

  const prompts = loadPrompts();
  console.log(`Found ${prompts.length} prompts × ${DIFFICULTIES.length} difficulties = ${prompts.length * DIFFICULTIES.length} total puzzles\n`);

  const results = [];

  for (let i = 0; i < prompts.length; i++) {
    const { title, topic } = prompts[i];

    console.log(`\n${'═'.repeat(60)}`);
    console.log(`[${i + 1}/${prompts.length}] "${title}" (${topic})`);
    console.log(`${'═'.repeat(60)}`);

    for (const diff of DIFFICULTIES) {
      const timestamp  = Date.now();
      const htmlDir    = path.join(RAW_HTML_DIR, diff.name);
      const csvDir     = path.join(PARSED_CSV_DIR, diff.name);
      const htmlFile   = `${timestamp}_PuzzleHTML.html`;
      const csvFile    = `${timestamp}_parsedCSV.csv`;
      const htmlPath   = path.join(htmlDir, htmlFile);
      const csvPath    = path.join(csvDir, csvFile);

      console.log(`\n  ── ${diff.name.toUpperCase()} ──`);

      runPlaywright(title, topic, diff.spec, htmlDir, htmlFile);

      if (!fs.existsSync(htmlPath)) {
        console.error(`  ✗ HTML not found at ${htmlPath} — skipping parse`);
        results.push({ title, difficulty: diff.name, success: false });
        continue;
      }

      const ok = runPythonParser(htmlPath, csvPath);
      results.push({ title, difficulty: diff.name, success: ok });
    }
  }

  // ── Summary ───────────────────────────────────────────────────────────────
  console.log(`\n${'═'.repeat(60)}`);
  console.log('PIPELINE COMPLETE — Summary:');
  console.log(`${'═'.repeat(60)}`);
  for (const r of results) {
    console.log(`  ${r.success ? '✓' : '✗'}  [${r.difficulty.padEnd(6)}] ${r.title}`);
  }
  const passed = results.filter(r => r.success).length;
  console.log(`\n${passed}/${results.length} puzzles completed successfully.`);

  // ── Next steps hint ─────────────────────────────────────────────────────
  if (passed > 0) {
    console.log(`\nNext steps:`);
    console.log(`  1. Generate runtime JSON:`);
    console.log(`     python3 generate_crosswords.py --csv-dir parsedCSVs --recursive --start-date YYYY-MM-DD`);
    console.log(`  2. Upload to R2:`);
    console.log(`     python3 upload_to_r2.py`);
  }
}

try {
  main();
} catch (err) {
  console.error('Fatal error:', err.message);
  process.exit(1);
}
