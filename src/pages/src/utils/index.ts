import { Message } from 'bkui-vue';
import moment from 'moment';

import abnormalImg from '@/images/abnormal.svg';
import loadingImg from '@/images/loading.svg';
import normalImg from '@/images/normal.svg';
import unknownImg from '@/images/unknown.svg';
import warningImg from '@/images/warning.svg';
export * from './countryCode';

export const statusIcon = {
  normal: {
    icon: normalImg,
    text: '正常',
  },
  disabled: {
    icon: unknownImg,
    text: '禁用',
  },
  locked: {
    icon: warningImg,
    text: '冻结',
  },
  delete: {
    icon: abnormalImg,
    text: '删除',
  },
};

export const copy = (value: string) => {
  const textArea = document.createElement('textarea');
  textArea.value = value;

  textArea.style.zIndex = '-99999';
  textArea.style.position = 'fixed';

  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    const res = document.execCommand('copy');
    if (res) {
      Message({
        message: '复制成功',
        theme: 'success',
        delay: 1500,
      });
      return;
    }
    throw new Error();
  } catch (e) {
    Message({
      message: '复制失败',
      theme: 'error',
      delay: 1500,
    });
  }
};

// file 转 base64
export const getBase64 = (file: any) => new Promise((resolve, reject) => {
  /// FileReader类就是专门用来读文件的
  const reader = new FileReader();
  // 开始读文件
  // readAsDataURL: dataurl它的本质就是图片的二进制数据， 进行base64加密后形成的一个字符串，
  reader.readAsDataURL(file);
  // 成功和失败返回对应的信息，reader.result一个base64，可以直接使用
  reader.onload = () => resolve(reader.result);
  // 失败返回失败的信息
  reader.onerror = error => reject(error);
});

// 无logo首字母色彩取值范围
export const LOGO_COLOR = [
  '#3A84FF', '#699DF4', '#18B456', '#51BE68', '#FF9C01', '#FFB848', '#EA3636', '#FF5656',
  '#3762B8', '#3E96C2', '#61B2C2', '#85CCA8', '#FFC685', '#FFA66B', '#F5876C', '#D66F6B',
];

// 日期转换
export function dateConvert(value: string) {
  value = moment.utc(value).format('YYYY-MM-DD');
  switch (value) {
    case null:
      return '--';
    case '2100-01-01':
      return '永久';
    default:
      return value;
  }
}

// logo转换
export function logoConvert(value: string) {
  return value?.charAt(0).toUpperCase();
}

// 组织上级转换
export function formatConvert(value: any) {
  return value?.map(item => item.name || item.username).join(' ; ') || '--';;
}

// 数据源启用状态
export const dataSourceStatus = {
  enabled: {
    icon: normalImg,
    text: '正常',
  },
  disabled: {
    icon: unknownImg,
    text: '未启用',
  },
};

export const validTime = {
  30: '一个月',
  90: '三个月',
  180: '六个月',
  365: '一年',
  '-1': '永久',
};

export function validTimeMap(value: number) {
  return validTime[value];
}

export const noticeTime = {
  1: '1天',
  7: '7天',
  15: '15天',
};
export function noticeTimeMap(value: any) {
  const list: string[] = value?.map(key => noticeTime[key]).filter(Boolean) || [];
  return list.join('，');
};

export const notification = {
  email: '邮箱',
  sms: '短信',
};

export function notificationMap(value: any) {
  const list: string[] = value?.map(key => notification[key]).filter(Boolean) || [];
  return list.join('，');
};

export const passwordMustIncludes = {
  contain_lowercase: '小写字母',
  contain_uppercase: '连续字母序',
  contain_digit: '数字',
  contain_punctuation: '特殊字符（除空格）',
};

export function passwordMustIncludesMap(value: any) {
  const list: string[] = Object.entries(value)
    .filter(([key, val]) => passwordMustIncludes[key] && val)
    .map(([key]) => passwordMustIncludes[key]);
  return list.join('，');
};

export const passwordNotAllowed = {
  not_keyboard_order: '键盘序',
  not_continuous_letter: '连续字母序',
  not_continuous_digit: '连续数字序',
  not_repeated_symbol: '重复字母、数字、特殊符号',
};

export function passwordNotAllowedMap(value: any) {
  const list: string[] = Object.entries(value)
    .filter(([key, val]) => passwordNotAllowed[key] && val)
    .map(([key]) => passwordNotAllowed[key]);
  return list.join('，');
};

// DOM 距离顶部的高度
export const getOffset = (target: HTMLElement) => {
  let totalLeft = 0;
  let totalTop = 0;
  let par = target.offsetParent as HTMLElement;
  totalLeft += target.offsetLeft;
  totalTop += target.offsetTop;
  while (par) {
    if (navigator.userAgent.indexOf('MSIE 8.0') === -1) {
      // 不是IE8我们才进行累加父级参照物的边框
      totalTop += par.clientTop;
      totalLeft += par.clientLeft;
    }
    totalTop += par.offsetTop;
    totalLeft += par.offsetLeft;
    par = par.offsetParent as HTMLElement;
  }
  return { left: totalLeft, top: totalTop };
};

// 表格根据页面高度自适应每页显示数量
export const currentLimit = (top: number, pagination: any, rowHeight?: number) => {
  const windowInnerHeight = window.innerHeight;
  const tableHeaderHeight = 42;
  const paginationHeight = 60;
  const pageOffsetBottom = 24;
  const tableRowHeight = rowHeight ? rowHeight : 42;

  const tableRowTotalHeight = windowInnerHeight - top - tableHeaderHeight - paginationHeight - pageOffsetBottom;

  const rowNum = Math.max(Math.floor(tableRowTotalHeight / tableRowHeight), 2);
  const pageLimit = new Set([
    ...pagination.limitList,
    rowNum,
  ]);
  const list = [...pageLimit].sort((a, b) => a - b);
  return { list, rowNum };
};

// 同步周期
export const SYNC_CONFIG_LIST = [
  {
    value: 0,
    label: '从不',
  },
  {
    value: 30,
    label: '每 30 分钟',
  },
  {
    value: 60,
    label: '每 1 小时',
  },
  {
    value: 3 * 60,
    label: '每 3 小时',
  },
  {
    value: 6 * 60,
    label: '每 6 小时',
  },
  {
    value: 12 * 60,
    label: '每 12 小时',
  },
  {
    value: 24 * 60,
    label: '每 1 天',
  },
  {
    value: 7 * 24 * 60,
    label: '每 7 天',
  },
  {
    value: 30 * 24 * 60,
    label: '每 30 天',
  },
];

// 数据更新记录状态
export const dataRecordStatus = {
  pending: {
    icon: loadingImg,
    text: '待执行',
    theme: 'warning',
  },
  running: {
    icon: loadingImg,
    text: '同步中',
    theme: 'warning',
  },
  success: {
    icon: normalImg,
    text: '成功',
    theme: 'success',
  },
  failed: {
    icon: abnormalImg,
    text: '失败',
    theme: 'danger',
  },
};

// 有效期
export const VALID_TIME = [
  { days: 30, text: '一个月' },
  { days: 90, text: '三个月' },
  { days: 180, text: '六个月' },
  { days: 365, text: '一年' },
  { days: -1, text: '永久' },
];

// 提醒时间
export const REMIND_DAYS = [
  { value: 1, label: '1天' },
  { value: 7, label: '7天' },
  { value: 15, label: '15天' },
];

// 通知方式
export const NOTIFICATION_METHODS = [
  { value: 'email', label: '邮箱', status: true },
  { value: 'sms', label: '短信', status: false },
];
