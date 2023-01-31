<!--
  - TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
  - Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
  - Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at http://opensource.org/licenses/MIT
  - Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
  - an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
  - specific language governing permissions and limitations under the License.
  -->
<template>
  <div data-test-id="profileInfo">
    <ul v-if="profileInfoList.length">
      <li class="infor-list" v-for="(item,index) in profileInfoList" :key="index">
        <p class="desc">{{item.name}}
          <span class="star" v-if="item.require">*</span>
          <i
            class="account-msg icon-user--l"
            v-if="item.key === 'username'"
            v-bk-tooltips="usernameTips"
          ></i>
          <i
            class="account-msg icon-user--l"
            v-if="item.key === 'display_name'"
            v-bk-tooltips="item.name + $t('可随时修改，长度为1-32个字符')"
          ></i>
        </p>
        <!-- 输入框 -->
        <div class="input-text">
          <InputPhone v-if="item.key === 'telephone'" :item="item" :edit-status="editStatus" />
          <InputDate
            v-else-if="item.key.includes(dateKey) || item.type === 'timer'"
            :item="item" :edit-status="editStatus" />
          <InputString
            v-else-if="item.type === 'string' || item.type === 'number'"
            :item="item"
            :edit-status="editStatus" />
          <InputSelect
            v-else-if="item.type.indexOf('enum') !== -1"
            :item="item"
            :edit-status="editStatus"
            :status-map="statusMap" />
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
    statusMap: {
      type: Object,
      default: {},
    },
  },
  data() {
    return {
      usernameTips: {
        width: 500,
        placement: 'top-middle',
        content: this.$t('由1-32位字母、数字、下划线(_)、点(.)、减号(-)字符组成，以字母或数字开头'),
      },
      dateKey: ['account_expiration_date'],
    };
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
.tips-style {
  color: #ea3636;
}
</style>
