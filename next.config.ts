import type {NextConfig} from "next";
import {initOpenNextCloudflareForDev} from "@opennextjs/cloudflare";

const nextConfig: NextConfig = {};

export default nextConfig;

// Enable Cloudflare bindings (R2, KV, etc.) during `next dev`.
initOpenNextCloudflareForDev();
