<template>
  <div class="card-wrapper">
    <div class="mb-[12px]" v-for="(item, index) in plugins" :key="index">
      <div
        v-if="dataSource?.plugin_id && index === 0"
        :class="['card-header', { 'hidden-card': dataSource.plugin_id !== item.id }]"
        v-bk-tooltips="{
          content: $t('若需切换数据源需要先对当前已选数据源进行重置操作'),
          delay: 300,
          offset: 0,
          disabled: dataSource.plugin_id === item.id,
        }"
        @click="handleClick(item.id)">
        <div class="card-header-right">
          <img :src="item.logo" />
          <div>
            <p class="title">{{ item.name }}</p>
            <p class="subtitle">{{ item.description }}</p>
          </div>
        </div>
        <slot name="right" v-if="dataSource.plugin_id === item.id"></slot>
      </div>
      <template v-else>
        <div
          v-if="isShow"
          :class="['card-header', { 'hidden-card': config }]"
          v-bk-tooltips="{
            content: $t('若需切换数据源需要先对当前已选数据源进行重置操作'),
            delay: 300,
            offset: 0,
            disabled: !config,
          }"
          @click="handleClick(item.id)">
          <div class="card-header-right">
            <img :src="item.logo" />
            <div>
              <p class="title">{{ item.name }}</p>
              <p class="subtitle">{{ item.description }}</p>
            </div>
          </div>
          <slot v-if="index === 0" name="right"></slot>
        </div>
      </template>
      <slot v-if="index === 0" name="content"></slot>
    </div>
    <p
      v-if="dataSource?.plugin_id"
      class="view-type"
      @click="toggleState">
      {{ text }}
      <AngleDownLine class="ml-[8px]" />
    </p>
  </div>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips } from 'bkui-vue';
import { AngleDownLine } from 'bkui-vue/lib/icon';
import { computed, ref, watch } from 'vue';

import { t } from '@/language/index';

const emit = defineEmits(['handleCollapse']);

const props = defineProps({
  plugins: {
    type: Array,
    default: () => ([]),
  },
  dataSource: {
    type: Object,
    default: () => {},
  },
  config: {
    type: Boolean,
    default: false,
  },
  showContent: {
    type: Boolean,
    default: false,
  },
});

const handleClick = (id: string) => {
  if (props.config && props.dataSource.plugin_id === 'local') return;
  if (!props.config || props.dataSource.plugin_id === id || id !== 'local') {
    emit('handleCollapse', id);
  }
};

const isShow = ref(true);

const text = computed(() => (isShow.value ? t('收起') : t('查看数据源类型')));

watch(() => props.showContent, (val) => {
  isShow.value = !val;
});

const toggleState = () => {
  isShow.value = !isShow.value;
};
</script>

<style lang="less" scoped>
.card-wrapper {
  .card-header {
    display: flex;
    padding: 16px;
    margin-bottom: 2px;
    background: #fff;
    border: 1px solid #fff;
    border-radius: 2px;
    box-shadow: 0 2px 4px 0 #1919290d;
    align-items: center;
    justify-content: space-between;

    &:hover {
      cursor: pointer;
    }

    .card-header-right {
      display: flex;
      align-items: center;

      img {
        width: 24px;
        height: 24px;
        margin-right: 12px;
      }

      .title {
        font-size: 14px;
        line-height: 22px;
        color: #313238;
      }

      .subtitle {
        line-height: 18px;
        color: #979BA5;
      }
    }

    &.hidden-card {
      img, .title, .subtitle {
        color: #C4C6CC;
      }

      &:hover {
        border: 1px solid transparent;
      }
    }
  }

  .card-content {
    display: none;
    background: #FFF;
    border-radius: 2px;
    box-shadow: 0 2px 4px 0 #1919290d;

    .step-bar {
      text-align: center;
      background: #FAFBFD;
      box-shadow: 0 1px 0 0 #F0F1F5;
    }
  }

  .active-card-content {
    display: block;
  }

  .view-type {
    font-size: 14px;
    text-align: center;
    cursor: pointer;

    span {
      transform: rotate(180deg);
    }
  }
}
</style>
