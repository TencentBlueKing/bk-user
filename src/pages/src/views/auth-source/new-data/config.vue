<template>
  <bk-loading class="config-wrapper" :loading="isLoading">
    <div class="config-content">
      <div class="config-type">
        <P class="title">{{ $t('认证源选择') }}</P>
        <ul>
          <li
            v-for="(item, index) in dataList"
            v-show="item.id !== 'local'"
            :key="index"
            :class="{ 'active': currentPlugin.id === item.id }"
            @click="handleClick(item)">
            <div class="config-item">
              <img :src="item.logo">
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
      <span v-bk-tooltips="{
        content: $t('请选择认证源'),
        distance: 20,
        disabled: !isDisabled,
      }">
        <bk-button
          theme="primary"
          class="mr8"
          @click="handleNext"
          :disabled="isDisabled"
        >{{ $t('下一步') }}</bk-button>
      </span>
      <bk-button @click="handleClickCancel">{{ $t('取消') }}</bk-button>
    </div>
  </bk-loading>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips } from 'bkui-vue';
import { computed, onMounted, ref } from 'vue';

import { getIdpsPlugins } from '@/http';
import { t } from '@/language/index';
import router from '@/router/index';
import { useMainViewStore } from '@/store';

const store = useMainViewStore();
store.breadCrumbsTitle = t('新建认证源');

const emit = defineEmits(['next']);

const dataList = ref([]);
const isLoading = ref(false);
const currentPlugin = ref({});

const isDisabled = computed(() => JSON.stringify(currentPlugin.value) === '{}');

onMounted(async () => {
  try {
    isLoading.value = true;
    const res = await getIdpsPlugins();
    dataList.value = res.data;
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
});

const handleClick = (item) => {
  currentPlugin.value = item;
};

const handleNext = () => {
  if (currentPlugin.value.id === 'local') return;
  emit('next', currentPlugin.value);
};

const handleClickCancel = () => {
  router.push({
    name: 'authSourceList',
  });
};
</script>

<style lang="less" scoped>
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

            img {
              width: 24px;
              height: 24px;
              margin-right: 15px;
            }

            p {
              font-size: 14px;
              color: #313238;
            }

            span {
              display: -webkit-box;
              overflow: hidden;
              color: #979BA5;
              text-overflow: ellipsis;
              word-break: break-all;
              -webkit-box-orient: vertical;
              -webkit-line-clamp: 2;
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
    margin-bottom: 24px;

    button {
      width: 88px;
    }
  }
}
</style>
