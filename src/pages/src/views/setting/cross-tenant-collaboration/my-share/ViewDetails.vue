<template>
  <div class="view-details-wrapper">
    <div class="view-details-content">
      <LabelContent :label="$t('策略名称')"></LabelContent>
      <LabelContent :label="$t('目标公司')"></LabelContent>
      <!-- 一期不做 -->
      <!-- <div class="content-item">
        <span class="item-key">{{ $t('协同范围') }}：</span>
        <div class="item-value-wrapper">
          <span class="count">1个租户，1个组织，2个用户</span>
          <div class="departments-list">
            <div v-for="(item) in departments" :key="item.id">
              <i :class="getNodeIcon(item.type)" />
              <span class="title">{{item.name}}</span>
            </div>
          </div>
        </div>
      </div> -->
      <LabelContent :label="$t('同步范围')"></LabelContent>
      <LabelContent :label="$t('字段预览')">
        <bk-table
          class="mt-[8px]"
          :data="tableData"
          :border="['outer']"
          show-overflow-tooltip>
          <template #empty>
            <Empty
              :is-data-empty="isDataEmpty"
              :is-data-error="isDataError"
              @handleUpdate="handleUpdate"
            />
          </template>
          <bk-table-column prop="username" :label="$t('用户名')" />
          <bk-table-column prop="full_name" :label="$t('中文名')" />
          <bk-table-column prop="email" :label="$t('邮箱')" />
          <bk-table-column prop="phone" :label="$t('手机号')" />
          <bk-table-column prop="organization" :label="$t('组织')" />
        </bk-table>
      </LabelContent>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, onMounted, ref } from 'vue';

import Empty from '@/components/Empty.vue';
import LabelContent from '@/components/layouts/LabelContent.vue';

defineProps({
  data: {
    type: Object,
    default: {},
  },
});

// 一期不做
// const departments = ref([
//   { type: 'tenant', name: '租户' },
//   { type: 'department', name: '组织' },
//   { type: 'username', name: '用户' },
// ]);

// const getNodeIcon = (type: string) => {
//   switch (type) {
//     case 'tenant':
//       return 'user-icon icon-homepage';
//     case 'department':
//       return 'bk-sq-icon icon-file-close';
//     default:
//       return 'bk-sq-icon icon-personal-user';
//   }
// };

const tableData = ref([]);
const isDataEmpty = ref(false);
const isDataError = ref(false);

onMounted(() => {
  isDataEmpty.value = false;
  isDataError.value = false;
  setTimeout(() => {
    if (tableData.value.length === 0) {
      isDataEmpty.value = true;
    }
  }, 1000);
});
</script>

<style lang="less" scoped>
.view-details-wrapper {
  padding: 20px 40px;

  .view-details-content {
    .content-item {
      display: flex;
      width: 100%;
      line-height: 40px;

      .item-key {
        display: inline-block;
        min-width: 100px;
        margin-right: 8px;
        overflow: hidden;
        font-size: 14px;
        color: #63656e;
        text-align: right;
      }

      .item-value {
        display: inline-block;
        width: 100%;
        overflow: hidden;
        font-size: 14px;
        color: #313238;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .item-list {
        padding: 12px 16px;
        font-size: 14px;
        background: #F5F7FA;
        border-radius: 2px;

        p {
          line-height: 28px;
          color: #313238;

          span {
            color: #979BA5;
          }
        }
      }

      .item-value-wrapper {
        .count {
          display: inline-block;
          font-size: 14px;
          line-height: 40px;
          color: #313238;
        }

        .departments-list {
          width: 320px;
          padding: 8px 12px;
          background: #F5F7FA;
          border-radius: 2px;

          div {
            display: flex;
            align-items: center;
            font-size: 14px;
            line-height: 36px;

            i {
              margin-right: 12px;
              font-size: 18px;
              color: #A3C5FD;
            }
          }
        }
      }
    }
  }
}
</style>
