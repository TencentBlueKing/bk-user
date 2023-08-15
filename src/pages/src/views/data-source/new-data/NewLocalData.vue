<template>
  <div>
    <MainBreadcrumbsDetails>
      <template #tag>
        <bk-tag>
          <template #icon>
            <i :class="typeText.icon" />
          </template>
          {{ typeText.name }}
        </bk-tag>
      </template>
    </MainBreadcrumbsDetails>
  </div>
</template>

<script setup lang="tsx">
import MainBreadcrumbsDetails from "@/components/layouts/MainBreadcrumbsDetails.vue";
import { useRoute } from "vue-router";
import { computed } from "vue";

const route = useRoute();

// 当前面包屑展示文案
const typeText = computed(() => {
  switch (route.params.type) {
    case "local":
      return {
        name: "本地",
        icon: "user-icon icon-wechat",
      };
  }
});
</script>

<style lang="less" scoped></style>
