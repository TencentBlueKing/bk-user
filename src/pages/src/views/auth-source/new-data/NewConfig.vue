<template>
  <div>
    <MainBreadcrumbsDetails>
      <template #content>
        <bk-steps
          ext-cls="steps-wrapper"
          :controllable="controllable"
          :cur-step="curStep"
          :steps="stepsConfig"
          class="mb20"
          @click="stepChanged"
        />
      </template>
    </MainBreadcrumbsDetails>
    <div class="config-wrapper">
      <div class="config-content">
        <div class="config-type">
          <P class="title">企业认证源</P>
          <ul>
            <li
              v-for="(item, index) in dataList"
              :key="index"
              :class="{ 'active': isActive === item.name }"
              @click="handleClick(item)">
              <div class="config-item">
                <i :class="item.logo"></i>
                <div>
                  <p>{{item.name}}</p>
                  <span>{{item.description}}</span>
                </div>
              </div>
              <i class="user-icon icon-check-line" />
            </li>
          </ul>
        </div>
        <div class="config-type">
          <P class="title">社会化认证源</P>
          <ul>
            <li
              v-for="(item, index) in dataList2"
              :key="index"
              :class="{ 'active': isActive === item.name }"
              @click="handleClick(item)">
              <div class="config-item">
                <i :class="item.logo"></i>
                <div>
                  <p>{{item.name}}</p>
                  <span>{{item.description}}</span>
                </div>
              </div>
              <i class="user-icon icon-check-line" />
            </li>
          </ul>
        </div>
      </div>
      <div class="footer-wrapper">
        <bk-button theme="primary" class="mr8" @click="handleSubmit">下一步</bk-button>
        <bk-button @click="handleClickCancel">取消</bk-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';

import MainBreadcrumbsDetails from '@/components/layouts/MainBreadcrumbsDetails.vue';
import router from '@/router/index';

const curStep = ref(1);
const controllable = ref(true);
const stepsConfig = reactive([
  { title: '认证源选择', icon: 1 },
  { title: '登录配置', icon: 2 },
]);
const isActive = ref('企业微信');

const dataList = reactive([
  {
    name: '企业微信',
    description: '企业微信是腾讯微信团队为企业打造的专业办公…',
    logo: 'user-icon icon-qiyeweixin',
  },
  {
    name: 'Windows AD',
    description: 'Windows AD 是 Microsoft 提供的本地…',
    logo: 'user-icon icon-win',
  },
  {
    name: 'Open LDAP',
    description: 'LDAP 是一个开放的，中立的，工业标准的应用…',
    logo: 'user-icon icon-qiyeweixin',
  },
]);

const dataList2 = reactive([
  {
    name: '微信',
    description: '微信是一款跨平台的通信工具。支持单人、多人…',
    logo: 'user-icon icon-wechat',
  },
  {
    name: '腾讯 QQ',
    description: '腾讯 QQ 是一款基于互联网的即时通讯软件。',
    logo: 'user-icon icon-win',
  },
  {
    name: 'GitHub',
    description: 'GitHub 是一个面向开源及私有软件项目的托管…',
    logo: 'user-icon icon-qiyeweixin',
  },
  {
    name: 'Google',
    description: 'Google 是全球最大的搜索引擎公司。',
    logo: 'user-icon icon-qiyeweixin',
  },
]);

// 改变当前选中值
const stepChanged = (index) => {
  curStep.value = index;
};

const handleClick = (item) => {
  isActive.value = item.name;
};

const handleClickCancel = () => {
  router.push({
    name: 'authSource',
  });
};
</script>

<style lang="less">
.main-breadcrumbs-details {
  .icon-arrow-left {
    margin-right: 10px;
    font-size: 18px;
    color: #3a84ff;
    cursor: pointer;
  }

  .tittle{
    margin-right: 8px;
    font-size: 16px;
    color: #313238;
  }

  .steps-wrapper {
    width: 360px;
    margin: 0 auto;
  }
}

.config-wrapper {
  width: 1000px;
  margin: 0 auto;

  .config-content {
    margin: 24px 0;
    background-color: #fff;

    .config-type {
      padding: 24px 40px;

      .title {
        font-size: 14px;
        font-weight: 700;
        color: #313238;
      }

      ul {
        display: flex;
        margin: 16px 0;

        li {
          width: 200px;
          height: 84px;
          margin-right: 16px;
          cursor: pointer;
          background: #F5F7FA;
          border-radius: 2px;
          box-sizing: content-box;

          .icon-check-line {
            display: none;
          }

          // &:hover {
          //   border: 1px solid #3A84FF;
          // }

          .config-item {
            display: flex;
            padding: 12px 16px;
            align-items: center;
            justify-content: space-between;

            i {
              margin-right: 12px;
              font-size: 24px;
            }

            p {
              font-size: 14px;
              color: #313238;
            }

            span {
              color: #979BA5;
            }
          }
        }

        .active {
          position: relative;
          background-color: #fff;
          border: 1px solid #3A84FF;

          .icon-check-line {
            position: absolute;
            top: 0;
            right: 0;
            z-index: 999;
            display: inline-block;
            font-size: 14px;
            color: #fff;
          }

          &::after {
            position: absolute;
            top: 0;
            right: 0;
            display: inline-block;
            width: 0;
            height: 0;
            border-top: 24px solid #3A84FF;
            border-left: 24px solid transparent;
            content: '';
          }
        }
      }
    }
  }

  .footer-wrapper {
    button {
      width: 88px;
    }
  }
}
</style>
