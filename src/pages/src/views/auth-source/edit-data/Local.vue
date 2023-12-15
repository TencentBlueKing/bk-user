<template>
  <bk-loading class="details-wrapper" :loading="isLoading">
    <div class="details-type">
      <img :src="authSourceData.plugin?.logo" class="w-[24px] h-[24px] mr-[15px]">
      <div>
        <p class="title">{{ authSourceData.plugin?.name }}</p>
        <p class="subtitle">{{ authSourceData.plugin?.description }}</p>
      </div>
    </div>
    <bk-form
      class="auth-source-form"
      ref="formRef"
      form-type="vertical"
      :model="authSourceData"
      :rules="rules">
      <div class="content-item">
        <p class="item-title">基础信息</p>
        <bk-form-item class="w-[600px]" label="名称" property="name" required>
          <bk-input v-model="authSourceData.name" @change="handleChange" />
        </bk-form-item>
      </div>
      <div class="content-item">
        <p class="item-title">基础配置</p>
        <div class="basic-config">
          <p v-if="onDataSources.length">以下数据源已开启「账密登录」</p>
          <div class="on">
            <bk-overflow-title
              type="tips"
              class="source-name"
              v-for="(item, index) in onDataSources"
              :key="index">
              {{ item.data_source_name }}
            </bk-overflow-title>
          </div>
          <p v-if="notDataSources.length">以下数据源未开启「账密登录」</p>
          <div class="off" v-for="(item, index) in notDataSources" :key="index">
            <bk-overflow-title
              type="tips"
              class="source-name">
              {{ item.data_source_name }}
              <bk-button text theme="primary" @click="handleOpen(item)">去开启</bk-button>
            </bk-overflow-title>
          </div>
        </div>
      </div>
      <div class="content-item pb-[24px]">
        <p class="item-title">数据源匹配</p>
        <div class="content-matching">
          <bk-exception
            v-if="onDataSources.length === 0"
            class="exception-part"
            type="empty"
            scene="part"
            description="暂无数据源匹配"
          />
          <div class="content-box" v-else v-for="(item, index) in onDataSources" :key="index">
            <p>{{ item.data_source_name }}</p>
            <div class="field-rules">
              <dl>
                <dt>数据源字段：</dt>
                <bk-overflow-title
                  type="tips"
                  class="source-field"
                  v-for="(val, i) in item.field_compare_rules"
                  :key="i">
                  {{ val.source_field }}
                </bk-overflow-title>
              </dl>
              <dl>
                <dt>认证源字段：</dt>
                <bk-overflow-title
                  type="tips"
                  class="source-field"
                  v-for="(val, i) in item.field_compare_rules"
                  :key="i">
                  {{ val.target_field }}
                </bk-overflow-title>
              </dl>
            </div>
            <span class="or" v-if="index !== 0">or</span>
          </div>
        </div>
      </div>
    </bk-form>
    <div class="footer-wrapper">
      <div class="footer-div">
        <bk-button theme="primary" :loading="btnLoading" @click="handleSubmit">
          提交
        </bk-button>
        <bk-button @click="handleCancel">
          取消
        </bk-button>
      </div>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

import useValidate from '@/hooks/use-validate';
import { getIdpsDetails, patchIdps } from '@/http/authSourceFiles';
import { getDataSourceList } from '@/http/dataSourceFiles';
import router from '@/router/index';
import { useMainViewStore } from '@/store/mainView';

const route = useRoute();
const validate = useValidate();
const store = useMainViewStore();

const formRef = ref();
const isLoading = ref(false);
const authSourceData = ref({});
const onDataSources = ref([]);
const notDataSources = ref([]);
const btnLoading = ref(false);

const rules = {
  name: [validate.required, validate.name],
};

onMounted(async () => {
  isLoading.value = true;
  try {
    const [authRes, dataRes] = await Promise.all([
      getIdpsDetails(route.params.id),
      getDataSourceList(''),
    ]);
    authSourceData.value = authRes.data;
    store.breadCrumbsTitle = `编辑${authSourceData.value.plugin.name}认证源`;
    processMatchRules(dataRes.data);
  } catch (error) {
    console.error(error);
  } finally {
    isLoading.value = false;
  }
});

const processMatchRules = (list) => {
  const dataSourceIds = authSourceData.value.data_source_match_rules.map(item => item.data_source_id);
  onDataSources.value = list
    .filter(val => dataSourceIds.includes(val.id))
    .map(val => ({
      data_source_id: val.id,
      data_source_name: val.name,
      field_compare_rules: authSourceData.value.data_source_match_rules
        .find(item => item.data_source_id === val.id).field_compare_rules,
    }));
  notDataSources.value = list
    .filter(val => !dataSourceIds.includes(val.id) && val.plugin_id === 'local')
    .map(val => ({
      data_source_id: val.id,
      data_source_name: val.name,
    }));
};

