/**
* by making 蓝鲸智云-用户管理(Bk-User) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License");
* you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and limitations under the License.
*/
// eslint-disable-next-line no-unused-vars
export async function response(getArgs, postArgs, req) {
  // 所有 mock 接口延时 500ms
  await new Promise((resolve) => {
    setTimeout(() => {
      resolve();
    }, 500);
  });

  const invoke = getArgs.invoke;
  // 获取目录列表
  if (invoke === 'ajaxPostCatalog') {
    return {
      code: 0,
      result: true,
      message: 'success',
      data: {
        id: Math.ceil(Math.random() * 100000),
        display_name: '企业内部AD',
        type: 'mad',
        update_time: '2018-12-16 22:56:21',
        enable: true,
      },
    };
  } if (invoke === 'ajaxGetCatalogList') {
    return {
      code: 0,
      result: true,
      message: 'success',
      data: [
        {
          id: '1',
          display_name: '企业内部AD',
          type: 'mad',
          update_time: '2018-12-16 22:56:21',
          enable: true,
        }, {
          id: '2',
          display_name: 'OpenLDAP',
          type: 'ldap',
          update_time: '2018-12-16 22:56:21',
          enable: false,
        }, {
          id: '3',
          display_name: '广东分公司',
          type: 'custom',
          update_time: '2018-12-16 22:56:21',
          enable: true,
        }, {
          id: '4',
          display_name: '合作伙伴',
          type: 'local',
          update_time: '2018-12-16 22:56:21',
          enable: true,
        },
      ],
    };
  } if (invoke === 'ajaxGetCatalog') {
    return {
      code: 0,
      result: true,
      message: 'success',
      data: {
        display_name: 'fake',
        domain: 'fake',
        enable: true,
      },
    };
  } if (invoke === 'ajaxGetPassport') {
    return {
      code: 0,
      result: true,
      message: 'success',
      data: [
        {
          key: 'password_min_length',
          value: 8,
          region: 'default',
        }, {
          key: 'password_must_includes',
          value: ['upper', 'lower', 'int'],
          region: 'default',
        }, {
          key: 'password_valid_days',
          value: 30,
          region: 'default',
        }, {
          key: 'max_trail_times',
          value: 3,
          region: 'default',
        }, {
          key: 'auto_unlock_seconds',
          value: 600,
          region: 'default',
        }, {
          key: 'init_password_method',
          value: 'fixed_preset',
          region: 'default',
        }, {
          key: 'init_password',
          value: 'Bk@123456',
          region: 'default',
        }, {
          key: 'init_mail_config',
          value: { title: '1', sender: '1', content: '1' },
          region: 'default',
        }, {
          key: 'reset_mail_config',
          value: { title: '1', sender: '1', content: '1' },
          region: 'default',
        }, {
          key: 'force_reset_first_login',
          value: true,
          region: 'default',
        }, {
          key: 'enable_auto_freeze',
          value: true,
          region: 'default',
        }, {
          key: 'freeze_after_days',
          value: 180,
          region: 'default',
        },
      ],
    };
  } if (invoke === 'ajaxGetConnection') {
    return {
      code: 0,
      result: true,
      message: 'success',
      data: [
        {
          key: 'connection_url',
          value: 'ldap://localhost:389/',
          region: 'default',
        }, {
          key: 'ssl_encryption',
          value: 'SSL',
          region: 'default',
        }, {
          key: 'ssl_encryption_list',
          value: ['none', 'SSL'],
          region: 'default',
        }, {
          key: 'timeout_setting',
          value: 120,
          region: 'default',
        }, {
          key: 'pull_cycle',
          value: 60,
          region: 'default',
        }, {
          key: 'base_dn',
          value: 'xxx',
          region: 'default',
        }, {
          key: 'username',
          value: 'xxx',
          region: 'default',
        }, {
          key: 'password',
          value: 'xxx',
          region: 'default',
        },
      ],
    };
  } if (invoke === 'ajaxGetFields') {
    return {
      code: 0,
      result: true,
      message: 'success',
      data: [
        {
          key: 'basic_pull_node',
          value: '假数据',
          region: 'basic',
        }, {
          key: 'basic_pull_node_list',
          value: ['我', '是', '假数据'],
          region: 'basic',
        }, {
          key: 'user_class',
          value: 'user',
          region: 'basic',
        }, {
          key: 'user_filter',
          value: '(&(objectCategory=Person)(sAMAccountName=*))',
          region: 'basic',
        }, {
          key: 'organization_class',
          value: 'organizationalUnit',
          region: 'basic',
        }, {
          key: 'account_name',
          value: 'sAMAccountName',
          region: 'basic',
        }, {
          key: 'username',
          value: 'cn',
          region: 'basic',
        }, {
          key: 'display_name',
          value: 'displayName',
          region: 'basic',
        }, {
          key: 'email',
          value: 'mail',
          region: 'basic',
        }, {
          key: 'telephone',
          value: 'Telephone',
          region: 'basic',
        }, {
          key: 'bk_fields',
          value: ['职务', '性别', '年龄', '工作年限', '婚姻状态', '籍贯'],
          region: 'extend',
        }, {
          key: 'mad_fields',
          value: ['', '', '', '', '', ''],
          region: 'extend',
        }, {
          // 上面两个数组按顺序对应，这个数组顺序无所谓
          key: 'mad_fields_list',
          value: ['job', 'gender', 'age', 'year', 'marry', 'home'],
          region: 'extend',
        }, {
          key: 'group_pull_node',
          value: '假数据',
          region: 'group',
        }, {
          key: 'group_pull_node_list',
          value: ['我', '是', '假数据'],
          region: 'group',
        }, {
          key: 'user_group_lass',
          value: 'groupOfUniqueNames',
          region: 'group',
        }, {
          key: 'user_group_filter',
          value: '(objectclass=groupOfUniqueNames)',
          region: 'group',
        }, {
          key: 'user_group_name',
          value: 'cn',
          region: 'group',
        }, {
          key: 'user_group_description',
          value: 'description',
          region: 'group',
        }, {
          key: 'user_group_member',
          value: 'uniqueMember',
          region: 'group',
        },
      ],
    };
  } if (invoke === 'ajaxTestConnection') {
    return {
      code: 0,
      result: Math.random() > 0.5,
      message: 'success',
      data: {},
    };
  } if (invoke === 'ajaxGetDefaultPassport') {
    // default 实际返回的对象数组 region，跟上面一样，这里暂时 mock 使用
    return {
      code: 0,
      result: true,
      message: 'success',
      data: {
        default: {
          // 密码长度
          password_min_length: 8,
          // 密码规则
          password_must_includes: ['upper', 'lower', 'int'],
          // 密码有效期 30 90 180 365 0 对应 一个月 三个月 六个月 一年 永久
          password_valid_days: 30,
          // 密码试错次数 有效值 3 5 10
          max_trail_times: 3,
          // 密码解锁时间
          auto_unlock_seconds: 600,
          // 初始密码获取方式 'fixed_preset' 或者 'random_via_mail'
          init_password_method: 'fixed_preset',
          init_password: 'Bk@123456',
          // 邮件相关配置
          init_mail_config: {
            title: '蓝鲸智云企业版 - 您的账户已经成功创建！',
            sender: '蓝鲸智云企业版',
            content: '您好！您的蓝鲸智云企业版账户已经成功创建，以下是您的账户信息:登录账户：{username}， 初始登录密码：{password} 为了保障账户安全，我们建议您尽快登录蓝鲸智云企业版修改密码：{url} 此邮件为系统自动发送，请勿回复。蓝鲸智云官网： http://bk.tencent.com',
          },
          reset_mail_config: {
            title: '蓝鲸智云企业版 - 登录密码重置',
            sender: '蓝鲸智云企业版',
            content: '您好！我们收到了你重置密码的申请，请点击下方链接进行密码重置：{url} 该链接有效时间为3小时，过期后请重新点击密码重置链接：{reset_url} 此邮件为系统自动发送，请勿回复',
          },
          // 首次登录强制修改密码
          force_reset_first_login: true,
          // 连续xx天未登录冻结
          enable_auto_freeze: true,
          freeze_after_days: 180,
        },
      },

    };
  } if (invoke === 'ajaxGetDefaultConnection') {
    return {
      code: 0,
      result: true,
      message: 'success',
      data: {
        default: {
          // 连接地址
          connection_url: '',
          // SSL加密方式
          ssl_encryption: 'SSL',
          ssl_encryption_list: ['none', 'SSL'],
          // 超时设置
          timeout_setting: 120,
          // 拉取周期
          pull_cycle: 60,
          // 根目录
          base_dn: '',
          // 用户名
          username: '',
          // 密码
          password: '',
        },
      },
    };
  } if (invoke === 'ajaxGetDefaultFields') {
    return {
      code: 0,
      result: true,
      message: 'success',
      data: {
        // 基础字段
        basic: {
          // 选择拉取节点
          basic_pull_node: '',
          basic_pull_node_list: ['我', '是', '假数据'],
          // 用户对象类
          user_class: 'user',
          // 用户对象过滤
          user_filter: '(&(objectCategory=Person)(sAMAccountName=*))',
          // 组织架构类
          organization_class: 'organizationalUnit',
          // 账户名字段
          account_name: 'sAMAccountName',
          // 用户名字段
          username: 'cn',
          // 展示名字段
          display_name: 'displayName',
          // 邮箱字段
          email: 'mail',
          // 手机号字段
          telephone: 'Telephone',
        },
        // 用户扩展字段
        extend: {
          bk_fields: ['职务', '性别', '年龄', '工作年限', '婚姻状态', '籍贯'],
          mad_fields: ['', '', '', '', '', ''],
          mad_fields_list: ['job', 'gender', 'age', 'year', 'marry', 'home'],
        },
        // 用户组字段
        group: {
          // 选择拉取节点
          group_pull_node: '',
          group_pull_node_list: ['我', '是', '假数据'],
          // 用户组对象类
          user_group_lass: 'groupOfUniqueNames',
          // 用户组对象过滤
          user_group_filter: '(objectclass=groupOfUniqueNames)',
          // 用户组名字段
          user_group_name: 'cn',
          // 用户组描述字段
          user_group_description: 'description',
          // 用户组成员字段
          user_group_member: 'uniqueMember',
        },
      },

    };
  } if (invoke === '') {
    return {
      code: 0,
      result: true,
      message: 'success',
      data: {},
    };
  }
  return {
    code: 0,
    result: true,
    message: 'success',
    data: {},
  };
}
