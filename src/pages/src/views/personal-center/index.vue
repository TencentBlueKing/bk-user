<template>
  <bk-resize-layout
    class="personal-center-wrapper"
    immediate
    :min="320"
    :max="500"
    :initial-divide="320"
  >
    <template #aside>
      <div class="personal-center-left">
        <div class="left-search">
          <bk-input />
        </div>
        <div class="left-add">
          <p>
            <span class="account">已关联账号</span>
            <span class="number">2</span>
          </p>
          <bk-button theme="primary" text>
            <i class="user-icon icon-add-2 mr8" />
            新增关联
          </bk-button>
        </div>
        <ul class="left-list">
          <li
            :class="{ isActive: state.activeIndex === index }"
            v-for="(item, index) in accountList"
            :key="index"
            @click="handleClickItem(item, index)"
          >
            <div class="account-item">
              <div>
                <img v-if="item.logo" :src="item.logo" />
                <img v-else src="@/images/avatar.png" />
                <span class="name">{{ item.name }}</span>
                <span class="tenant">{{ item.tenant }}</span>
              </div>
              <bk-tag type="filled" theme="success" v-if="item.state">
                当前登录
              </bk-tag>
            </div>
          </li>
        </ul>
      </div>
    </template>
    <template #main>
      <div class="personal-center-main">
        <header>
          <div class="header-left">
            <img v-if="state.item.logo" :src="state.item.logo" />
            <img v-else src="@/images/avatar.png" />
            <div>
              <p class="name">
                {{ state.item.name }}
                <bk-tag>
                  local-test
                </bk-tag>
              </p>
              <p class="login-time">最近登录时间：2023-03-05 21:09:35</p>
            </div>
          </div>
          <div class="header-right">
            <bk-popover
              content="该账号已登录"
              placement="top"
              :disabled="!state.item.state"
            >
              <bk-button :disabled="state.item.state">
                切换为该账号登录
              </bk-button>
            </bk-popover>
            <bk-button>
              取消关联
            </bk-button>
          </div>
        </header>
        <div class="details-info-wrapper">
          <ul class="details-info-content">
            <li class="content-item">
              <div class="item-header">
                <p class="item-title">身份信息</p>
                <bk-button outline theme="primary" @click="handleClickEdit">
                  编辑
                </bk-button>
              </div>
              <ul class="item-content flex">
                <li v-for="(item, index) in state.idInfo" :key="index">
                  <span class="key">{{ dataMap[item.key] }}：</span>
                  <span class="value">{{ item.value }}</span>
                </li>
              </ul>
            </li>
            <li class="content-item">
              <div class="item-header">
                <p class="item-title">个人社交账号</p>
              </div>
              <ul class="item-content ">
                <li></li>
              </ul>
            </li>
            <li class="content-item">
              <div class="item-header">
                <p class="item-title">MFA设置</p>
              </div>
              <ul class="item-content">
                <li>
                  <span class="key"></span>
                  <span class="value"></span>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </template>
  </bk-resize-layout>
</template>

<script setup lang="ts">
import { reactive } from 'vue';

const accountList = reactive([
  {
    logo: '',
    name: 'Eric Lee',
    tenant: '@ 默认租户',
    state: true,
  },
  {
    logo: '',
    name: 'Eric Li',
    tenant: '@ loca-test',
    state: false,
  },
  {
    logo: '',
    name: 'Eric',
    tenant: '@ 移动分公司',
    state: false,
  },
  {
    logo: '',
    name: 'Eric Lee',
    tenant: '@ 苏州研究所',
    state: false,
  },
]);

const dataMap = {
  username: '用户名',
  tenant_id: '所属租户ID',
  full_name: '全名',
  department: '所属组织',
  email: '邮箱',
  leader: '直属上级',
  phone: '手机号',
  job: '职务',
};
const state = reactive({
  activeIndex: 0,
  item: {},
  idInfo: [
    {
      key: 'username',
      value: '张三',
    },
    {
      key: 'tenant_id',
      value: 'test',
    },
    {
      key: 'full_name',
      value: '张三',
    },
    {
      key: 'department',
      value: '总公司',
    },
    {
      key: 'email',
      value: '123@qq.com',
    },
    {
      key: 'leader',
      value: '李四',
    },
    {
      key: 'phone',
      value: '13122334455',
    },
    {
      key: 'job',
      value: '产品经理',
    },
  ],
});

const handleClickItem = (item, index) => {
  state.item = item;
  state.activeIndex = index;
};
handleClickItem(accountList[0], 0);
</script>

<style lang="less" scoped>
@import url("@/css/tenantViewStyle.less");

.personal-center-wrapper {
  width: 100%;
  height: calc(100vh - 52px);

  .personal-center-left {
    height: 100%;
    background-color: #fff;

    .left-search {
      padding: 16px;

      :deep(.bk-input) {
        height: 40px;
        line-height: 40px;
        border: none;

        .bk-input--text {
          background-color: #f0f1f5;
        }
      }
    }

    .left-add {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 16px 16px;

      .account {
        margin-right: 8px;
        font-size: 14px;
      }

      .number {
        display: inline-block;
        height: 16px;
        padding: 0 8px;
        line-height: 16px;
        color: #979ba5;
        text-align: center;
        background: #f0f1f5;
        border-radius: 8px;
      }

      .bk-button {
        font-size: 14px;
      }
    }

    .left-list {
      li {
        padding: 0 12px 0 24px;

        &:hover {
          background: #f0f1f5;
        }

        .account-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          height: 40px;
          line-height: 40px;
          cursor: pointer;

          img {
            width: 22px;
            height: 22px;
            vertical-align: middle;
            object-fit: contain;
          }

          .name {
            display: inline-block;
            margin: 0 8px;
            font-family: MicrosoftYaHei;
            font-size: 14px;
            color: #313238;
          }

          .tenant {
            color: #ff9c01;
          }
        }
      }

      .isActive {
        background-color: #e1ecff;
      }
    }
  }

  .personal-center-main {
    padding: 24px;

    header {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .header-left {
        display: flex;

        img {
          width: 72px;
          height: 72px;
          object-fit: contain;
          margin-right: 16px;
        }

        .name {
          font-family: MicrosoftYaHei-Bold;
          font-size: 32px;
          font-weight: 700;

          .bk-tag {
            font-weight: 400;
          }
        }

        .login-time {
          font-size: 14px;
        }
      }
    }
  }
}
</style>
