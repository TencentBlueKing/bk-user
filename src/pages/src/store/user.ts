import { defineStore } from 'pinia';
import type { IUser } from 'types/store';

export const useUser = defineStore('user', {
  state: () => ({
    user: {
      username: '',
      avatar_url: '',
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
