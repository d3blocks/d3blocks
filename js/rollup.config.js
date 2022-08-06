import {nodeResolve} from '@rollup/plugin-node-resolve';

/**
 * @type {import('rollup').RollupOptions}
 */
const globalConfig = {
    plugins: [
        nodeResolve()
    ]
}

/**
 * @type {import('rollup').RollupOptions}
 */
const config = [
    {
        input: 'src/sankey/index.js',
        output: {
            file: '../d3blocks/sankey/d3js/sankey.js',
            format: 'iife'
        },
        ...globalConfig
    },
    {
        input: 'src/chord/index.js',
        output: {
            file: '../d3blocks/chord/d3js/chord.js',
            format: 'iife'
        },
        ...globalConfig
    }
];

module.exports = config;