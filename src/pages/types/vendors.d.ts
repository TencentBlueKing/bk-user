/**
 * 第三方库类型声明
 * 用于声明没有提供 TypeScript 类型定义的第三方包
 */

// @blueking/notice-component - 蓝鲸通知组件
declare module '@blueking/notice-component' {
  const NoticeComponent: any;
  export default NoticeComponent;
}

declare module '@blueking/notice-component/dist/style.css';

// @blueking/release-note - 蓝鲸版本日志组件
declare module '@blueking/release-note' {
  const ReleaseNote: any;
  export default ReleaseNote;
}

declare module '@blueking/release-note/vue3/vue3.css';
