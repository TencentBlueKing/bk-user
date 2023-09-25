// 获取 OA 登录用户详情
module.exports = async function user(req, res, next) {
  if (req.path !== '/api/user' && req.path !== '/user') {
    next();
    return;
  }
  const request = require('request');
  request(`http://login.o.oa.com/user/get_info?bk_ticket=${req.cookies.bk_ticket}`, (err, response, body) => {
    if (err) {
      return;
    }

    const loginURL = 'http://login.o.oa.com/plain?';

    const data = JSON.parse(body || '{}');

    // 有登录状态
    if (data.ret === 0) {
      const {
        username,
        avatar_url,
      } = data.data;
      res.json({
        code: 0,
        message: data.msg,
        data: {
          username,
          avatar_url,
        },
      });
      return;
    }
    // 登录状态失效
    res.status(401);
    res.set({
      'X-Login-Url': loginURL,
    });
    res.send('');
  });
};
