<template>
  <ul class="details-content">
    <li>
      <div class="details-content-info">
        <div
          class="details-content-item"
          v-for="(item, index) in basicData"
          :key="index"
        >
          <span class="details-content-key">{{ userMap[item.key] }}：</span>
          <span class="details-content-value">{{ item.value }}</span>
        </div>
      </div>
      <img
        v-if="tenantsData.logo"
        class="user-logo"
        :src="tenantsData.logo"
        alt=""
      />
      <img v-else class="user-logo" src="../../../images/avatar.png" alt="" />
    </li>
  </ul>
</template>

<script setup lang="tsx">
import { reactive, computed } from "vue";

const props = defineProps({
  tenantsData: {
    type: Object,
    default: {},
  },
});

const managersList = computed(() =>
  props.tenantsData.managers.filter((item) => item.id)
);

const columns = [
  {
    label: "用户名",
    field: "username",
  },
  {
    label: "姓名",
    field: "full_name",
    render: ({ cell }: { cell: string }) => <span>{cell || "--"}</span>,
  },
  {
    label: "邮箱",
    field: "email",
  },
  {
    label: "手机号",
    field: "phone",
  },
];

const userMap = {
  user_id: "用户ID",
  user_name: "用户名",
  full_name: "全名",
  email: "邮箱",
  phone: "手机号",
  department: "所属组织",
  leader: "直属上级",
  status: "在职状态",
  position: "职务",
  account_expiration_date: "账号过期时间",
  password_expiration_date: "密码过期时间",
}

const basicData = reactive([
  {
    key: "user_id",
    value: "123",
  },
  {
    key: "user_name",
    value: "aaa",
  },
  {
    key: "full_name",
    value: "bbb",
  },
  {
    key: "email",
    value: "124567345@qq.com",
  },
  {
    key: "phone",
    value: "15756734555",
  },
  {
    key: "department",
    value: "总公司",
  },
  {
    key: "leader",
    value: "Morty Zhang（李三）",
  },
  {
    key: "status",
    value: "在职",
  },
  {
    key: "position",
    value: "产品经理",
  },
  {
    key: "account_expiration_date",
    value: "2023-10-10",
  },
  {
    key: "password_expiration_date",
    value: "2023-10-10",
  },
]);
</script>

<style lang="less" scoped>
.details-content {
  padding: 0 40px;
  li {
    list-style: none;
    padding: 20px 0;
    border-bottom: 1px solid #dcdee5;
    position: relative;
    .details-content-info {
      width: calc(100% - 100px);
      .details-content-item {
        line-height: 40px;
        width: 100%;
        display: flex;
        .details-content-key {
          font-size: 14px;
          color: #63656e;
          display: inline-block;
          width: 100px;
          text-align: right;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .details-content-value {
          font-size: 14px;
          color: #313238;
          display: inline-block;
          width: calc(100% - 100px);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          vertical-align: top;
        }
      }
    }
    .user-logo {
      position: absolute;
      top: 20px;
      right: 0;
      width: 96px;
      height: 96px;
      border: 1px dashed #c4c6cc;
      object-fit: contain;
    }
  }
  li:last-child {
    border-bottom: none;
  }
}
</style>
