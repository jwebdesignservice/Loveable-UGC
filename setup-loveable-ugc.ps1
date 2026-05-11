# setup-loveable-ugc.ps1
# Scaffolds the Loveable-UGC project at the path below.
# Usage: right-click -> Run with PowerShell, or run from a PowerShell prompt.

$root = "C:\Users\Jack\Desktop\AI Website\htdocs\Websites\Loveable-UGC"

New-Item -ItemType Directory -Force -Path `
    $root, `
    "$root\src", `
    "$root\src\pillars", `
    "$root\assets\example-project", `
    "$root\content" | Out-Null

# ---------- package.json ----------
@'
{
  "name": "loveable-ugc",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "description": "Automated UGC content generator for Loveable (lovable.dev) videos",
  "scripts": {
    "generate": "tsx src/cli.ts generate",
    "generate-day": "tsx src/cli.ts generate-day",
    "schedule": "tsx src/cli.ts schedule"
  },
  "dependencies": {
    "@anthropic-ai/sdk": "^0.95.1",
    "commander": "^12.1.0",
    "dayjs": "^1.11.13",
    "dotenv": "^16.4.5",
    "gray-matter": "^4.0.3",
    "js-yaml": "^4.1.0"
  },
  "devDependencies": {
    "@types/js-yaml": "^4.0.9",
    "@types/node": "^22.10.0",
    "tsx": "^4.19.2",
    "typescript": "^5.7.2"
  }
}
'@ | Set-Content "$root\package.json" -Encoding utf8

# ---------- tsconfig.json ----------
@'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "allowImportingTsExtensions": false,
    "noEmit": true,
    "isolatedModules": true
  },
  "include": ["src/**/*"]
}
'@ | Set-Content "$root\tsconfig.json" -Encoding utf8

# ---------- .env.example ----------
"ANTHROPIC_API_KEY=sk-ant-..." | Set-Content "$root\.env.example" -Encoding utf8

# ---------- .gitignore ----------
@'
node_modules/
.env
.env.local
dist/
.DS_Store
*.log
'@ | Set-Content "$root\.gitignore" -Encoding utf8

# ---------- schedule.json ----------
@'
{
  "slots": ["09:00", "13:00", "19:00"],
  "platforms": ["tiktok", "reels", "shorts"],
  "rotation": [
    "site-previews",
    "one-prompt-site",
    "one-shot-revamp",
    "how-to",
    "common-mistakes"
  ]
}
'@ | Set-Content "$root\schedule.json" -Encoding utf8

# ---------- README.md ----------
@'
# Loveable UGC Content Generator

Automated short-form video script generator for UGC content about Lovable (lovable.dev). Built on the Anthropic SDK with Claude Opus 4.7.

## Content pillars

- `site-previews` — carousel walkthrough of a finished site
- `one-prompt-site` — one prompt -> finished site reveal
- `one-shot-revamp` — before/after site rebuild
- `how-to` — concrete technique inside Lovable
- `common-mistakes` — call out a bad pattern + show the fix

## Schedule

3 videos/day at 09:00, 13:00, 19:00. Pillars rotate evenly across all 5. Configure in `schedule.json`.

## Setup

```bash
npm install
cp .env.example .env  # fill in ANTHROPIC_API_KEY
```

## Projects

Each project lives in `assets/<slug>/` with a `project.yaml`. See `assets/example-project/` for the shape. Drop screenshots in the same folder.

## Usage

```bash
npm run schedule
npm run generate -- --pillar=how-to --project=my-site --time=09:00
npm run generate-day
npm run generate-day -- --date=2026-05-12
```

Output lands in `content/YYYY-MM-DD/HHMM-<pillar>-<slug>.md`.
'@ | Set-Content "$root\README.md" -Encoding utf8

# ---------- src/types.ts ----------
@'
export type Pillar =
  | "site-previews"
  | "one-prompt-site"
  | "one-shot-revamp"
  | "how-to"
  | "common-mistakes";

export interface Project {
  slug: string;
  title: string;
  description?: string;
  url?: string;
  lovable_prompts?: string[];
  images?: string[];
  before_after?: { before: string; after: string };
  notes?: string;
}

export interface Slot {
  date: string;
  time: string;
  pillar: Pillar;
}

export interface VideoContent {
  hook: string;
  voiceover: string;
  on_screen_text: string[];
  shots: string[];
  caption: string;
  hashtags: string[];
  cta: string;
  duration_sec: number;
}

export interface ScheduleConfig {
  slots: string[];
  platforms: string[];
  rotation: Pillar[];
}
'@ | Set-Content "$root\src\types.ts" -Encoding utf8

# ---------- src/claude.ts ----------
@'
import Anthropic from "@anthropic-ai/sdk";
import "dotenv/config";

const MODEL = "claude-opus-4-7";
const client = new Anthropic();

export interface GenerateOptions {
  system: string;
  user: string;
  schema: Record<string, unknown>;
}

export async function generateStructured<T>(opts: GenerateOptions): Promise<T> {
  const response = await client.messages.create({
    model: MODEL,
    max_tokens: 16000,
    thinking: { type: "adaptive" },
    output_config: {
      effort: "high",
      format: { type: "json_schema", schema: opts.schema },
    },
    system: [
      { type: "text", text: opts.system, cache_control: { type: "ephemeral" } },
    ],
    messages: [{ role: "user", content: opts.user }],
  });

  for (const block of response.content) {
    if (block.type === "text") return JSON.parse(block.text) as T;
  }
  throw new Error("No text block in response");
}
'@ | Set-Content "$root\src\claude.ts" -Encoding utf8

# ---------- src/schedule.ts ----------
@'
import dayjs from "dayjs";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import type { Pillar, ScheduleConfig, Slot } from "./types.js";

export function loadSchedule(cwd = process.cwd()): ScheduleConfig {
  const raw = readFileSync(resolve(cwd, "schedule.json"), "utf8");
  return JSON.parse(raw) as ScheduleConfig;
}

export function slotsForDay(date: string, cfg: ScheduleConfig): Slot[] {
  const epoch = dayjs("2026-01-01");
  const dayIndex = dayjs(date).diff(epoch, "day");
  const baseOffset = (dayIndex * cfg.slots.length) % cfg.rotation.length;

  return cfg.slots.map((time, i) => {
    const pillarIdx = (baseOffset + i) % cfg.rotation.length;
    return { date, time, pillar: cfg.rotation[pillarIdx] as Pillar };
  });
}
'@ | Set-Content "$root\src\schedule.ts" -Encoding utf8

# ---------- src/writer.ts ----------
@'
import matter from "gray-matter";
import { mkdirSync, writeFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import type { Pillar, Project, VideoContent } from "./types.js";

export interface WriteArgs {
  date: string;
  time: string;
  pillar: Pillar;
  project: Project;
  content: VideoContent;
  outDir?: string;
}

export function writeVideoMarkdown(args: WriteArgs): string {
  const { date, time, pillar, project, content, outDir = "content" } = args;
  const slugTime = time.replace(":", "");
  const filename = `${slugTime}-${pillar}-${project.slug}.md`;
  const path = resolve(outDir, date, filename);

  const frontmatter = {
    pillar,
    date,
    slot: time,
    status: "draft" as const,
    source_project: project.slug,
    duration_sec: content.duration_sec,
    platforms: ["tiktok", "reels", "shorts"],
  };

  const body = renderBody(content, project);
  const file = matter.stringify(body, frontmatter);

  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, file, "utf8");
  return path;
}

function renderBody(c: VideoContent, p: Project): string {
  const lines: string[] = [];
  lines.push(`# ${p.title} - ${c.hook}`, "");
  lines.push("## Hook (first 3s)", "", c.hook, "");
  lines.push("## Voiceover", "", c.voiceover, "");
  lines.push("## On-screen text");
  for (const t of c.on_screen_text) lines.push(`- ${t}`);
  lines.push("");
  lines.push("## Shots / B-roll");
  for (const s of c.shots) lines.push(`- ${s}`);
  lines.push("");
  lines.push("## Caption", "", c.caption, "");
  lines.push("## Hashtags", "", c.hashtags.join(" "), "");
  lines.push("## CTA", "", c.cta, "");
  if (p.lovable_prompts?.length) {
    lines.push("## Lovable prompts (on-camera)");
    for (const lp of p.lovable_prompts) lines.push(`> ${lp}`);
    lines.push("");
  }
  return lines.join("\n");
}
'@ | Set-Content "$root\src\writer.ts" -Encoding utf8

