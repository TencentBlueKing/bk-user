import { defineStore } from 'pinia';
import type { IUser } from 'types/store';

export const useUser = defineStore('user', {
  state: () => ({
    user: {
      username: '',
      display_name: '',
      role: '',
      tenant_id: '',
    },
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
