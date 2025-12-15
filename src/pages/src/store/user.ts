import { defineStore } from 'pinia';
import type { IUser } from 'types/store';

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
  },
});