# ---------- src/projects.ts ----------
@'
import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { resolve, join } from "node:path";
import yaml from "js-yaml";
import type { Project } from "./types.js";

export function loadProject(slug: string, cwd = process.cwd()): Project {
  const dir = resolve(cwd, "assets", slug);
  const yml = join(dir, "project.yaml");
  const yamlAlt = join(dir, "project.yml");
  const path = existsSync(yml) ? yml : yamlAlt;
  if (!existsSync(path)) throw new Error(`No project.yaml found in ${dir}`);
  const data = yaml.load(readFileSync(path, "utf8")) as Project;
  if (!data.slug) data.slug = slug;
  return data;
}

export function listProjects(cwd = process.cwd()): string[] {
  const dir = resolve(cwd, "assets");
  if (!existsSync(dir)) return [];
  return readdirSync(dir).filter((name) => {
    const p = join(dir, name);
    return statSync(p).isDirectory();
  });
}

export function pickProject(slugs: string[], seed: string): string {
  if (slugs.length === 0) {
    throw new Error("No projects in assets/. Add one (assets/<slug>/project.yaml).");
  }
  let hash = 0;
  for (let i = 0; i < seed.length; i++) hash = (hash * 31 + seed.charCodeAt(i)) | 0;
  return slugs[Math.abs(hash) % slugs.length] as string;
}
'@ | Set-Content "$root\src\projects.ts" -Encoding utf8

