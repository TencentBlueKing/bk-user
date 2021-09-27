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
  <div class="info-set-wrapper">
    <bk-button theme="primary" class="king-button"
               v-cursor="{ active: Boolean(authData) }"
               @click="addField">
      {{$t('添加字段')}}
    </bk-button>

    <div class="table-content-wrapper" ref="userInfoField">
      <div class="thead-container table-container" data-test-id="list_thInfo">
        <table>
          <thead>
            <tr>
              <th style="width: 42px;"></th>
              <th>{{$t('字段名称')}}</th>
              <th>{{$t('英文标识')}}</th>
              <th>{{$t('字段类型')}}</th>
              <th>{{$t('必填')}}</th>
              <th>{{$t('唯一')}}</th>
              <th>{{$t('可编辑')}}</th>
              <th>{{$t('操作')}}</th>
            </tr>
          </thead>
        </table>
      </div>
      <div class="tbody-container table-container" v-bkloading="{ isLoading: basicLoading }">
        <div class="scroll-container" data-test-id="list_fieldsData">
          <table>
            <tbody id="table-list">
              <tr v-for="item in fieldsList" :key="item.id" :id="item.id">
                <td style="width: 42px;" class="handle">
                  <div class="td-container">
                    <i class="move-btn icon-user-uniE921"></i>
                  </div>
                </td>
                <td>
                  <div class="td-container">
                    <span class="name">{{item.name}}</span><span class="sign" v-if="item.builtin">{{$t('内置')}}</span>
                  </div>
                </td>
                <td>
                  <div class="td-container">
                    <span class="name">{{item.key}}</span>
                  </div>
                </td>
                <td>
                  <div class="td-container">
                    <span class="name">{{switchType(item.type)}}</span>
                  </div>
                </td>
                <td>
                  <div class="td-container">
                    <i class="user-icon icon-duihao-i" v-if="item.require"></i>
                  </div>
                </td>
                <td>
                  <div class="td-container">
                    <i class="user-icon icon-duihao-i" v-if="item.unique"></i>
                  </div>
                </td>
                <td>
                  <div class="td-container">
                    <i class="user-icon icon-duihao-i" v-if="item.editable"></i>
                  </div>
                </td>
                <td>
                  <div class="td-container">
                    <!-- 内置字段（除了potion）不可编辑 -->
                    <span v-if="item.builtin && item.key !== 'position'"
                          class="name operate gray" v-bk-tooltips="editTips">{{$t('编辑')}}
                    </span>
                    <span v-else class="name operate" v-cursor="{ active: Boolean(authData) }"
                          @click="editorField(item)">{{$t('编辑')}}
                    </span>
                    <span v-if="item.builtin" class="name operate gray" v-bk-tooltips="deleteTips">{{$t('删除')}}</span>
                    <span v-else class="name operate" v-cursor="{ active: Boolean(authData) }"
                          @click="deleteField(item)">{{$t('删除')}}
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 添加字段的侧边栏 -->
    <bk-sideslider class="king-sideslider"
                   :show-mask="false"
                   :quick-close="false"
                   :style="{ visibility: isHideBar ? 'hidden' : 'visible' }"
                   :is-show.sync="fieldData.isShow"
                   :title="fieldData.title"
                   :width="fieldData.width">
      <div slot="content" class="member-content" v-if="fieldData.isShow">
        <FieldsAdd
          :set-type="setType"
          :is-show.sync="fieldData.isShow"
          :current-editor-data="currentEditorData"
          @hideBar="hideBar"
          @showBar="showBar"
          @getFields="getFields" />
      </div>
    </bk-sideslider>
    <!-- table basic loading 时的遮罩层 -->
    <div v-show="basicLoading" class="loading-cover" @click.stop></div>
  </div>
</template>

<script>
import FieldsAdd from './FieldsAdd';

import Sortable from 'sortablejs';

