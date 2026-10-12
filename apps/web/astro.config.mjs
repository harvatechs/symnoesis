import { defineConfig } from "astro/config";
import svelte from "@astrojs/svelte";

export default defineConfig({
  site: "https://harvatechs.github.io",
  base: "/symnoesis",
  output: "static",
  integrations: [svelte()],
});
