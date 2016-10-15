const objs_en = require('./objs_en.json');
const objs_cn = require('./objs_cn.json');
const path = require('path');

const data = [];

for(let i = 0; i < 109; i++) {
  data.push({
    name: objs_en[i],
    name_cn: objs_cn[i],
    picFileName: objs_en[i] + '.jpeg'
  });
}

const fs = require('fs');

fs.writeFileSync(path.join(__dirname, './objs.json'), JSON.stringify(data, null, '  '));