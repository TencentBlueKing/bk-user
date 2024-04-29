<template>
  <div class="login-setting-wrapper user-scroll-y" v-bkloading="{ loading: isLoading, zIndex: 9 }">
    <ul v-if="currentDataSource?.plugin_id" class="login-setting-content">
      <li class="item-box">
        <div class="header">
          <p>{{ $t('基本登录方式') }}</p>
        </div>
        <div class="login-box">
          <div
            class="login-item"
            v-for="(item, index) in idpsPlugins"
            :key="index">
            <div
              :class="['login-content',
                       { 'login-content-disabled': currentDataSource.plugin_id !== 'local' && item.id === 'local' }]">
              <div
                :class="['box', { 'disabled-box': item.status === 'disabled' && !item.idp_id }]"
                v-bk-tooltips="{
                  content: item.text,
                  disabled: item.status !== 'disabled' || item.idp_id,
                }"
                @click="handleClickActive(item)">
                <img :src="item.logo" class="logo-style" />
                <span>{{ item.name }}</span>
                <bk-tag
                  v-if="item.id === 'local'"
                  class="tag-info"
                  type="stroke"
                  theme="info"
                >
                  {{ $t('本地') }}
                </bk-tag>
              </div>
              <bk-tag
                v-if="item.status === 'enabled'"
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
    <div v-else>
      <bk-exception
        class="exception-wrap-item"
        type="building"
        :title="$t('暂未配置数据源')"
        :description="$t('需要先配置数据源后才可进行登录配置，当前支持使用以下方式进行登录')"
      >
        <div class="bg-white px-[24px] py-[16px] w-[508px] text-left">
          <p class="mb-[8px]">{{ $t('基本登录方式') }}</p>
          <bk-tag v-for="(item, index) in idpsPlugins" :key="index" class="mr-[8px] !important">
            <template #icon>
              <img :src="item.logo" class="w-[16px] h-[16px]">
            </template>
            {{ item.name }}
          </bk-tag>
        </div>
        <bk-button theme="primary" class="mt-[24px]" @click="handleDataSource">
          {{ $t('配置数据源') }}
        </bk-button>
      </bk-exception>
    </div>
    <!-- 认证源详情 -->
    <bk-sideslider
      :width="(authDetails?.id === 'local' && detailsConfig.isEdit) ? 960 : 640"
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
        <template v-if="authDetails?.id === 'local'">
          <Local
            v-if="detailsConfig.isEdit"
            :current-id="authDetails?.idp_id"
            @cancel="cancelEdit"
            @success="localSuccess" />
          <LocalView v-else :current-id="authDetails?.idp_id" @updateRow="updateRow" />
        </template>
        <template v-if="authDetails?.id === 'wecom'">
          <WeCom
            v-if="detailsConfig.isEdit"
            :data-source-id="currentDataSource?.id"
            :current-id="authDetails?.idp_id"
            @success="weComSuccess"
            @cancelEdit="cancelEdit" />
          <WeComView v-else :current-id="authDetails?.idp_id" />
        </template>
      </template>
    </bk-sideslider>
  </div>
</template>

<script setup lang="ts"> import { h, inject, onMounted, reactive, ref } from 'vue';
import { bkTooltips as vBkTooltips, InfoBox } from 'bkui-vue';

import Local from './auth-config/Local.vue';
import LocalView from './auth-config/LocalView.vue';
import WeCom from './auth-config/WeCom.vue';
import WeComView from './auth-config/WeComView.vue';

import {
  getDataSourceList,
  getIdps,
  getIdpsPlugins,
} from '@/http';
import { t } from '@/language/index';
import router from '@/router';
import { useMainViewStore } from '@/store';
import { copy } from '@/utils';

const store = useMainViewStore();
store.customBreadcrumbs = false;
const editLeaveBefore = inject('editLeaveBefore');

const isLoading = ref(false);
const idpsPlugins = ref([]);
const currentDataSource = ref({});
onMounted(() => {
  getRealDataSource();
  initIdpsPlugins();
});

// 获取当前实名数据源
const getRealDataSource = () => {
  getDataSourceList({ type: 'real' }).then((res) => {
    currentDataSource.value = res.data[0] || {};
  });
};

