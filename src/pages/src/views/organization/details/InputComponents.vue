<!--
  - Tencent is pleased to support the open source community by making Bk-User 蓝鲸用户管理 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
  -
  - License for Bk-User 蓝鲸用户管理:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->
<template>
  <div data-test-id="profileInfo">
    <ul v-if="profileInfoList.length">
      <li class="infor-list" v-for="(item,index) in profileInfoList" :key="index">
        <p class="desc">{{item.name}}
          <span class="star" v-if="item.require">*</span>
          <i class="account-msg icon-user--l"
             v-if="item.key === 'username'"
             v-bk-tooltips="$t('由1-32位字母、数字、下划线(_)、点(.)、减号(-)字符组成，以字母或数字开头')"
          ></i>
          <i class="account-msg icon-user--l"
             v-if="item.key === 'display_name'"
             v-bk-tooltips="item.name + $t('可随时修改，长度为1-32个字符')"
          ></i>
        </p>
        <!-- 输入框 -->
        <div class="input-text">
          <InputPhone v-if="item.key === 'telephone'" :item="item" :edit-status="editStatus" />
          <InputString v-else-if="item.type === 'string' || item.type === 'number'"
                       :item="item"
                       :edit-status="editStatus" />
          <InputDate v-else-if="item.type === 'timer'" :item="item" :edit-status="editStatus" />
          <InputSelect v-else-if="item.type.indexOf('enum') !== -1" :item="item" :edit-status="editStatus" />
        </div>
      </li>
    </ul>
  </div>

</template>

<script>
import InputString from './InputString';
import InputSelect from './InputSelect';
import InputDate from './InputDate';
import InputPhone from './InputPhone';

export default {
  components: {
    InputString,
    InputSelect,
    InputDate,
    InputPhone,
  },
  props: {
    editStatus: {
      type: Boolean,
      required: true,
    },
    profileInfoList: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.infor-list {
  font-size: 14px;
  color: rgba(99, 101, 110, 1);

  &.no-verifica {
    .select-text {
      padding-right: 12px;
    }
  }

  &:nth-child(1),
  &:nth-child(2) {
    .input-text {
      width: 368px;

      .select-text {
        width: 368px;
      }
    }
  }

  .desc {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    padding-top: 17px;
    line-height: 19px;

    .star {
      display: inline-block;
      vertical-align: middle;
      margin-left: 4px;
      color: #fe5c5c;
    }

    .account-msg {
      margin-left: 4px;
      outline: none;
      display: inline-block;
      vertical-align: middle;
      font-size: 16px;
    }
  }

  .input-text {
    position: relative;

    .select-text {
      display: block;
      padding: 0 30px 0 12px;
      width: 460px;

      &.active {
        color: #63656e !important;
      }

      &.disable {
        background-color: #fafbfd;
        cursor: not-allowed;
      }
    }

    .icon-user-exclamation-circle-shape {
      position: absolute;
      right: 10px;
      top: 10px;
      font-size: 16px;
      color: #ea3636;
    }
  }
}
</style>
