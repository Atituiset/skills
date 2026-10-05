// Validates the skills directory contract. Zero dependencies, run with:
//   node scripts/validate-skills.mjs
// Checks:
//   1. Every skills/<category>/<skill>/ has a SKILL.md with valid frontmatter
//      (name matches the directory, description present and <= 1024 chars).
//   2. Every category directory has a README.md.
//   3. Relative Markdown links in tracked Markdown files resolve to real files.
//
// On (3): the walk covers **git-tracked files only**, so a local run and a CI run
// agree. Otherwise the check descends into untracked working directories — a
// video project's `frame-packets/` legitimately point at another skill's rule
// files outside this repo — and reports ~90 links that are not broken. A check
// whose findings are all noise is worse than no check, because it teaches you
// to skip it. Falls back to a full walk when git is unavailable.
import { readdirSync, readFileSync, existsSync, statSync } from "node:fs";
import { join, dirname, resolve, relative } from "node:path";
import { execFileSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const skillsDir = join(root, "skills");
const errors = [];

function fail(msg) {
  errors.push(msg);
}

// --- 1 & 2: skill contract ------------------------------------------------
for (const category of readdirSync(skillsDir)) {
  const categoryDir = join(skillsDir, category);
  if (!statSync(categoryDir).isDirectory()) continue;

  if (!existsSync(join(categoryDir, "README.md"))) {
    fail(`skills/${category}/ is missing its category README.md`);
  }

  for (const skill of readdirSync(categoryDir)) {
    const skillDir = join(categoryDir, skill);
    if (!statSync(skillDir).isDirectory()) continue;

    const skillFile = join(skillDir, "SKILL.md");
    if (!existsSync(skillFile)) {
      fail(`skills/${category}/${skill}/ is missing SKILL.md`);
      continue;
    }

    const text = readFileSync(skillFile, "utf8");
    const match = text.match(/^---\n([\s\S]*?)\n---/);
    if (!match) {
      fail(`skills/${category}/${skill}/SKILL.md has no YAML frontmatter`);
      continue;
    }
    const frontmatter = match[1];
    const name = frontmatter.match(/^name:\s*(.+)$/m)?.[1]?.trim();
    const description = frontmatter.match(/^description:\s*(.+)$/m)?.[1]?.trim();

    if (!name) fail(`skills/${category}/${skill}/SKILL.md frontmatter is missing "name"`);
    else if (name !== skill)
      fail(`skills/${category}/${skill}/SKILL.md: name "${name}" does not match directory "${skill}"`);
    if (!description) fail(`skills/${category}/${skill}/SKILL.md frontmatter is missing "description"`);
    else if (description.length > 1024)
      fail(`skills/${category}/${skill}/SKILL.md: description is ${description.length} chars (max 1024)`);
  }
}

// --- 3: relative markdown links resolve -----------------------------------
// Tracked files only, when git can tell us. Falls back to a full walk so the
// check still runs from an unpacked tarball with no .git.
let tracked = null;
try {
  const out = execFileSync("git", ["ls-files", "-z"], { cwd: root, maxBuffer: 64 << 20 }).toString();
  tracked = new Set(out.split("\0").filter(Boolean));
} catch {
  tracked = null;
}

const mdFiles = [];
function collectMd(dir) {
  for (const entry of readdirSync(dir)) {
    if (entry === ".git" || entry === "node_modules") continue;
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) collectMd(p);
    else if (entry.endsWith(".md") && (!tracked || tracked.has(relative(root, p)))) mdFiles.push(p);
  }
}
collectMd(root);

const linkRe = /\[[^\]]*\]\(([^)\s#]+)(#[^)]+)?\)/g;
for (const file of mdFiles) {
  const text = readFileSync(file, "utf8");
  for (const m of text.matchAll(linkRe)) {
    const target = m[1];
    if (/^[a-z]+:/i.test(target) || target.startsWith("mailto:")) continue; // external
    if (target.startsWith("<") || target.endsWith(">")) continue; // placeholder like <project>
    const resolved = resolve(dirname(file), target);
    if (!existsSync(resolved)) {
      fail(`${file.slice(root.length + 1)}: broken link -> ${target}`);
    }
  }
}

if (errors.length) {
  console.error("Skill validation failed:\n");
  for (const e of errors) console.error(`  ✗ ${e}`);
  process.exit(1);
}
console.log("All skills valid.");
