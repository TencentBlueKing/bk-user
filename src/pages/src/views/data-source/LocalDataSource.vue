<template>
  <div class="user-info-wrapper user-scroll-y">
    <header>
      <bk-dropdown trigger="click" placement="bottom-start">
        <bk-button theme="primary">
          <i class="user-icon icon-add-2 mr8" />
          新建数据源
        </bk-button>
        <template #content>
          <bk-dropdown-menu ext-cls="dropdown-menu-ul">
            <p class="dropdown-title">数据源类型选择</p>
            <bk-dropdown-item
              v-for="item in dropdownList"
              :key="item"
              @click="newDataSource(item)"
            >
              <i :class="item.icon"></i>
              <div class="dropdown-item">
                <span class="dropdown-item-title">{{ item.title }}</span>
                <span class="dropdown-item-subtitle">{{ item.subTitle }}</span>
              </div>
            </bk-dropdown-item>
          </bk-dropdown-menu>
        </template>
      </bk-dropdown>
      <bk-input
        class="header-right"
        v-model="searchVal"
        placeholder="搜索数据源名称"
        type="search"
      />
    </header>
    <bk-table
      class="user-info-table"
      :data="tableData"
      settings
      :border="['outer']"
      show-overflow-tooltip
    >
      <bk-table-column prop="name" label="数据源名称">
        <template #default="{ row }">
          <bk-button text theme="primary" @click="handleClick(row)">
            {{ row.name }}
          </bk-button>
        </template>
      </bk-table-column>
      <bk-table-column prop="type" label="数据源类型">
        <template #default="{ row }">
          <div>
            <i :class="[dataSourceType[row.type]?.icon, 'type-icon']" />
            <span>{{ dataSourceType[row.type]?.text }}</span>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column prop="status" label="状态">
        <template #default="{ row }">
          <div>
            <img :src="statusIcon[row.status]?.icon" class="account-status-icon" />
            <span>{{ statusIcon[row.status]?.text }}</span>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column prop="modified_by" label="更新人"></bk-table-column>
      <bk-table-column prop="modified_at" label="更新时间"></bk-table-column>
    </bk-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import router from '@/router/index';
import { dataSourceType, statusIcon } from '@/utils';

const searchVal = ref('');
const dropdownList = ref([
  {
    icon: 'user-icon icon-shujuku',
    title: '本地数据源',
    subTitle: '支持用户的增删改查，以及用户的登录认证',
    type: 'local',
  },
  // {
  //   icon: 'user-icon icon-win',
  //   title: 'Microsoft Active Directory',
  //   subTitle:
  //       '支持对接 Microsoft Active Directory，将用户信息同步到本地或者直接通过接口完成用户登录验证',
  //   type: 'mad',
  // },
  // {
  //   icon: 'user-icon icon-ladp',
  //   title: 'OpenLDAP',
  //   subTitle:
  //       '支持对接 OpenLDAP，将用户信息同步到本地或者直接通过接口完成用户登录验证',
  //   type: 'ldap',
  // },
  // {
  //   icon: 'user-icon icon-qiyeweixin',
  //   title: '企业微信',
  //   subTitle: '支持企业微信用户数据同步和登录认证',
  //   type: 'wechat',
  // },
]);

const tableData = [
  {
    name: '联通子公司正式员工',
    type: 'local',
    status: 'normal',
    modified_by: 'v_yutyi',
    modified_at: '2022-04-30  22:35:49',
  },
  {
    name: '企业内部',
    type: 'local',
    status: 'disabled',
    modified_by: 'v_yutyi',
    modified_at: '2022-04-30  22:35:49',
  },
];

function handleClick(item) {
  router.push({
    name: 'dataConfDetails',
    params: {
      name: item.name,
      type: item.type,
    },
  });
}
function newDataSource(item) {
  router.push({
    name: 'newLocal',
    params: {
      type: item.type,
    },
  });
}
</script>

<style lang="less" scoped>
.user-info-wrapper {
  width: 100%;
  height: calc(100vh - 140px);
  padding: 24px;

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .header-right {
      width: 400px;
    }
  }

  :deep(.user-info-table) {
    .bk-table-head {
      table thead th {
        text-align: center;
      }

      .table-head-settings {
        border-right: none;
      }
    }

    .bk-table-footer {
      padding: 0 15px;
      background: #fff;
    }

    .type-icon {
      margin-right: 8px;
      font-size: 14px;
      color: #979BA5;
    }

    .account-status-icon {
      width: 16px;
      height: 16px;
      margin-right: 5px;
      vertical-align: middle;
    }
  }
}

.dropdown-menu-ul {
  width: 380px;
  font-family: MicrosoftYaHei;

  .dropdown-title {
    padding: 12px 16px;
    color: #63656e;
  }

  .bk-dropdown-item {
    display: flex;
    height: 100%;
    padding: 10px 16px;
    line-height: 32px;
    align-items: center;

    .user-icon {
      font-size: 24px;
      color: #979ba5;
    }

    .dropdown-item {
      margin-left: 15px;

      span {
        display: block;
      }

      .dropdown-item-title {
        font-size: 14px;
        font-weight: 700;
      }

      .dropdown-item-subtitle {
        width: 300px;
        line-height: 20px;
        color: #979ba5;
        white-space: break-spaces;
      }
    }
  }
}
</style>