const initIdpsPlugins = async () => {
  try {
    isLoading.value = true;
    const [pluginsRes, idpsRes] = await Promise.all([
      getIdpsPlugins(),
      getIdps(''),
    ]);

    idpsPlugins.value = pluginsRes.data;

    idpsPlugins.value.forEach((plugin) => {
      const idp = idpsRes.data.find(idp => idp.plugin.id === plugin.id);
      if (idp) {
        plugin.idp_id = idp.id;
        plugin.status = idp.status;
      } else {
        plugin.status = 'disabled';
        plugin.text = currentDataSource.value.plugin_id !== 'local' && plugin.id === 'local'
          ? t('仅对本地数据源启用')
          : t('暂未配置');
      }
    });
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
};

const detailsConfig = reactive({
  show: false,
  title: t('认证源详情'),
  isEdit: false,
});

const authDetails = ref({});

const handleClickActive = (item) => {
  if (currentDataSource.value.plugin_id !== 'local' && item.id === 'local') return;
  if (!item.idp_id) {
    detailsConfig.isEdit = true;
    detailsConfig.title = `${item.name}${t('登录配置')}`;
  } else {
    detailsConfig.isEdit = false;
    detailsConfig.title = `${item.name}${t('登录详情')}`;
  }
  authDetails.value = item;
  detailsConfig.show = true;
};

const currentRow = ref({});
const updateRow = (row) => {
  currentRow.value = row;
};

const handleEditDetails = () => {
  detailsConfig.isEdit = true;
};

const cancelEdit = () => {
  if (!authDetails.value.idp_id) {
    detailsConfig.show = false;
  }
  detailsConfig.isEdit = false;
  window.changeInput = false;
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

// 本地认证源配置成功
const localSuccess = (status: boolean) => {
  window.changeInput = false;
  detailsConfig.show = false;
  InfoBox({
    title: t('配置成功'),
    infoType: 'success',
    subTitle: h('div', {
      style: {
        height: '44px',
        background: '#F5F7FA',
        lineHeight: '44px',
        display: status ? 'flex' : 'none',
        alignItems: 'center',
      },
    }, [
      h('i', {
        class: 'user-icon icon-info-i',
        style: {
          margin: '0 8px 0 12px',
        },
      }),
      h('span', {
        style: {
          fontSize: '12px',
        },
      }, t('账号陆续生效中，请以用户最终收到的邮件为准')),
    ]),
    dialogType: 'confirm',
    footerAlign: 'center',
    closeIcon: false,
    quickClose: false,
    onConfirm: () => {
      initIdpsPlugins();
    },
  });
};

// 企业微信认证源配置成功
const weComSuccess = (url: string) => {
  window.changeInput = false;
  detailsConfig.show = false;
  if (url) {
    InfoBox({
      title: t('配置成功'),
      subTitle: h('div', {
        style: {
          display: url ? 'block' : 'none',
          textAlign: 'left',
        },
      }, [
        h('p', {
          style: {
            marginBottom: '12px',
          },
        }, t('请将一下回调地址填写到企业微信配置内：')),
        h('div', {
          style: {
            background: '#F5F7FA',
            padding: '8px 12px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          },
        }, [
          h('p', {
            style: {
              width: '230px',
            },
          }, url),
          h('i', {
            class: 'user-icon icon-copy',
            style: {
              color: '#3A84FF',
              fontSize: '14px',
              cursor: 'pointer',
            },
            onClick: () => copy(url),
          }),
        ]),
      ]),
      dialogType: 'confirm',
      confirmText: t('确定'),
      infoType: 'success',
      quickClose: false,
      closeIcon: false,
      onConfirm() {
        initIdpsPlugins();
      },
    });
  } else {
    initIdpsPlugins();
  }
};

const handleDataSource = () => {
  router.push({ name: 'dataSource' });
};
</script>

<style lang="less" scoped>
.login-setting-wrapper {
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

          .login-content-disabled {
            &:hover {
              background: #F5F7FA !important;
            }
          }

          .login-content {
            position: relative;
            height: 80px;
            line-height: 80px;
            cursor: pointer;
            background: #F5F7FA;

            &:hover {
              background: #E1ECFF;
            }

            .box {
              display: flex;
              align-items: center;

              .logo-style {
                width: 24px;
                height: 24px;
                margin-left: 24px;
              }

              span {
                margin: 0 6px 0 12px;
                font-size: 14px;
                color: #313238;
              }

              .tag-info {
                background: #F0F5FF;

                :deep(.bk-tag-text) {
                  background: #F0F5FF;
                }
              }
            }

            .disabled-box {
              span {
                color: #C4C6CC !important;
              }

              .tag-info {
                background: #FAFBFD;
                border: 1px solid #DCDEE5;

                :deep(.bk-tag-text) {
                  color: #C4C6CC;
                  background: #FAFBFD;
                }
              }
            }

            .status-tag {
              position: absolute;
              top: -2px;
              right: -6px;
              background: #2DCB9D;
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
