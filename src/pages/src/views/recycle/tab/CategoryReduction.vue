<template>
  <div class="reduction-content">
    <div class="content-table">
      <bk-table :data="selectedList">
        <bk-table-column :label="$t('目录名')" prop="display_name" />
        <bk-table-column :label="$t('还原校验')">
          <template slot-scope="props">
            <p class="restore-check">
              <i :class="props.row.status ? 'success' : 'danger'"></i>
              {{ props.row.status ? $t('可还原') : $t('错误：原组织已不存在') }}
            </p>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作')" width="80">
          <bk-button theme="primary" text @click="$emit('remove')">
            {{ $t('移除') }}
          </bk-button>
        </bk-table-column>
      </bk-table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ReductionIndex',
  props: {
    selectedList: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {};
  },
  methods: {},
};
</script>

<style lang="scss" scoped>
.reduction-content {
  .content-table {
    .table-title {
      display: flex;
      justify-content: space-between;
      height: 42px;
      line-height: 42px;
      background: #F0F1F5;
      border: 1px solid #DCDEE5;
      border-bottom: none;
      padding: 0 22px;
      font-size: 14px;
      color: #63656e;
      .title-left {
        font-weight: 700;
        span {
          color: #3A84FF;
        }
      }
      .title-right {
        span {
          font-weight: 700;
          &:first-child {
            color: #2dcb56;
          }
          &:last-child {
            color: #EA3636;
          }
        }
      }
    }
  }
}
.restore-check {
  i {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 5px;
  }
  .success {
    background: #E5F6EA;
    border: 1px solid #3FC06D;
  }
  .danger {
    background: #FFE6E6;
    border: 1px solid #EA3636;
  }
  span {
    color: #3A84FF;
  }
}
</style>
