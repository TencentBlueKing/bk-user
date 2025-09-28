const fs = require('fs');
const path = require('path');

/**
 * @description 在不影响.bk.local.env的前提下，通过覆盖.bk.custom.env文件，实现自定义环境变量
 */
function envAssign() {
  const rootDir = process.cwd(); // 获取当前工作目录（项目根目录）
  const targetFileName = '.bk.custom.env';
  const targetFilePath = path.join(rootDir, targetFileName);

  if (fs.existsSync(targetFilePath)) {
    fs.unlinkSync(targetFilePath);
    console.log(`✅ Successfully remove ${targetFileName}`);
  }

  const envVersion = process.env?.npm_config_env;
  if (!envVersion) return;

  const sourceFileName = `.bk.local.${envVersion}.env`;
  const sourceFilePath = path.join(rootDir, sourceFileName);

  if (!fs.existsSync(sourceFilePath)) {
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

envAssign();
