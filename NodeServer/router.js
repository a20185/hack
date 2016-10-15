'use strict';

const router = require('koa-router')();

//TODO: 删除测试路由
router.get('/', function*() {
  this.body = 'Everything looks good.';
});

router.get('/test', function*() {
  console.log('-----------------this.query--------------------');
  console.log(this.query);
  console.log('-----------------this.params--------------------');
  console.log(this.params);
  console.log('--------------this.request.body-----------------');
  console.log(this.request.body);
  console.log('--------------this.request.files-----------------');
  console.log(this.request.files);

  this.body = 'success';
});

exports.router = router;
exports.serverRouter = router.routes();
