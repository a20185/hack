'use strict';

const router = require('koa-router')();

//TODO: 删除测试路由
router.get('/', function*() {
  this.body = 'Everything looks good.';
});

router.get('/w', function*() {
  console.log('----------------------------------------');
  console.log('[this.url]');
  console.log(this.url);
  console.log('[this.query]');
  console.log(this.query);
  console.log('[this.params]');
  console.log(this.params);
  console.log('[this.request.body]');
  console.log(this.request.body);
  console.log('[this.request.files]');
  console.log(this.request.files);
  console.log('---------------------------------------');

  this.body = 'Everything looks good.';
});

exports.router = router;
exports.serverRouter = router.routes();
