'use strict';

const koa = require('koa');
const staticCache = require('koa-static-cache');
const formidable = require('koa-formidable');
const render = require('koa-ejs');
const path = require('path');
const ms = require('ms');
const chance = require('chance').Chance();
const objs = require('./objs.json');

const router = require('./router');
const app = koa();

app.use(staticCache({
  dir: path.join(__dirname, './static'),
  prefix: '/static',
  maxAge: ms('1y'),
  buffer: true,
  gzip: false,
}));

render(app, {
  root: path.join(__dirname, 'view'),
  layout: 'template',
  viewExt: 'html',
  cache: false,
  debug: true
});

app.use(formidable());

app.use(function* (next) {
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

  yield next;
});

require('./controllers');

router.router.post('/change', function () {
  const body = JSON.parse(this.request.body.data);
  io.emit('change', body.map((elm) => {
    const tmp = objs[elm.tag];
    tmp.score = elm.score;

    return tmp;
  }));
});

app.use(router.serverRouter);

const server = require('http').createServer(app.callback());
const io = require('socket.io')(server);

// socket.io
io.on('connection', function (socket) {
  console.log('one client connects.');
});

//aiServer
const aiServer = require('net').createServer(function (c) {
  c.on('data', function (data) {
    //emit
    io.emit('change', data);
  });
});
aiServer.listen(8124);

server.listen(8080);
console.log('listening on port 8080');