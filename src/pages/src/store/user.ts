import { defineStore } from 'pinia';
import type { IUser } from 'types/store';

import BkUserDisplayName from '@blueking/bk-user-display-name';

import { ROLE } from '@/common/constant';
import { currentUser, getBuiltinManager } from '@/http';
import { BuiltinManagerData } from '@/http/types/settingFiles';

export const useUser = defineStore('user', {
  state: () => ({
    user: {
      username: '',
      display_name: '',
      role: '',
      tenant_id: '',
    },
    admin: {} as BuiltinManagerData,
    showAlert: false, // 消息通知显示状态
  }),
  actions: {
    setUser(user: IUser) {
      this.user = user;
    },
    setShowAlert(status: boolean) {
      this.showAlert = status;
    },
    /**
     * 初始化用户信息
     * DisplayName组件数据初始化
     */
    async initUserInfo() {
      const res = await currentUser();
      this.user = res.data;
      const { role, tenant_id } = res.data;
      BkUserDisplayName.configure({
        tenantId: tenant_id,
        apiBaseUrl: window.BK_USER_WEB_APIGW_URL,
      });
      // 角色为租户管理员或内置管理员时
      if (role === ROLE.SUPER_MANAGER || role === ROLE.TENANT_MANAGER) {
        this.initAdmin();
      }
    },
    async initAdmin() {
      const res = await getBuiltinManager();
      this.admin = res?.data;
    },
  },
});
