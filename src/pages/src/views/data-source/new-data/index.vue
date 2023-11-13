<template>
  <bk-loading :loading="isLoading" class="data-source-wrapper">
    <MainBreadcrumbsDetails>
      <template #tag>
        <bk-dropdown
          class="data-source-type"
          v-for="item in typeList"
          :key="item"
          placement="bottom-start"
          @hide="() => (isDropdown = false)"
          @show="() => (isDropdown = true)">
          <div :class="['type-title', { 'hover-title': isDropdown && !currentId }]" v-if="item.id === currentType">
            <img v-if="item.logo" :src="item.logo">
            <span class="pr-[10px]">{{ item.name }}</span>
            <DownShape v-if="!currentId" class="down-shape-icon" />
          </div>
          <template #content v-if="!currentId">
            <bk-dropdown-menu ext-cls="tag-menu">
              <bk-dropdown-item
                v-for="element in typeList"
                :key="element"
                :class="['type-item', { 'active': element.id === currentType }]"
                @click="toggleType(element)">
                <img v-if="element.logo" :src="element.logo">
                <span>{{ element.name }}</span>
              </bk-dropdown-item>
            </bk-dropdown-menu>
          </template>
        </bk-dropdown>
      </template>
      <template #content v-if="currentType === 'general'">
        <bk-steps
          ext-cls="steps-wrapper"
          :cur-step="curStep"
          :steps="typeSteps?.[currentType]"
        />
      </template>
    </MainBreadcrumbsDetails>
    <Local v-if="currentType === 'local'" />
    <Http
      v-if="currentType === 'general'"
      :cur-step="curStep"
      @updateCurStep="updateCurStep" />
  </bk-loading>
</template>

<script setup lang="ts">
import { DownShape } from 'bkui-vue/lib/icon';
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';

import Http from './Http.vue';
import Local from './Local.vue';

import MainBreadcrumbsDetails from '@/components/layouts/MainBreadcrumbsDetails.vue';
import { getDataSourcePlugins } from '@/http/dataSourceFiles';
import router from '@/router/index';
import { useMainViewStore } from '@/store/mainView';

const route = useRoute();
const store = useMainViewStore();

const isDisabled = ref(false);
const currentType = ref('');
const currentId = computed(() => {
  const { id } = route.params;
  isDisabled.value = !!id;
  currentType.value = route.params.type;
  return id;
});

const isLoading = ref(false);
const typeList = ref([]);

const curStep = ref(1);
const typeSteps = reactive({
  general: [
    { title: '服务配置' },
    { title: '字段设置' },
  ],
});

const isDropdown = ref(false);

onMounted(async () => {
  isLoading.value = true;
  try {
    const pluginsRes = await getDataSourcePlugins();
    typeList.value = pluginsRes.data;
    if (currentId.value) {
      store.breadCrumbsTitle = '编辑数据源';
    }
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
});

const updateCurStep = (value: number) => {
  curStep.value = value;
};

const toggleType = (item) => {
  router.push({
    name: 'newLocal',
    params: {
      type: item.id,
    },
  });
};
</script>

<style lang="less" scoped>
.data-source-type {
  .type-title {
    display: flex;
    height: 24px;
    line-height: 24px;
    background-color: #f0f1f5;
    align-items: center;
    border-radius: 2px;

    img {
      width: 14px;
      height: 14px;
      margin: 0 8px 0 10px;
    }

    .down-shape-icon {
      display: inline-block;
      margin-right: 10px;
    }
  }

  .hover-title {
    cursor: pointer;
    background-color: #DCDEE5;

    .down-shape-icon {
      display: inline-block;
      transform: rotate(180deg);
      transition: all 0.2s;
    }
  }
}

.type-item {
  display: flex;
  align-items: center;

  img {
    width: 14px;
    height: 14px;
  }

  span {
    margin-left: 8px;
  }
}

.active {
  color: #3a84ff;
  background-color: #E1ECFF;

  &:hover {
    background-color: #E1ECFF;
  }
}

.steps-wrapper {
  width: 350px;
  margin: 0 auto;
}
</style>
