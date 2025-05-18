import eslintPluginPrettier from "eslint-plugin-prettier";
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import next from "eslint-plugin-next";

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  next.configs.recommended,
  {
    plugins: {
      prettier: eslintPluginPrettier,
    },
    rules: {
      "prettier/prettier": "error",
      "react/react-in-jsx-scope": "off",
    },
  },
];