# ---------- src/cli.ts ----------
@'
import { Command } from "commander";
import dayjs from "dayjs";
import { getGenerator } from "./pillars/index.js";
import { loadProject, listProjects, pickProject } from "./projects.js";
import { loadSchedule, slotsForDay } from "./schedule.js";
import type { Pillar, Slot } from "./types.js";
import { writeVideoMarkdown } from "./writer.js";

const program = new Command();
program.name("loveable-ugc").description("Automated UGC content generator for Loveable videos");

program
  .command("schedule")
  .description("Print the 3-slot schedule for a date")
  .option("--date <YYYY-MM-DD>", "date", dayjs().format("YYYY-MM-DD"))
  .action((opts: { date: string }) => {
    const cfg = loadSchedule();
    const slots = slotsForDay(opts.date, cfg);
    for (const s of slots) console.log(`${s.date} ${s.time} ${s.pillar}`);
  });

program
  .command("generate")
  .description("Generate one video script for a single slot")
  .requiredOption("--pillar <pillar>", "pillar")
  .requiredOption("--project <slug>", "project slug in assets/")
  .option("--date <YYYY-MM-DD>", "date", dayjs().format("YYYY-MM-DD"))
  .option("--time <HH:MM>", "time", "12:00")
  .action(async (opts: { pillar: Pillar; project: string; date: string; time: string }) => {
    const project = loadProject(opts.project);
    const gen = getGenerator(opts.pillar);
    if (!gen) throw new Error(`Unknown pillar: ${opts.pillar}`);
    const content = await gen(project);
    const path = writeVideoMarkdown({
      date: opts.date,
      time: opts.time,
      pillar: opts.pillar,
      project,
      content,
    });
    console.log(`Wrote ${path}`);
  });

