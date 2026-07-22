import { access, mkdir } from "node:fs/promises";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const exec = promisify(execFile);
const source = new URL("../architecture/system.mmd", import.meta.url);
const output = new URL("../portfolio/assets/system.png", import.meta.url);
await access(source);
await mkdir(new URL("../portfolio/assets/", import.meta.url), { recursive: true });
await exec("npx", ["--yes", "@mermaid-js/mermaid-cli", "-i", source.pathname, "-o", output.pathname, "-b", "transparent"]);
console.log(`Rendered ${output.pathname}`);
