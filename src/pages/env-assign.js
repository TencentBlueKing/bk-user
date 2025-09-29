const fs = require('fs');
const path = require('path');

/**
 * @description 通过覆盖.bk.local.env文件，实现自定义环境变量
 * @param {string} [defaultEnv='default'] - 默认环境名称，当没有指定env参数时使用
 */
function envAssign(defaultEnv = 'default') {
  const rootDir = process.cwd(); // 获取当前工作目录（项目根目录）
  const targetFileName = '.bk.local.env';
  const targetFilePath = path.join(rootDir, targetFileName);

  if (fs.existsSync(targetFilePath)) {
    fs.unlinkSync(targetFilePath);
    console.log(`✅ Successfully remove ${targetFileName}`);
  }

  // 获取环境参数，如果没有指定则使用默认环境
  const envVersion = process.env?.npm_config_env || defaultEnv;

  console.log(`🎯 Using environment: ${envVersion}`);

  const sourceFileName = `.bk.local.${envVersion}.env`;
  const sourceFilePath = path.join(rootDir, sourceFileName);

  if (!fs.existsSync(sourceFilePath)) {
    // 如果是默认环境文件不存在，给出友好提示
    if (envVersion === defaultEnv) {
      console.log(`ℹ️  Default environment file ${sourceFileName} not found, skipping env assignment`);
      return;
    }
    throw new Error(`${sourceFileName} is not found in ${rootDir}`);
  }

  try {
    const sourceContent = fs.readFileSync(sourceFilePath, 'utf8');
    fs.writeFileSync(targetFilePath, sourceContent, 'utf8');

    console.log(`✅ Successfully copied ${sourceFileName} to ${targetFileName}`);
    console.log(`📁 Source: ${sourceFilePath}`);
    console.log(`📁 Target: ${targetFilePath}`);
  } catch (error) {
    throw new Error(`Failed to copy file: ${error.message}`);
  }
};

// 执行函数，可以传入默认环境参数
envAssign('default');
