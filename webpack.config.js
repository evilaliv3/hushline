const path = require('path');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

const entries = new Object();
modules = [
  // ours
  "client-side-encryption",
  "diceware-words",
  "directory",
  "directory_verified",
  "global",
  "inbox",
  "mailvelope",
  "message_success",
  "premium",
  "premium-waiting",
  "settings-fields",
  "settings",
  "submit-message",
  "vision",
  // dummies for css
  "style",
];

for (const mod_name of modules) {
  entries[mod_name] = `./assets/js/${mod_name}.js`
}

module.exports = (env) => {
  const isDev = env.WEBPACK_WATCH
  return {
    mode: isDev ? 'development' : 'production',
    entry: entries,
    output: {
      path: path.resolve(__dirname, 'hushline', 'static', 'js'),
      filename: '[name].js',
    },
    plugins: [
      new MiniCssExtractPlugin({
        filename: "../css/[name].css",
      }),
    ],
    module: {
      rules: [
        {
          test: /\.s[ca]ss$/,
          use: [
            {
              loader: MiniCssExtractPlugin.loader,
              options: {
                publicPath: '/static/css/',
              },
            },
            {
              loader: 'css-loader',
              options: {
                sourceMap: isDev,
              },
            },
            {
              loader: 'sass-loader',
              options: {
                sourceMap: isDev,
              },
            },
          ]
        },
        {
          test: /\.(woff(2)?|ttf|eot|svg)(\?.*)?$/,
          type: 'asset/resource',
          generator: {
            filename: '../fonts/[name][ext]',
          },
        },
        {
          test: /\.(png|svg|jpg|jpeg|gif)$/i,
          type: 'asset/resource',
          generator: {
            filename: '../img/[name][ext]',
          },
        },
      ],
    },
    performance: {
      // TODO figure out hot to chunk assets
      hints: false,
    },
  };
};
