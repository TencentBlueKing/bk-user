
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

  // 降级到 es2015 时 esbuild 会在 chunk 顶层生成对象展开等 helper，异步 chunk 无函数包裹会被泄漏成 window 全局变量，
  // 各 chunk 独立分配的压缩短名互相覆盖会导致运行时报错（如 fg 同时是 Object.defineProperties 和 __spreadProps，
  // 使 @blueking/table 的列配置 slots 丢失、渲染报 reading 'header'），因此用 IIFE 包裹限制作用域。
  chainWebpack(config) {
    if (!config.optimization.minimizers.has('js')) {
      // 脚手架未按预期注册 minimizer 时直接失败，避免修复静默失效
      throw new Error('未找到 js minimizer，format: iife 未生效，请检查 @blueking/cli-service-webpack 版本');
    }
    config.optimization.minimizer('js').tap(([options]) => [{ ...options, format: 'iife' }]);
    return config;
  },
};
