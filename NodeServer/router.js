'use strict';

const router = require('koa-router')();

//TODO: 删除测试路由
router.get('/', function*() {
  this.body = 'Everything looks good.';
});

exports.router = router;
exports.serverRouter = router.routes();
