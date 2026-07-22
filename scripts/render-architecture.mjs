import { access } from "node:fs/promises";

await access(new URL("../architecture/system.mmd", import.meta.url));
console.log("Architecture source is present. Render it with the approved Mermaid renderer before publication and save the reviewed image under portfolio/assets/.");
