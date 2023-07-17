<template>
  <MainView>
    <template #menu>
      <OrganizationTree @change-node="(node) => changeNode(node)" />
    </template>
    <!-- <template #main-content>
      <bk-tab
        v-model:active="active"
        type="unborder-card"
        ext-cls="tab-details"
      >
        <bk-tab-panel
          v-for="(item, index) in panels"
          :key="item.name"
          :name="item.name"
          :label="item.label"
        >
          <UserInfo v-if="index === 0" />
          <DetailsInfo v-if="index === 1" />
        </bk-tab-panel>
      </bk-tab>
    </template> -->
  </MainView>
</template>

<script setup lang="tsx">
import { useMainViewStore } from "@/store/mainView";
import { ref, reactive } from "vue";
import MainView from "@/components/layouts/MainView.vue";
import OrganizationTree from "./tree/OrganizationTree.vue";

const mainViewStore = useMainViewStore();
const state = reactive({
  nodeItem: {
    name: "",
    id: null,
  },
});
const panels = reactive([
  { name: "user_info", label: "人员信息" },
  { name: "details_info", label: "详细信息" },
]);
const active = ref("user_info");

const changeNode = (node: any) => {
  mainViewStore.breadCrumbsTitle = node.title;
  state.nodeItem = node;
};
</script>

<style lang="less" scoped>
.header-left-name {
  font-size: 16px;
  color: #313238;
  margin-right: 10px;
}
.header-left-num {
  border-radius: 11px !important;
}
:deep(.tab-details) {
  height: calc(100vh - 104px);
  .bk-tab-header {
    background: #fff;
    border-bottom: none;
    box-shadow: 0 3px 4px 0 rgba(0, 0, 0, 0.04);
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
