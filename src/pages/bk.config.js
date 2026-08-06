
const mockServer = require('./mock-server');

const isDesignPreview = process.env.BK_DESIGN_PREVIEW === 'true';

// 配置了 USE_HTTPS 时按数字开关决定是否启用 HTTPS（数字非 0 开启，0 及非数字值关闭）；未配置时走 BK_HTTPS_KEY_PATH/BK_HTTPS_CERT_PATH 逻辑
const localHttps = process.env.USE_HTTPS !== undefined
  ? Boolean(Number(process.env.USE_HTTPS))
  : process.env.BK_HTTPS_KEY_PATH && process.env.BK_HTTPS_CERT_PATH
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