program
  .command("generate-day")
  .description("Generate all 3 videos for a day")
  .option("--date <YYYY-MM-DD>", "date", dayjs().format("YYYY-MM-DD"))
  .option("--project <slug>", "force a single project for all 3 slots")
  .action(async (opts: { date: string; project?: string }) => {
    const cfg = loadSchedule();
    const slots = slotsForDay(opts.date, cfg);
    const projects = listProjects();
    if (!opts.project && projects.length === 0) {
      throw new Error("No projects found in assets/. Add one or pass --project.");
    }
    for (const slot of slots) {
      const slug =
        opts.project ?? pickProject(projects, `${slot.date}-${slot.time}-${slot.pillar}`);
      await runSlot(slot, slug);
    }
  });

async function runSlot(slot: Slot, slug: string): Promise<void> {
  const project = loadProject(slug);
  const gen = getGenerator(slot.pillar);
  console.log(`[${slot.date} ${slot.time}] ${slot.pillar} <- ${slug}`);
  const content = await gen(project);
  const path = writeVideoMarkdown({
    date: slot.date,
    time: slot.time,
    pillar: slot.pillar,
    project,
    content,
  });
  console.log(`  -> ${path}`);
}

program.parseAsync().catch((err) => {
  console.error(err);
  process.exit(1);
});
'@ | Set-Content "$root\src\cli.ts" -Encoding utf8

# ---------- src/pillars/_schema.ts ----------
@'
export const videoContentSchema = {
  type: "object",
  additionalProperties: false,
  properties: {
    hook: { type: "string", description: "First 3 seconds. One sentence. Pattern-interrupt." },
    voiceover: { type: "string", description: "Full VO script as one block. ~30-45s spoken." },
    on_screen_text: {
      type: "array",
      items: { type: "string" },
      description: "3-7 short on-screen text beats synced to VO.",
    },
    shots: {
      type: "array",
      items: { type: "string" },
      description: "Shot list / screen recordings / B-roll cues in order.",
    },
    caption: { type: "string", description: "Platform caption." },
    hashtags: {
      type: "array",
      items: { type: "string" },
      description: "5-10 hashtags including #lovable.",
    },
    cta: { type: "string", description: "Final call-to-action line." },
    duration_sec: { type: "integer", description: "Target duration in seconds, 20-60." },
  },
  required: [
    "hook",
    "voiceover",
    "on_screen_text",
    "shots",
    "caption",
    "hashtags",
    "cta",
    "duration_sec",
  ],
} as const;
'@ | Set-Content "$root\src\pillars\_schema.ts" -Encoding utf8

# ---------- src/pillars/index.ts ----------
@'
import type { Pillar, Project, VideoContent } from "../types.js";
import * as sitePreviews from "./site-previews.js";
import * as onePromptSite from "./one-prompt-site.js";
import * as oneShotRevamp from "./one-shot-revamp.js";
import * as howTo from "./how-to.js";
import * as commonMistakes from "./common-mistakes.js";

type Generator = (p: Project) => Promise<VideoContent>;

const map: Record<Pillar, Generator> = {
  "site-previews": sitePreviews.generate,
  "one-prompt-site": onePromptSite.generate,
  "one-shot-revamp": oneShotRevamp.generate,
  "how-to": howTo.generate,
  "common-mistakes": commonMistakes.generate,
};

export function getGenerator(pillar: Pillar): Generator {
  return map[pillar];
}

export const allPillars: Pillar[] = [
  "site-previews",
  "one-prompt-site",
  "one-shot-revamp",
  "how-to",
  "common-mistakes",
];
'@ | Set-Content "$root\src\pillars\index.ts" -Encoding utf8

# ---------- src/pillars/site-previews.ts ----------
@'
import { generateStructured } from "../claude.js";
import type { Project, VideoContent } from "../types.js";
import { videoContentSchema } from "./_schema.js";

const SYSTEM = `You write short-form UGC scripts for a creator who builds websites with Lovable (lovable.dev) and posts demos to TikTok, Reels, and Shorts.

Pillar: SITE PAGE PREVIEWS CAROUSELS
Goal: Walk through 3-5 pages/sections of a finished Lovable site as a satisfying carousel/montage.

Style rules:
- Hook in first 3 seconds. Pattern-interrupt. No "Hey guys".
- Voiceover is punchy, confident, not salesy.
- On-screen text echoes VO beats, not duplicates.
- Shots are concrete: "scroll hero", "hover CTA", "click pricing tab".
- End with a CTA pointing to the live site or "I'll build yours".
- Target 25-40 seconds.`;

