<template>
  <MainView>
    <template #menu>
      <bk-menu :active-key="state.activeKey">
        <bk-menu-item v-for="item in menuData" :key="item.key" @click="handleClickItem(item)">
          <template #icon>
            <i :class="item.icon" />
          </template>
          {{ item.name }}
        </bk-menu-item>
      </bk-menu>
    </template>
    <template #main-header>
      <div>{{ state.activeName }}</div>
    </template>
    <template #main-content>
      <GroupDetails />
    </template>
  </MainView>
</template>

<script setup lang="tsx">
import MainView from "@/components/layouts/MainView.vue";
import GroupDetails from "./group-details/index.vue";
import { ref, reactive } from "vue";

const state = reactive({
  activeKey: "overview",
  activeName: "集团概览",
});
const menuData = reactive([
  {
    name: "集团概览",
    key: "overview",
    icon: "user-icon icon-root-node-i",
  },
]);

const handleClickItem = (item: any) => {
  state.activeKey = item.key;
  state.activeName = item.name
};
</script>

<style lang="less" scoped>
:deep(.bk-menu) {
  width: 240px;
  height: 100%;
  background-color: #fff;
  box-shadow: 1px 0 0 0 #dcdee5;
  .bk-menu-item {
    color: #63656e;
    margin: 0px;
    &:hover {
      background: #f0f1f5;
    }
    &:first-child {
      margin-top: 12px;
    }
  }
  .is-active {
    background: #e1ecff;
    color: #3a84ff;
    &:hover {
      background: #e1ecff;
    }
  }
}
</style>
