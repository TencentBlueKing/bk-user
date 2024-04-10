import { h } from 'vue';

import { t } from '@/language/index';

// 重置数据源、删除租户前的确认信息
export const useInfoBoxContent = (data: any, type: string) => {
  const subContent = h('div', {
    style: {
      textAlign: 'left',
      lineHeight: '24px',
    },
  }, [
    h('p', {
      style: {
        marginBottom: '12px',
      },
    }, type === 'tenant' ? t('删除租户将导致以下数据被删除:') : t('重置将导致以下数据被删除:')),
    h('ul', [
      h('li', {
        style: {
          listStyle: 'disc',
          marginLeft: '18px',
          display: (data?.own_department_count
                || data?.own_user_count) > 0
            ? 'list-item'
            : 'none',
        },
      }, [
        t('本租户下的数据：共计'),
        h('span', { style: { margin: '0 4px' } }, data?.own_department_count),
        h('span', t('个组织，')),
        h('span', { style: { margin: '0 4px' } }, data?.own_user_count),
        h('span', t('个用户。')),
      ]),
      h('li', {
        style: {
          listStyle: 'disc',
          marginLeft: '18px',
          display: (data?.shared_to_tenant_count
                || data?.shared_to_department_count
                || data?.shared_to_user_count) > 0
            ? 'list-item'
            : 'none',
        },
      }, [
        type === 'tenant' ? t('本租户分享给其他租户的数据：涉及') : t('分享给其他租户的数据：涉及'),
        h('span', { style: { margin: '0 4px' } }, data?.shared_to_tenant_count),
        h('span', t('个租户，共计')),
        h('span', { style: { margin: '0 4px' } }, data?.shared_to_department_count),
        h('span', t('个组织，')),
        h('span', { style: { margin: '0 4px' } }, data?.shared_to_user_count),
        h('span', t('个用户。')),
      ]),
      h('li', {
        style: {
          listStyle: 'disc',
          marginLeft: '18px',
          display: (data?.shared_from_tenant_count
                || data?.shared_from_department_count
                || data?.shared_from_user_count) > 0
            ? 'list-item'
            : 'none',
        },
      }, [
        t('其他租户分享至本租户的数据：涉及'),
        h('span', { style: { margin: '0 4px' } }, data?.shared_from_tenant_count),
        h('span', t('个租户，共计')),
        h('span', { style: { margin: '0 4px' } }, data?.shared_from_department_count),
        h('span', t('个组织，')),
        h('span', { style: { margin: '0 4px' } }, data?.shared_from_user_count),
        h('span', t('个用户。')),
      ]),
    ]),
  ]);

  return { subContent };
};
