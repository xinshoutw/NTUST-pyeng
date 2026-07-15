import {defineCloudflareConfig} from "@opennextjs/cloudflare";

// ponytail: no incremental cache — app is SSR-only, no ISR/R2 needed.
// Add an incremental-cache override here if you introduce ISR later.
export default defineCloudflareConfig({});
