
const mockServer = require('./mock-server');

module.exports = {
  host: process.env.BK_APP_HOST,
  port: process.env.BK_APP_PORT,
  publicPath: process.env.BK_STATIC_URL,
  cache: true,
  open: true,
  replaceStatic: true,
  outputAssetsDirName: '',
  https: true,

  // webpack config 配置
  configureWebpack() {
    return {
      devServer: {
        setupMiddlewares: mockServer,
        proxy: [{
          '/api': {
            target: process.env.BK_AJAX_BASE_URL,
            changeOrigin: true,
            secure: false,
          },
        }],
        client: {
          overlay: false,
        },
      },
    };
  },
};