const handleOpen = (item) => {
  router.push({
    name: 'newLocal',
    params: {
      type: 'local',
      id: item.data_source_id,
    },
  });
};

const handleChange = () => {
  window.changeInput = true;
};

const handleCancel = () => {
  router.push({
    name: 'authSourceList',
  });
};

const handleSubmit = async () => {
  await formRef.value.validate();
  btnLoading.value = true;
  patchIdps({
    id: route.params.id,
    name: authSourceData.value.name,
  }).then(() => {
    Message({ theme: 'success', message: '认证源更新成功' });
    window.changeInput = false;
    router.push({ name: 'authSourceList' });
  })
    .catch((e) => {
      console.warn(e);
      Message({ theme: 'error', message: '认证源更新失败' });
    })
    .finally(() => {
      btnLoading.value = false;
    });
};
</script>

<style lang="less" scoped>
.details-wrapper {
  width: 1000px;
  margin: 0 auto;

  .details-type {
    display: flex;
    padding: 10px 16px;
    margin: 16px 0;
    background: #FFF;
    border-radius: 2px;
    align-items: center;

    .title {
      font-size: 14px;
      color: #313238;
    }

    .subtitle {
      font-size: 12px;
      color: #979BA5;
    }
  }

  .auth-source-form {
    .content-item {
      margin-bottom: 16px;
      background: #fff;
      border-radius: 2px;
      box-shadow: 0 2px 4px 0 #1919290d;

      .item-title {
        padding: 16px 0 16px 24px;
        font-size: 14px;
        font-weight: 700;
      }

      .basic-config {
        padding-bottom: 12px;
        margin-left: 64px;

        p {
          margin-bottom: 12px;
          font-size: 14px;
          color: #63656E;
        }

        .source-name {
          width: 300px;
          height: 40px;
          padding-left: 24px;
          margin-bottom: 12px;
          margin-left: 40px;
          line-height: 40px;
          color: #313238;
          background: #F5F7FA;
          border-radius: 2px;
        }

        .off {
          .source-name {
            position: relative;
            color: #C4C6CC;

            ::v-deep .text-ov {
              width: 220px;
            }

            .bk-button {
              position: absolute;
              top: 13px;
              right: 16px;
            }
          }
        }
      }

      .content-matching {
        margin-left: 59px;

        ::v-deep .exception-part {
          position: relative;
          width: 400px;

          .bk-exception-img {
            width: 340px;
            height: 170px;
          }

          .bk-exception-description {
            position: absolute;
            bottom: 0;
            font-size: 14px;
          }
        }

        .content-box {
          position: relative;
          width: 622px;

          .or {
            position: absolute;
            top: -16px;
            left: -22px;
            display: inline-block;
            width: 19px;
            height: 16px;
            line-height: 16px;
            color: #FE9C00;
            text-align: center;
            background: #FFF3E1;
            border-radius: 2px;

            &::before {
              position: absolute;
              top: -16px;
              left: 10px;
              width: 12px;
              height: 16px;
              border: 1px solid #DCDEE5;
              border-right: transparent;
              border-bottom: transparent;
              border-top-left-radius: 2px;
              content: '';
            }

            &::after {
              position: absolute;
              top: 16px;
              left: 10px;
              width: 12px;
              height: 16px;
              border: 1px solid #DCDEE5;
              border-top: transparent;
              border-right: transparent;
              border-bottom-left-radius: 2px;
              content: '';
            }
          }
        }

        p {
          position: relative;
          padding: 0 24px;
          line-height: 32px;
          background: #F0F1F5;
          border-radius: 2px 2px 0 0;
        }

        .field-rules {
          display: flex;
          margin-bottom: 16px;
          background: #FAFBFD;
          border-radius: 2px;

          dl {
            padding: 12px 0 12px 50px;;

            dt {
              font-size: 14px;
              line-height: 22px;
              color: #979BA5;
            }

            .source-field {
              max-width: 250px;
              min-width: 120px;
              font-size: 14px;
              line-height: 22px;
              color: #313238;
            }
          }
        }
      }

      ::v-deep .bk-form-item {
        padding-bottom: 24px;
        margin-bottom: 0;
        margin-left: 64px;
        font-size: 14px;

        &:last-child {
          margin-bottom: 16px;
        }

        .bk-radio-button {
          .bk-radio-button-label {
            font-size: 14px !important;
          }
        }

        .bk-radio-label {
          font-size: 14px !important;
        }

        .error-text {
          font-size: 12px;
          line-height: 1;
          color: #ea3636;
          animation: form-error-appear-animation .15s;
        }
      }

      .data-source-matching {
        width: 622px;
        margin-left: 59px;
        border-radius: 2px;

        .hover-item {
          cursor: pointer;
        }

        .matching-item {
          position: relative;
          padding: 16px 16px 16px 24px;
          margin-bottom: 16px;
          background: #F5F7FA;

          .bk-sq-icon {
            position: absolute;
            top: -6px;
            right: -6px;
            font-size: 20px;
            color: #EA3636;
          }

          .or {
            position: absolute;
            top: -16px;
            left: -22px;
            display: inline-block;
            width: 19px;
            height: 16px;
            line-height: 16px;
            color: #FE9C00;
            text-align: center;
            background: #FFF3E1;
            border-radius: 2px;

            &::before {
              position: absolute;
              top: -27px;
              left: 10px;
              width: 12px;
              height: 27px;
              border: 1px solid #DCDEE5;
              border-right: transparent;
              border-bottom: transparent;
              border-top-left-radius: 2px;
              content: '';
            }

            &::after {
              position: absolute;
              top: 16px;
              left: 10px;
              width: 12px;
              height: 27px;
              border: 1px solid #DCDEE5;
              border-top: transparent;
              border-right: transparent;
              border-bottom-left-radius: 2px;
              content: '';
            }
          }

          ::v-deep .bk-form-item {
            padding-bottom: 24px;
            margin-bottom: 0;
            margin-left: 0;
            font-size: 14px;

            &:last-child {
              margin-bottom: 0;
            }
          }

          .item-flex-header {
            display: flex;
            align-items: center;

            ::v-deep .bk-form-item {
              padding-bottom: 0;
              margin-bottom: 0;
              margin-left: 0;
              font-size: 14px;

              &:last-child {
                margin-left: 16px;
              }
            }
          }

          .item-flex {
            position: relative;
            display: flex;
            padding-bottom: 8px;
            align-items: center;

            ::v-deep .bk-form-item {
              padding-bottom: 0;
              margin-bottom: 0;
              margin-left: 0;
              font-size: 14px;
            }

            .auth-source-fields {
              margin-left: 16px;
            }

            .user-icon {
              font-size: 16px;
              color: #dcdee5;

              &:hover {
                color: #c4c6cc;
              }
            }

            .icon-plus-fill {
              position: absolute;
              top: 9px;
              right: 35px;
            }

            .icon-minus-fill {
              position: absolute;
              top: 9px;
              right: 5px;
            }

            .and {
              position: absolute;
              top: -12px;
              left: -24px;
              display: inline-block;
              width: 24px;
              height: 16px;
              line-height: 16px;
              color: #14A568;
              text-align: center;
              background: #E4FAF0;
              border-radius: 2px;

              &::before {
                position: absolute;
                top: -12px;
                left: 12px;
                width: 12px;
                height: 12px;
                border: 1px solid #DCDEE5;
                border-right: transparent;
                border-bottom: transparent;
                border-top-left-radius: 2px;
                content: '';
              }

              &::after {
                position: absolute;
                top: 16px;
                left: 12px;
                width: 12px;
                height: 12px;
                border: 1px solid #DCDEE5;
                border-top: transparent;
                border-right: transparent;
                border-bottom-left-radius: 2px;
                content: '';
              }
            }
          }
        }
      }

      .add-data-source {
        display: flex;
        width: 622px;
        height: 32px;
        margin-left: 59px;
        font-size: 14px;
        color: #3A84FF;
        cursor: pointer;
        background: #F0F5FF;
        border: 1px dashed #A3C5FD;
        border-radius: 2px;
        align-items: center;
        justify-content: center;

        span {
          margin-left: 5px;
        }
      }
    }
  }

  .footer-wrapper {
    position: fixed;
    bottom: 0;
    left: 0;
    z-index: 9;
    width: 100%;
    height: 48px;
    margin-bottom: 0;
    line-height: 48px;
    background: #FAFBFD;
    box-shadow: 0 -1px 0 0 #DCDEE5;

    .footer-div {
      width: 1000px;
      margin: 0 auto;
    }

    .bk-button {
      width: 88px;
      margin-right: 8px;
    }
  }
}
</style>