export default {
  components: {
    FieldsAdd,
  },
  data() {
    return {
      editTips: this.$t('该内置字段，不支持修改'),
      deleteTips: this.$t('内置字段，不能删除'),
      clickSecond: false,
      fieldData: {
        isShow: false,
        title: this.$t('添加字段'),
        width: 520,
      },
      // 点击保存时打开 loading，临时在样式上隐藏侧边栏
      isHideBar: false,
      // 侧边栏区分添加字段、编辑字段
      setType: '',
      // 字段List
      fieldsList: [],
      currentEditorData: {},
      isRepeatClick: false,
      basicLoading: true,
      authData: null,
    };
  },
  mounted() {
    this.$nextTick(async () => {
      // 初始化渲染用户信息字段
      await Promise.all([this.initField(), this.getAuthInfo()]);
      this.$store.commit('updateInitLoading', false);
      const dragWrapper = document.getElementById('table-list');
      Sortable.create(dragWrapper, {
        handle: '.handle',
        group: dragWrapper,
        ghostClass: 'blue-background-class',
        animation: 150,
        onUpdate: (event) => {
          this.changeFieldOrder(event.item.id, event.newIndex + 1);
        },
      });
    });
  },
  methods: {
    // 字段类型的转换
    switchType(type) {
      if (!type) {
        console.warn('错误的字段类型');
      }
      const typeObj = {
        multi_enum: this.$t('枚举'),
        string: this.$t('字符串'),
        bool: this.$t('布尔值'),
        number: this.$t('数值'),
        timer: this.$t('日期'),
        one_enum: this.$t('枚举'),
      };
      return typeObj[type];
    },
    // 拖拽
    changeFieldOrder(id, index) {
      try {
        this.$store.dispatch('setting/dragFields', { id, index });
      } catch (e) {
        console.warn(e);
      }
    },
    // 初始化字段
    async initField() {
      try {
        this.basicLoading = true;
        const res = await this.$store.dispatch('setting/getFields');
        const fieldsListShadow = [];
        res.data.forEach((item) => {
          if (item.type === 'one_enum' || item.type === 'multi_enum') {
            // 显示对应的报错信息
            item.options.forEach((option) => {
              option.isErrorValue = false;
            });
          }
          fieldsListShadow.push(item);
        });
        this.fieldsList = fieldsListShadow;
      } catch (e) {
        console.warn(e);
      } finally {
        this.basicLoading = false;
      }
    },
    async getAuthInfo() {
      try {
        await this.$store.dispatch('setting/getAuthInfo');
      } catch (e) {
        console.warn(e);
        if (e.response.status === 403) {
          this.authData = e.response.data;
        }
      }
    },
    addField() {
      if (this.authData) {
        this.$store.commit('updateNoAuthData', {
          requestId: '',
          data: this.authData,
        });
        return;
      }
      this.currentEditorData = {};
      this.fieldData.title = this.$t('添加字段');
      this.setType = 'add';
      this.fieldData.isShow = true;
    },
    // 更新字段
    getFields() {
      this.initField();
      this.fieldData.isShow = false;
      setTimeout(() => {
        this.isHideBar = false;
      }, 300);
    },
    // 编辑字段
    editorField(item) {
      if (this.authData) {
        this.$store.commit('updateNoAuthData', {
          requestId: '',
          data: this.authData,
        });
        return;
      }

      this.currentEditorData = item;
      this.fieldData.title = this.$t('编辑字段');
      this.setType = 'edit';
      this.fieldData.isShow = true;
    },
    // 删除字段
    deleteField(item) {
      if (this.authData) {
        this.$store.commit('updateNoAuthData', {
          requestId: '',
          data: this.authData,
        });
        return;
      }

      this.$bkInfo({
        title: this.$t('确认要删除吗？'),
        confirmFn: () => {
          // 需要调用接口 和后台一起删除
          if (this.clickSecond) {
            return;
          }
          this.clickSecond = true;
          this.basicLoading = true;
          // eslint-disable-next-line no-unused-vars
          this.$store.dispatch('setting/deleteFields', { id: item.id }).then((res) => {
            this.messageSuccess(this.$t('删除字段成功'));
            this.initField();
          })
            .catch((e) => {
              console.warn(e);
              this.basicLoading = false;
            })
            .finally(() => {
              this.clickSecond = false;
            });
        },
      });
    },
    hideBar() {
      this.isHideBar = true;
      this.basicLoading = true;
    },
    showBar() {
      this.isHideBar = false;
      this.basicLoading = false;
    },
  },
};
</script>

<style lang="scss" scoped>
    @import '../../scss/mixins/scroller';

    .king-sideslider {
      background-color: rgba(0, 0, 0, .6);
    }

    .blue-background-class {
      background: #e1ecff;
    }
    // 公共样式
    .checkbox {
      display: inline-block;
      vertical-align: middle;
      width: 14px;
      height: 14px;
      outline: none;
      visibility: visible;
      cursor: pointer;
      background: #fff url('../../images/icon.png') 0 -95px;
      appearance: none;

      &:checked {
        background-position: -33px -95px;
      }
    }

    .info-set-wrapper {
      height: 100%;

      > .king-button {
        margin: 20px;
        width: 100px;
      }

      .member-content {
        height: 100%;
        padding-bottom: 20px;
      }

      > .table-content-wrapper {
        margin: 0 20px;
        height: calc(100% - 85px);
        border: 1px solid #e6e6e6;

        > .table-container {
          // table 公用样式
          table {
            color: #888;
            width: 100%;
            table-layout: fixed;
            border: none;
            border-collapse: collapse;
            font-size: 12px;

            tr {
              height: 42px;
              border-bottom: 1px solid #dcdee5;
            }

            td {
              font-size: 12px;
            }
          }
        }

        > .thead-container {
          height: 42px;

          > table {
            background: #fafbfd;

            th {
              padding: 0 10px;
              text-align: left;
              border: none;
              color: #666;

              &.hidden {
                display: none;
              }
            }
          }
        }

        > .tbody-container {
          height: calc(100% - 42px);

          > .scroll-container {
            height: 100%;
            overflow: auto;

            @include scroller($backgroundColor: #e6e9ea, $width: 4px);

            > table > tbody > tr {
              &:hover {
                background: #e1ecff;
              }

              > td {
                padding: 0 10px;
                border: none;

                &.hidden {
                  display: none;
                }

                > .td-container {
                  overflow: hidden;
                  text-overflow: ellipsis;
                  white-space: nowrap;
                  font-size: 12px;
                }
              }
            }
          }

          .handle {
            cursor: move;
            position: relative;

            .move-btn {
              font-size: 16px;
              position: absolute;
              top: 50%;
              left: calc(50% + 5px);
              transform: translate(-50%, -50%);
            }
          }

          .sign {
            margin-left: 8px;
            padding: 0 4px;
            height: 15px;
            font-size: 12px;
            font-weight: 400;
            color: rgba(255, 255, 255, 1);
            line-height: 15px;
            text-align: center;
            border-radius: 2px;
            background: #c4c6cc;
          }

          .icon-duihao-i {
            padding-left: 4px;
            font-size: 20px;
            font-weight: bold;
            color: #2dcb56;
          }

          .operate {
            color: #3a84ff;
            cursor: pointer;
            outline: none;

            &:last-child {
              margin-left: 10px;
            }

            &.gray {
              color: #c4c6cc;
              cursor: not-allowed;
            }
          }
        }
      }
    }
</style>
