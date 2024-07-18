import { Message } from 'bkui-vue';
import moment from 'moment';
import momentTimeZone from 'moment-timezone';
import { ref } from 'vue';

import abnormalImg from '@/images/abnormal.svg';
import loadingImg from '@/images/loading.svg';
import normalImg from '@/images/normal.svg';
import unknownImg from '@/images/unknown.svg';
import warningImg from '@/images/warning.svg';
import { t } from '@/language/index';
export * from './countryCode';

export const copy = (value: string) => {
  navigator.clipboard.writeText(value)
    .then(() => {
      Message({
        message: t('复制成功'),
        theme: 'success',
        delay: 1500,
      });
    })
    .catch(() => {
      Message({
        message: t('复制失败'),
        theme: 'error',
        delay: 1500,
      });
    });
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
      return t('永久');
    default:
      return value;
  }
}

// 时区获取
export const TIME_ZONES = momentTimeZone.tz.names()?.map(item => ({
  value: item,
  label: item
}))

// 语言
export const LANGUAGE_OPTIONS = [
  {value: 'zh-CN', label: '简体中文'},
  {value: 'en-US', label: 'English'}
]

// logo转换
export function logoConvert(value: string) {
  return value?.charAt(0).toUpperCase();
}

// 组织上级转换
export function formatConvert(value: any) {
  return value?.map(item => item.name || item.username).join(', ') || '--';
}

// 数据源启用状态
export const dataSourceStatus = {
  enabled: {
    icon: normalImg,
    text: t('正常'),
  },
  disabled: {
    icon: unknownImg,
    text: t('未启用'),
  },
  confirmed: {
    icon: warningImg,
    text: t('待确认'),
  },
  unconfirmed: {
    icon: warningImg,
    text: t('待确认'),
  },
};

export const validTime = {
  30: t('一个月'),
  90: t('三个月'),
  180: t('六个月'),
  365: t('一年'),
  '-1': t('永久'),
};

export function validTimeMap(value: number) {
  return validTime[value];
}

export const noticeTime = {
  1: t('1天前'),
  7: t('7天前'),
  15: t('15天前'),
};
export function noticeTimeMap(value: any) {
  const list: string[] = value?.map(key => noticeTime[key]).filter(Boolean) || [];
  return list.join('，');
};

export const notification = {
  email: t('邮箱'),
  sms: t('短信'),
};

export function notificationMap(value: any) {
  const list: string[] = value?.map(key => notification[key]).filter(Boolean) || [];
  return list.join('，');
};

export const passwordMustIncludes = {
  contain_lowercase: t('小写字母'),
  contain_uppercase: t('连续字母序'),
  contain_digit: t('数字'),
  contain_punctuation: t('特殊字符（除空格）'),
};

export function passwordMustIncludesMap(value: any) {
  const list: string[] = Object.entries(value)
    .filter(([key, val]) => passwordMustIncludes[key] && val)
    .map(([key]) => passwordMustIncludes[key]);
  return list.join('，');
};

export const passwordNotAllowed = {
  not_keyboard_order: t('键盘序'),
  not_continuous_letter: t('连续字母序'),
  not_continuous_digit: t('连续数字序'),
  not_repeated_symbol: t('重复字母、数字、特殊符号'),
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
    label: t('从不'),
  },
  {
    value: 30,
    label: t('每 30 分钟'),
  },
  {
    value: 60,
    label: t('每 1 小时'),
  },
  {
    value: 3 * 60,
    label: t('每 3 小时'),
  },
  {
    value: 6 * 60,
    label: t('每 6 小时'),
  },
  {
    value: 12 * 60,
    label: t('每 12 小时'),
  },
  {
    value: 24 * 60,
    label: t('每 1 天'),
  },
  {
    value: 7 * 24 * 60,
    label: t('每 7 天'),
  },
  {
    value: 30 * 24 * 60,
    label: t('每 30 天'),
  },
];

// 数据更新记录状态
export const dataRecordStatus = {
  pending: {
    icon: loadingImg,
    text: t('待执行'),
    theme: 'warning',
  },
  running: {
    icon: loadingImg,
    text: t('同步中'),
    theme: 'warning',
  },
  success: {
    icon: normalImg,
    text: t('成功'),
    theme: 'success',
  },
  failed: {
    icon: abnormalImg,
    text: t('失败'),
    theme: 'danger',
  },
};

// 有效期
export const VALID_TIME = [
  { days: 30, text: t('一个月') },
  { days: 90, text: t('三个月') },
  { days: 180, text: t('六个月') },
  { days: 365, text: t('一年') },
  { days: -1, text: t('永久') },
];

// 提醒时间
export const REMIND_DAYS = [
  { value: 1, label: t('1天前') },
  { value: 7, label: t('7天前') },
  { value: 15, label: t('15天前') },
];

// 通知方式
export const NOTIFICATION_METHODS = [
  { value: 'email', label: t('邮箱'), status: true },
  { value: 'sms', label: t('短信'), status: false },
];

// 自定义字段转换
export function customFieldsMap(item: any) {
  const fields = ref('');
  fields.value = item.value === '' ? '--'
    : item.data_type === 'enum' ? item.options?.find(option => option.id === item.value)?.value
      : item.data_type === 'multi_enum' ? item.value?.map(key => item.options?.find(option => option.id === key)?.value)
        .filter(Boolean)
        .join(', ')
        : item.value;
  return fields.value;
};

// 用户表格数据转换
export function getTableValue(row: any, item: any) {
  let val = '';
  if (Object.keys(row).length !== 0) {
    val = row[item.field] === '' ? '--'
      : item.data_type === 'enum' ? item.options?.find(option => option.id === row[item.field])?.value
        : item.data_type === 'multi_enum' ? row[item.field]?.map(key => item.options?.find(a => a.id === key)?.value)
          .filter(Boolean)
          .join(', ')
          : row[item.field];
  }
  return val;
};

// 数据源启用状态
export const tenantStatus = {
  enabled: {
    icon: normalImg,
    text: t('已启用'),
  },
  disabled: {
    icon: unknownImg,
    text: t('未启用'),
  },
};
