import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypeScript from "eslint-config-next/typescript";

const eslintConfig = [
    {ignores: [".next/**", ".open-next/**", ".vercel/**", ".wrangler/**", "out/**", "build/**"]},
    ...nextCoreWebVitals,
    ...nextTypeScript,
    {
        rules: {
            "@next/next/no-html-link-for-pages": "off",
            // ponytail: react-hooks v7 (via eslint-config-next 16) newly flags
            // pre-existing mount-time cookie reads. Working code, perf nit only —
            // keep as warning, not a build-blocking error. Refactor if it matters.
            "react-hooks/set-state-in-effect": "warn",
        },
    },
];

export default eslintConfig;
