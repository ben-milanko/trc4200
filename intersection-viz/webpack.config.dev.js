const CopyWebpackPlugin = require('copy-webpack-plugin')
const HTMLWebpackPlugin = require('html-webpack-plugin')

module.exports = {
    mode: 'development',
    devServer: {
        static: 'resources',
        port: 3000
    },
    devtool: 'inline-source-map',
    plugins: [
        new CopyWebpackPlugin({
            patterns: [
                {from: 'resources/assets', to: 'assets'}
            ]
        }),
        new HTMLWebpackPlugin({
            template: 'resources/index.html',
            filename: 'index.html'
        })
    ]
}