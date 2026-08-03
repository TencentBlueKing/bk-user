
const mockServer = require('./mock-server');

const isDesignPreview = process.env.BK_DESIGN_PREVIEW === 'true';

const localHttps = process.env.BK_HTTPS_KEY_PATH && process.env.BK_HTTPS_CERT_PATH
  ? {
    key: process.env.BK_HTTPS_KEY_PATH,
    cert: process.env.BK_HTTPS_CERT_PATH,
  }
  : true;

module.exports = {
  host: process.env.BK_APP_HOST,
  port: process.env.BK_APP_PORT,
  publicPath: process.env.BK_STATIC_URL,
  cache: !isDesignPreview,
  open: true,
  replaceStatic: true,
  outputDir: isDesignPreview ? 'dist-design-preview' : 'dist',
  outputAssetsDirName: '',
  https: localHttps,

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
