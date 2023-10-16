module.exports = (middlewares, devServer) => {
  devServer.app.use(require('cookie-parser')());
  /** mock 接口 */
  require('../paas-server/api/table')(devServer.app);
  return middlewares;
};
