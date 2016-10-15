'use strict';

const router = require('../router').router;

router.get('/hello', function*() {
  yield this.render('hello');
});