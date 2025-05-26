import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    rules: {
      // Example rules to handle common errors
      "@typescript-eslint/no-unused-vars": "off",
      "react/react-in-jsx-scope": "off",
      "no-console": ["warn", { allow: ["warn", "error"] }],
      "react/prop-types": "off",
      "@typescript-eslint/no-explicit-any": "warn",
      "jsx-a11y/anchor-is-valid": "off",
    },
  },
];

export default eslintConfig;
