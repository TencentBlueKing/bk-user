/**
 * ESLint 自定义规则：禁止使用硬编码的角色值
 *
 * 该规则会检测代码中是否直接使用了 ROLE 常量对应的 value 值
 * 而不是使用 ROLE.SUPER_MANAGER, ROLE.TENANT_MANAGER, ROLE.NATURAL_USER 常量
 */

const path = require('path');
const fs = require('fs');

// 动态读取 ROLE 常量定义
function getRoleMapping() {
  try {
    const constantPath = path.resolve(__dirname, '../src/common/constant.ts');
    const content = fs.readFileSync(constantPath, 'utf-8');

    // 解析 ROLE 对象
    const roleRegex = /export const ROLE = \{([^}]+)\}/s;
    const match = content.match(roleRegex);

    if (!match) {
      return {};
    }

    const roleContent = match[1];
    const mapping = {};

    // 解析每个角色定义：SUPER_MANAGER: 'super_manager'
    const rolePattern = /(\w+):\s*['"]([^'"]+)['"]/g;
    let roleMatch;

    while ((roleMatch = rolePattern.exec(roleContent)) !== null) {
      const [, key, value] = roleMatch;
      mapping[value] = key;
    }

    return mapping;
  } catch (error) {
    console.error('Failed to load ROLE constants:', error);
    return {};
  }
}

module.exports = {
  meta: {
    type: 'suggestion',
    docs: {
      description: '禁止使用硬编码的角色值，应使用 ROLE 常量',
      category: 'Best Practices',
      recommended: true,
    },
    messages: {
      useRoleConstant: '不要使用硬编码的角色值 "{{value}}"，请使用 ROLE.{{constant}} 常量',
    },
    fixable: 'code',
    schema: [],
  },

  create(context) {
    // 从 constant.ts 动态获取角色值映射
    const roleMapping = getRoleMapping();

    return {
      // 检测字面量字符串
      Literal(node) {
        // 只检查字符串类型的字面量
        if (typeof node.value !== 'string') {
          return;
        }

        const { value } = node;

        // 检查是否是角色值
        if (roleMapping[value]) {
          context.report({
            node,
            messageId: 'useRoleConstant',
            data: {
              value,
              constant: roleMapping[value],
            },
            fix(fixer) {
              // 自动修复：将硬编码的字符串替换为 ROLE 常量
              return fixer.replaceText(node, `ROLE.${roleMapping[value]}`);
            },
          });
        }
      },
    };
  },
};

// 导出 getRoleMapping 函数供 .eslintrc.js 使用
module.exports.getRoleMapping = getRoleMapping;
