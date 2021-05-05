const CopyWebpackPlugin = require('copy-webpack-plugin')
const HTMLWebpackPlugin = require('html-webpack-plugin')
const TerserWebpackPlugin = require('terser-webpack-plugin')

module.exports = {
    mode: 'production',
    module: {
        rules: [{
            test: /\.(js)$/,
            exclude: /node_modules/,
            use: {
                loader: 'babel-loader'
            }
        }]
    },
    optimization: {
        minimize: true,
        minimizer: [new TerserWebpackPlugin({
            terserOptions: {
                format: {
                    comments: false,
                },
            },
            extractComments: false,
        })]
    },
    plugins: [
        new CopyWebpackPlugin([{
            from: 'resources/assets',
            to: 'assets'
        }]),
        new HTMLWebpackPlugin({
            template: 'resources/index.html',
            filename: 'index.html',
            hash: true,
            minify: false
        })
    ]
}