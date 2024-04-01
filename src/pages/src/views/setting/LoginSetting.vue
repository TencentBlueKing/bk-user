<template>
  <div class="login-setting-wrapper user-scroll-y">
    <ul class="login-setting-content">
      <li class="item-box">
        <div class="header">
          <p>{{ $t('基本登录方式') }}</p>
        </div>
        <div class="login-box">
          <div
            class="login-item"
            v-for="(item, index) in loginMethods"
            :key="index">
            <div
              :class="[
                'login-content',
                item.status,
              ]">
              <div
                class="name"
                v-bk-tooltips="{
                  content: $t('暂未配置'),
                  disabled: item.status !== 'not',
                }"
                @click="handleClickActive(item)">
                <i :class="item.logo" />
                <span>{{ item.name }}</span>
                <bk-tag
                  v-if="item.type === 'local'"
                  type="stroke"
                  theme="info"
                >
                  {{ $t('本地') }}
                </bk-tag>
              </div>
              <bk-tag
                v-if="item.status === 'enable'"
                class="status-tag"
                type="filled"
                theme="success"
              >
                {{ $t('已启用') }}
              </bk-tag>
            </div>
          </div>
        </div>
      </li>
      <li class="item-box">
        <div class="header">
          <p>{{ $t('个人社交账号登录') }}</p>
        </div>
        <div class="login-box">
          <div
            class="login-item"
            v-for="(item, index) in personalLoginMethods"
            :key="index">
            <div
              :class="[
                'login-content',
                item.status,
              ]">
              <div
                class="name"
                v-bk-tooltips="{
                  content: $t('暂未配置'),
                  disabled: item.status !== 'not',
                }">
                <i :class="item.logo" />
                <span>{{ item.name }}</span>
              </div>
              <bk-tag
                v-if="item.status === 'enable'"
                class="status-tag"
                type="filled"
                theme="success"
              >
                {{ $t('已启用') }}
              </bk-tag>
            </div>
          </div>
        </div>
      </li>
    </ul>
    <!-- 认证源详情 -->
    <bk-sideslider
      width="640"
      :is-show="detailsConfig.show"
      :title="detailsConfig.title"
      :before-close="handleBeforeClose"
      quick-close
    >
      <template #header>
        <span>{{ detailsConfig.title }}</span>
        <div>
          <bk-button
            v-if="!detailsConfig.isEdit"
            outline
            theme="primary"
            @click="handleEditDetails">
            {{ $t('编辑') }}
          </bk-button>
          <!-- <bk-button>删除</bk-button> -->
        </div>
      </template>
      <template #default>
        <Local
          v-if="authDetails?.type === 'local' && detailsConfig.isEdit"
          :data="authDetails"
          @cancelEdit="cancelEdit" />
        <WeCom
          v-if="authDetails?.type === 'wecom' && detailsConfig.isEdit"
          :data="authDetails"
          @cancelEdit="cancelEdit" />
        <ViewDetails v-else-if="!detailsConfig.isEdit" :data="authDetails" @updateRow="updateRow" />
      </template>
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips } from 'bkui-vue';
import { inject, reactive, ref } from 'vue';

import Local from './auth-config/Local.vue';
import ViewDetails from './auth-config/ViewDetails.vue';
import WeCom from './auth-config/WeCom.vue';

import { t } from '@/language/index';
import { useMainViewStore } from '@/store';

const store = useMainViewStore();
store.customBreadcrumbs = false;
const editLeaveBefore = inject('editLeaveBefore');

const loginMethods = ref([
  {
    id: 'a48b55c2f3fb41ec8df661a5ea0e1cb6',
    logo: 'bk-sq-icon icon-personal-user',
    name: '账密登录1',
    status: 'enable',
    type: 'local',
  },
  {
    id: '',
    logo: 'bk-sq-icon icon-personal-user',
    name: '账密登录2',
    status: 'not',
    type: 'local',
  },
  {
    id: 'bd103f62c51e4683bd240271ab9e08cf',
    logo: 'user-icon icon-qiyeweixin-2',
    name: '企业微信登录1',
    status: 'enable',
    type: 'wecom',
  },
  {
    id: '',
    logo: 'user-icon icon-qiyeweixin-2',
    name: '企业微信登录2',
    status: 'not',
    type: 'wecom',
  },
]);

const personalLoginMethods = ref([
  {
    logo: 'user-icon icon-weixin',
    name: '微信扫码登录',
    status: 'enable',
  },
  {
    logo: 'user-icon icon-qq',
    name: 'QQ扫码登录',
    status: 'enable',
  },
  {
    logo: 'user-icon icon-google',
    name: '谷歌账号登录',
    status: 'not',
  },
]);

const detailsConfig = reactive({
  show: false,
  title: t('认证源详情'),
  isEdit: false,
});

const authDetails = ref({});

const handleClickActive = (item) => {
  authDetails.value = item;
  detailsConfig.show = true;
  if (item.status === 'not') {
    detailsConfig.isEdit = true;
  }
};

const currentRow = ref({});
const updateRow = (row) => {
  currentRow.value = row;
};

const handleEditDetails = () => {
  detailsConfig.isEdit = true;
};

const cancelEdit = () => {
  if (!authDetails.value.id) {
    detailsConfig.show = false;
  }
  detailsConfig.isEdit = false;
};

const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
    detailsConfig.show = false;
    detailsConfig.isEdit = false;
  } else {
    detailsConfig.show = false;
    detailsConfig.isEdit = false;
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};
</script>

<style lang="less" scoped>
.login-setting-wrapper {
  height: calc(100vh - 104px);
  padding: 24px;

  .login-setting-content {
    padding: 24px;
    background: #fff;

    .item-box {
      .header {
        display: flex;
        align-items: center;
        justify-content: space-between;

        p {
          font-size: 14px;
          font-weight: 700;
          color: #313238;
        }
      }

      .login-box {
        display: flex;
        margin: 24px 0;
        flex-wrap: wrap;

        .login-item {
          position: relative;
          display: inline-block;
          width: 200px;
          margin-bottom: 16px;
          margin-left: 16px;
          text-align: center;
          border-radius: 2px;

          .login-content {
            position: relative;
            height: 80px;
            line-height: 80px;
            cursor: pointer;
            background: #F5F7FA;

            &:hover {
              background: #E1ECFF;
            }

            i {
              font-size: 24px;
            }

            span {
              margin-left: 8px;
              font-size: 14px;
              color: #313238;
            }

            .status-tag {
              position: absolute;
              top: -2px;
              right: -6px;
              background: #2DCB9D;
            }
          }

          .not {
            &:hover {
              background: #F5F7FA;
            }

            i, span {
              color: #C4C6CC;
            }
          }
        }
      }
    }
  }
}

:deep(.bk-sideslider-title) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px 0 50px !important;

  .bk-button {
    padding: 5px 17px !important;
  }
}
</style>