export async function generate(project: Project): Promise<VideoContent> {
  const user = `Project: ${project.title}
Slug: ${project.slug}
Description: ${project.description ?? "(none provided)"}
URL: ${project.url ?? "(none)"}
Screens available: ${(project.images ?? []).join(", ") || "(creator will pick)"}
Notes: ${project.notes ?? ""}

Write a site-preview carousel script.`;

  return generateStructured<VideoContent>({
    system: SYSTEM,
    user,
    schema: videoContentSchema as unknown as Record<string, unknown>,
  });
}
'@ | Set-Content "$root\src\pillars\site-previews.ts" -Encoding utf8

# ---------- src/pillars/one-prompt-site.ts ----------
@'
import { generateStructured } from "../claude.js";
import type { Project, VideoContent } from "../types.js";
import { videoContentSchema } from "./_schema.js";

const SYSTEM = `You write short-form UGC scripts for a creator who builds with Lovable (lovable.dev).

Pillar: ONE PROMPT SITE
Goal: One prompt -> finished site. Show the prompt, then cut to result.

Style rules:
- Hook leads with the prompt or the result.
- Reveal the actual prompt on screen at some point.
- Shots: type/paste prompt, generation animation, scroll final site.
- End with the prompt as text + "steal this prompt" CTA.
- Target 30-45 seconds.`;

export async function generate(project: Project): Promise<VideoContent> {
  const prompts = project.lovable_prompts ?? [];
  const user = `Project: ${project.title}
Slug: ${project.slug}
Description: ${project.description ?? "(none provided)"}
URL: ${project.url ?? "(none)"}
The actual Lovable prompt(s) used:
${prompts.length ? prompts.map((p) => `- ${p}`).join("\n") : "(creator will fill in)"}
Notes: ${project.notes ?? ""}

Write a one-prompt-site script. Reference the actual prompt in the VO and on-screen text.`;

  return generateStructured<VideoContent>({
    system: SYSTEM,
    user,
    schema: videoContentSchema as unknown as Record<string, unknown>,
  });
}
'@ | Set-Content "$root\src\pillars\one-prompt-site.ts" -Encoding utf8

# ---------- src/pillars/one-shot-revamp.ts ----------
@'
import { generateStructured } from "../claude.js";
import type { Project, VideoContent } from "../types.js";
import { videoContentSchema } from "./_schema.js";

const SYSTEM = `You write short-form UGC scripts for a creator who revamps existing websites in Lovable.

Pillar: ONE-SHOT SITE REVAMP
Goal: Take an ugly/dated site and rebuild it in Lovable in one pass. Before/after is the payoff.

Style rules:
- Hook: "Look at this site" + show the before. A bit savage, never cruel.
- Mid: the prompt fed to Lovable.
- Big reveal of the after.
- Shots: before scroll, side-by-side, after scroll, micro-interactions.
- CTA: "want yours done? comment 'revamp'".
- Target 30-50 seconds.`;

export async function generate(project: Project): Promise<VideoContent> {
  const ba = project.before_after;
  const user = `Project: ${project.title}
Slug: ${project.slug}
Description: ${project.description ?? "(none provided)"}
Before: ${ba?.before ?? "(creator will show)"}
After: ${ba?.after ?? "(creator will show)"}
URL of result: ${project.url ?? "(none)"}
Lovable prompt used: ${(project.lovable_prompts ?? [])[0] ?? "(creator will fill in)"}
Notes: ${project.notes ?? ""}

Write a one-shot revamp script.`;

  return generateStructured<VideoContent>({
    system: SYSTEM,
    user,
    schema: videoContentSchema as unknown as Record<string, unknown>,
  });
}
'@ | Set-Content "$root\src\pillars\one-shot-revamp.ts" -Encoding utf8

