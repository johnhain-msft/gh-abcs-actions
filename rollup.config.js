import commonjs from "@rollup/plugin-commonjs";
import { nodeResolve } from "@rollup/plugin-node-resolve";

const config = {
  input: ".github/actions/hello-world-javascript-action/index.js",
  output: {
    esModule: true,
    file: ".github/actions/hello-world-javascript-action/dist/index.js",
    format: "es",
    sourcemap: true,
  },
  plugins: [commonjs(), nodeResolve({ preferBuiltins: true })],
};

export default config;
