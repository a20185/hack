'use strict';

const router = require('../router').router;

router.get('/hello', function*() {
  yield this.render('hello');
});

router.get('/test', function*() {
  yield this.render('test');
});