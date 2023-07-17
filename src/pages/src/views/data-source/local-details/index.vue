<template>
  <div>
    <MainBreadcrumbsDetails :subtitle="subtitle">
      <template #tag>
        <bk-tag>
          <template #icon>
            <i :class="typeText.icon" />
          </template>
          {{ typeText.name }}
        </bk-tag>
      </template>
    </MainBreadcrumbsDetails>
    <bk-tab
      v-model:active="activeKey"
      type="unborder-card"
      ext-cls="tab-details"
    >
      <bk-tab-panel
        v-for="item in panels"
        :key="item.name"
        :name="item.name"
        :label="item.label"
      >
        <UserInfo v-if="activeKey === 'user'" />
        <PswInfo v-else />
      </bk-tab-panel>
    </bk-tab>
  </div>
</template>

<script setup lang="ts">
import MainBreadcrumbsDetails from "@/components/layouts/MainBreadcrumbsDetails.vue";
import { useRoute } from "vue-router";
import { ref, reactive, computed } from "vue";
import UserInfo from "./UserInfo.vue";
import PswInfo from "./PswInfo.vue";

const route = useRoute();

// 当前面包屑展示文案
const subtitle = computed(() => route.params.name);
const typeText = computed(() => {
  switch (route.params.type) {
    case "local":
      return {
        name: "本地",
        icon: "user-icon icon-wechat",
      };
  }
});

const activeKey = ref("user");
const panels = reactive([
  { name: "user", label: "用户信息" },
  { name: "account", label: "账密信息" },
]);
</script>

<style lang="less">
.main-breadcrumbs-details {
  box-shadow: none;
}
</style>
<style lang="less">
.congfig {
  display: flex;
}
</style>
