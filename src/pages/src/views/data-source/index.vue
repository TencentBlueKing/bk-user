<template>
  <MainView>
    <template #menu>
      <bk-menu :active-key="state.activeKey">
        <bk-menu-item
          v-for="item in menuData"
          :key="item.key"
          @click="handleClickItem(item)"
        >
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
      <bk-tab
        v-if="state.activeKey === 'dataSourceManage'"
        v-model:active="active"
        type="unborder-card"
        ext-cls="tab-details"
      >
        <bk-tab-panel
          v-for="item in panels"
          :key="item.name"
          :name="item.name"
          :label="item.label"
        >
          <OurCompany />
        </bk-tab-panel>
      </bk-tab>
    </template>
  </MainView>
</template>

<script setup lang="tsx">
import MainView from "@/components/layouts/MainView.vue";
import { reactive, ref } from "vue";
import OurCompany from "./OurCompany.vue";

const state = reactive({
  activeKey: "dataSourceManage",
  activeName: "数据源管理",
});
const menuData = reactive([
  {
    name: "数据源管理",
    key: "dataSourceManage",
    icon: "user-icon icon-root-node-i",
  },
]);
const active = ref("our");
const panels = reactive([
  { name: "our", label: "本公司" },
]);

const handleClickItem = (item: any) => {
  state.activeKey = item.key;
  state.activeName = item.name;
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
:deep(.tab-details) {
  height: calc(100vh - 104px);
  .bk-tab-header {
    background: #fff;
    border-bottom: none;
    box-shadow: 0 3px 4px 0 #0000000a;
    font-size: 14px;
    line-height: 36px !important;
    .bk-tab-header-item {
      padding: 0px 5px !important;
      margin: 0 20px;
    }
  }
  .bk-tab-content {
    padding: 0;
  }
}
</style>
