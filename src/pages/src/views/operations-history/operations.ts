import { t } from '@/language/index';

// 若有增加操作对象及操作类型的对应关系，可在operationMap及operationType进行补充
export const operationMap = {
  data_source: {
    create_data_source: t('创建数据源'),
    modify_data_source: t('修改数据源'),
    delete_data_source: t('删除数据源'),
    sync_data_source: t('同步数据源'),
  },
  idp: {
    create_idp: t('创建认证源'),
    modify_idp: t('修改认证源'),
    modify_idp_status: t('修改认证源状态'),
    delete_idp: t('删除认证源'),
  },
  data_source_user: {
    create_data_source_user: t('创建数据源用户'),
    create_user_leader: t('创建用户-上级关系'),
    create_user_department: t('创建用户-部门关系'),

    modify_data_source_user: t('修改数据源用户'),
    modify_user_leader: t('修改用户-上级关系'),
    modify_user_department: t('修改用户-部门关系'),
    modify_user_password: t('修改用户密码'),

    delete_data_source_user: t('删除数据源用户'),
    delete_user_leader: t('删除用户-上级关系'),
    delete_user_department: t('删除用户-部门关系'),
  },
  tenant_user: {
    create_tenant_user: t('创建租户用户'),
    create_collaboration_tenant_user: t('创建协同租户用户'),

    modify_tenant_user: t('修改租户用户'),
    modify_user_status: t('修改用户状态'),
    modify_user_account_expired_at: t('修改用户账号过期时间'),
    modify_user_email: t('修改用户邮箱'),
    modify_user_phone: t('修改用户电话号码'),

    delete_tenant_user: t('删除租户用户'),
    delete_collaboration_tenant_user: t('删除协同租户用户'),
  },
  data_source_department: {
    create_data_source_department: t('创建数据源部门'),
    create_parent_department: t('创建部门-父部门关系'),

    modify_data_source_department: t('修改数据源部门'),
    modify_parent_department: t('修改部门-父部门关系'),

    delete_data_source_department: t('删除数据源部门'),
    delete_parent_department: t('删除部门-父部门关系'),
  },
  tenant_department: {
    create_tenant_department: t('创建租户部门'),
    create_collaboration_tenant_department: t('创建协同租户部门'),

    modify_tenant_department: t('修改租户部门'),
    delete_tenant_department: t('删除租户部门'),

    delete_collaboration_tenant_department: t('删除协同租户部门'),
  },
  tenant: {
    create_tenant: t('创建租户'),
    create_tenant_real_manager: t('创建租户实名管理员'),

    modify_tenant: t('修改租户信息'),
    modify_tenant_status: t('修改租户状态'),
    modify_tenant_account_validity_period_config: t('修改租户账户有效期配置'),

    delete_tenant: t('删除租户'),
    delete_tenant_real_manager: t('删除租户实名管理员'),
  },
  virtual_user: {
    create_virtual_user: t('创建虚拟用户'),
    modify_virtual_user: t('修改虚拟用户'),
    delete_virtual_user: t('删除虚拟用户'),
  },
};

// eslint-disable-next-line @typescript-eslint/naming-convention
export const operationType = [
  {
    key: 'data_source',
    label: t('数据源'),
  },
  {
    key: 'idp',
    label: t('认证源'),
  },
  {
    key: 'data_source_user',
    label: t('数据源用户'),
  },
  {
    key: 'tenant_user',
    label: t('租户用户'),
  },
  {
    key: 'data_source_department',
    label: t('数据源部门'),
  },
  {
    key: 'tenant_department',
    label: t('租户部门'),
  },
  {
    key: 'tenant',
    label: t('租户'),
  },
  {
    key: 'virtual_user',
    label: t('虚拟用户'),
  },
];

// 展开operationMap子项，获取操作类型所有下拉项
export const getCurrentOperationOptions = () => Object
  .entries(operationMap)
  .flatMap(([relyKey, actions]) => Object.entries(actions).map(([key, label]) => ({ key, label, relyKey })));
