import css from "rollup-plugin-css-only";

export default {
    input: './src/main.js',
    output: {
        file: './build/bundle.min.js',
        format: 'iife',
        name: 'bundle'
    }
}