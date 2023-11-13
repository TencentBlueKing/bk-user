<template>
  <ul class="details-content">
    <li>
      <div class="details-content-title">基本信息</div>
      <div class="details-content-info">
        <div
          class="details-content-item"
          v-for="(item, index) in basicData"
          :key="index"
        >
          <span class="details-content-key">{{ item.name }}：</span>
          <span class="details-content-value">{{ item.value }}</span>
        </div>
      </div>
      <img v-if="tenantsData.logo" class="user-logo" :src="tenantsData.logo" alt="">
      <img v-else class="user-logo" src="@/images/avatar.png" alt="">
    </li>
    <li>
      <div class="details-content-title">管理员</div>
      <bk-table
        class="details-content-table"
        :data="managersList"
        show-overflow-tooltip
      >
        <bk-table-column prop="username" label="用户名" />
        <bk-table-column prop="full_name" label="姓名" />
        <bk-table-column prop="email" label="邮箱" />
        <bk-table-column prop="phone" label="手机号" />
      </bk-table>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { computed, defineProps, reactive } from 'vue';

const props = defineProps({
  tenantsData: {
    type: Object,
    default: {},
  },
});

const managersList = computed(() => props.tenantsData.managers.filter(item => item.id));

const basicData = reactive([
  {
    name: '租户名称',
    value: props.tenantsData.name,
  },
  {
    name: '租户ID',
    value: props.tenantsData.id,
  },
  {
    name: '人员数量',
    value: props.tenantsData.feature_flags.user_number_visible ? '显示' : '隐藏',
  },
]);
</script>

<style lang="less" scoped>
.details-content {
  padding: 0 40px;

  li {
    position: relative;
    padding: 20px 0;
    list-style: none;
    border-bottom: 1px solid #dcdee5;

    .details-content-title {
      font-size: 14px;
      font-weight: 700;
      line-height: 40px;
      color: #63656e;
    }

    .details-content-info {
      width: calc(100% - 92px);

      .details-content-item {
        display: flex;
        width: 100%;
        line-height: 40px;

        .details-content-key {
          display: inline-block;
          width: 100px;
          font-size: 14px;
          color: #63656e;
          text-align: right;
        }

        .details-content-value {
          display: inline-block;
          width: calc(100% - 100px);
          overflow: hidden;
          font-size: 14px;
          color: #313238;
          text-overflow: ellipsis;
          white-space: nowrap;
          vertical-align: top;
        }
      }
    }

    .user-logo {
      position: absolute;
      top: 60px;
      right: 0;
      width: 72px;
      height: 72px;
      border: 1px dashed #c4c6cc;
      object-fit: contain;
    }
  }

  li:last-child {
    border-bottom: none;
  }
}

.details-content-table {
  margin-top: 16px;

  :deep(.bk-fixed-bottom-border) {
    border-top: none;
  }
}
</style>
