const CopyWebpackPlugin = require("copy-webpack-plugin");
const HTMLWebpackPlugin = require("html-webpack-plugin");

module.exports = {
    mode: "development",
    devServer: {
        static: "resources",
        port: 5178,
        host: "0.0.0.0",
        public: "lasagne.xyz"
    },
    module: {
        rules: [{
            test: /\.(png|jpg|gif)$/i,
            use: [
                {
                    loader: "url-loader",
                    options: {
                        limit: 8192,
                    },
                },
            ],
        }]
    },
    devtool: "inline-source-map",
    plugins: [
        new CopyWebpackPlugin({
            patterns: [{from: "resources/assets", to: "assets"}]
        }),
        new HTMLWebpackPlugin({
            template: "resources/index.html",
            filename: "index.html"
        })
    ]
};
