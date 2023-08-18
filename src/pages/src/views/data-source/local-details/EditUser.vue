<template>
  <div class="edit-user-wrapper">
    <bk-form
      ref="formRef"
      class="add-user-form"
      form-type="vertical"
      :model="formData"
      :rules="rules"
    >
      <bk-form-item
        style="width: 440px;"
        label="用户名"
        property="username"
        required
      >
        <bk-input
          v-model="formData.username"
          placeholder="数字、下划线(_)、点(.)、减号(-)字符组成，以字母或数字开头"
        />
      </bk-form-item>
      <bk-form-item
        style="width: 440px;"
        label="全名"
        property="full_name"
        required
      >
        <bk-input
          v-model="formData.full_name"
          placeholder="全名可随时修改"
        />
      </bk-form-item>
      <BkUpload
        theme="picture"
        with-credentials
        :multiple="false"
        :files="files"
        :handle-res-code="handleRes"
        :url="'https://jsonplaceholder.typicode.com/posts/'"
      />
      <bk-form-item label="邮箱" property="email" required>
        <bk-input v-model="formData.email" placeholder="请输入" />
      </bk-form-item>
      <bk-form-item label="手机号" property="telphone" required>
        <div class="input-text">
          <bk-input
            ref="inputRef"
            v-model="formData.telphone"
            placeholder="请输入"
            type="number"
          />
        </div>
      </bk-form-item>
      <div class="form-item-flex">
        <bk-form-item label="所属组织" property="department_name" required>
          <bk-select v-model="formData.department_name">
            <bk-option value="1" label="" />
            <bk-option value="2" label="" />
          </bk-select>
        </bk-form-item>
        <bk-form-item label="直属上级" property="leader" required>
          <bk-select v-model="formData.leader">
            <bk-option value="1" label="" />
            <bk-option value="2" label="" />
          </bk-select>
        </bk-form-item>
      </div>
      <div class="form-item-flex">
        <bk-form-item label="在职状态" required>
          <bk-radio-group>
            <bk-radio label="在职" />
            <bk-radio label="离职" />
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item label="职务">
          <bk-radio-group>
            <bk-radio label="员工" />
            <bk-radio label="组长" />
          </bk-radio-group>
        </bk-form-item>
      </div>
      <div class="form-item-flex">
        <bk-form-item
          label="账号过期时间"
          property="account_expiration_time"
          required
        >
          <bk-date-picker
            type="datetime"
            v-model="formData.account_expiration_time"
            clearable
          />
        </bk-form-item>
        <bk-form-item
          label="密码过期时间"
          property="password_expiration_time"
          required
        >
          <bk-date-picker
            type="datetime"
            v-model="formData.password_expiration_time"
            clearable
          />
        </bk-form-item>
      </div>
    </bk-form>
    <div class="footer">
      <bk-button theme="primary" @click="handleSubmit">
        提交
      </bk-button>
      <bk-button @click="() => $emit('handleCancelEdit')">
        取消
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, toRefs } from "vue";

const formRef = ref("");
const inputRef = ref("");
const formData = ref({
  username: "",
  full_name: "",
  department_name: "",
  leader: "",
  email: "",
  telphone: "",
  account_expiration_time: "",
  password_expiration_time: "",
});
let iti = null;
const files: any = [];
const rules = {
  username: [
    {
      validator: (value: string) => value.length > 2,
      message: "姓名长度不能小于2",
      trigger: "blur",
    },
  ],
};
const handleRes = (response: any) => {
  if (response.id) {
    return true;
  }
  return false;
};

const handleSubmit = () => {}
</script>

<style lang="less" scoped>
.edit-user-wrapper {
  position: relative;
  overflow-x: hidden;

  .add-user-form {
    position: relative;
    padding: 28px 40px 60px;
    .bk-upload {
      position: absolute;
      top: 54px;
      right: 32px;
    }
    .form-item-flex {
      display: flex;
      justify-content: space-between;
      .bk-form-item {
        width: 268px;
        .input-text {
          position: relative;
        }
      }
    }
  }
  .footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    height: 48px;
    line-height: 48px;
    padding: 0 24px;
    background: #FAFBFD;
    box-shadow: 0 -1px 0 0 #DCDEE5;
    .bk-button {
      width: 88px;
      margin-right: 8px;
    }
  }
}
</style>
