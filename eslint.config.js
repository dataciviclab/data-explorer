// ESLint flat config — see package.json "lint" script
import globals from "globals";

export default [
  {
    ignores: [
      "build/",
      "dist/",
      "node_modules/",
      "src/data/",
      "src/dataset/",
      "src/temi/",
      ".observablehq/",
    ],
  },
  {
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.node,
      },
    },
    rules: {
      // Error prevention
      "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
      "no-undef": "error",
      "no-cond-assign": "error",
      "no-dupe-keys": "error",
      "no-duplicate-case": "error",
      "no-empty": ["warn", { allowEmptyCatch: true }],
      "no-extra-boolean-cast": "warn",
      "no-irregular-whitespace": "error",
      "no-regex-spaces": "warn",
      "no-sparse-arrays": "error",
      "no-unreachable": "warn",
      "use-isnan": "error",
      "valid-typeof": "error",

      // Best practices
      "eqeqeq": ["error", "always"],
      "curly": ["warn", "multi-line"],
      "dot-notation": "warn",
      "no-eval": "error",
      "no-throw-literal": "error",
      "prefer-const": "warn",
      "no-var": "warn",
      "prefer-template": "warn",
    },
  },
];
