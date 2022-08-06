import { nodeResolve } from '@rollup/plugin-node-resolve';

/**
 * @type {import('rollup').RollupOptions}
 */
const config = {
    input: 'src/sankey/index.js',
    output: {
        file: '../d3blocks/sankey/d3js/sankey.js',
        format: 'iife'
    },
    plugins: [
        nodeResolve()
    ]

};

module.exports = config;