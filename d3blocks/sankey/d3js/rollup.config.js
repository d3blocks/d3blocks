import { nodeResolve } from '@rollup/plugin-node-resolve';

/**
 * @type {import('rollup').RollupOptions}
 */
const config = {
    input: 'src/sankey/index.js',
    output: {
        file: 'bundle/sankey.js',
        format: 'iife'
    },
    plugins: [
        nodeResolve()
    ]

};

module.exports = config;