# ---------- src/pillars/how-to.ts ----------
@'
import { generateStructured } from "../claude.js";
import type { Project, VideoContent } from "../types.js";
import { videoContentSchema } from "./_schema.js";

const SYSTEM = `You write short-form UGC scripts for a creator who teaches Lovable.

Pillar: HOW-TO SERIES
Goal: One concrete technique. Educational, screenshot-heavy. Viewer can do the thing after one watch.

Style rules:
- Hook is the problem or outcome.
- VO is step-by-step but tight. 3-5 steps max.
- On-screen text is numbered.
- Shots show the click path inside Lovable's UI.
- CTA: "save this for later" or "follow for more".
- Target 30-60 seconds.`;

export async function generate(project: Project): Promise<VideoContent> {
  const user = `Topic: ${project.title}
Slug: ${project.slug}
Description: ${project.description ?? "(none provided)"}
Reference: ${project.url ?? "(none)"}
Screens: ${(project.images ?? []).join(", ") || "(creator will pick)"}
Notes / steps: ${project.notes ?? ""}

Write a how-to script. Be specific about the click path.`;

  return generateStructured<VideoContent>({
    system: SYSTEM,
    user,
    schema: videoContentSchema as unknown as Record<string, unknown>,
  });
}
'@ | Set-Content "$root\src\pillars\how-to.ts" -Encoding utf8

# ---------- src/pillars/common-mistakes.ts ----------
@'
import { generateStructured } from "../claude.js";
import type { Project, VideoContent } from "../types.js";
import { videoContentSchema } from "./_schema.js";

const SYSTEM = `You write short-form UGC scripts for a creator who calls out common mistakes in Lovable.

Pillar: COMMON MISTAKES
Goal: One specific mistake. Show bad pattern, explain why, show the fix. Punchy and a little spicy.

Style rules:
- Hook states the mistake bluntly.
- VO: name the mistake, show example, explain the fix.
- On-screen text: bad pattern with strikethrough, then the fix.
- CTA: "what's another one? drop it in the comments".
- Target 25-45 seconds.`;

export async function generate(project: Project): Promise<VideoContent> {
  const user = `Mistake: ${project.title}
Slug: ${project.slug}
Description: ${project.description ?? "(none provided)"}
Reference: ${project.url ?? "(none)"}
Screens: ${(project.images ?? []).join(", ") || "(creator will pick)"}
Fix notes: ${project.notes ?? ""}

Write a common-mistakes script focused on this one mistake.`;

  return generateStructured<VideoContent>({
    system: SYSTEM,
    user,
    schema: videoContentSchema as unknown as Record<string, unknown>,
  });
}
'@ | Set-Content "$root\src\pillars\common-mistakes.ts" -Encoding utf8

# ---------- assets/example-project/project.yaml ----------
@'
slug: example-project
title: "Example SaaS Landing"
description: "Clean dark-mode SaaS marketing site for an AI scheduling tool."
url: "https://example-project.lovable.app"
lovable_prompts:
  - "Build a dark-themed SaaS landing page for an AI scheduling tool. Hero with animated gradient, 3-tier pricing, testimonials marquee, FAQ accordion."
images:
  - "hero.png"
  - "pricing.png"
  - "testimonials.png"
notes: "Replace with your real project. Drop screenshots in this folder."
'@ | Set-Content "$root\assets\example-project\project.yaml" -Encoding utf8

Write-Host ""
Write-Host "Created Loveable-UGC scaffold at $root" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  cd `"$root`""
Write-Host "  npm install"
Write-Host "  copy .env.example .env"
Write-Host "  notepad .env   # paste your ANTHROPIC_API_KEY"
Write-Host "  npm run schedule"
Write-Host ""
Write-Host "To push to GitHub:" -ForegroundColor Cyan
Write-Host "  git init -b main"
Write-Host "  git add ."
Write-Host "  git commit -m `"Initial scaffold`""
Write-Host "  git remote add origin https://github.com/jwebdesignservice/Loveable-UGC.git"
Write-Host "  git push -u origin main"
