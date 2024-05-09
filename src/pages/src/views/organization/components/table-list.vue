<template>
    <div class="organization-table px-[24px] py-[24px]">
        <div class="table-search mb-[16px]">
            <bk-button v-if="isTenant && isLocalDataSource" @click="() => importDialogShow = true">
                <Upload class="mr-[8px] text-[16px]" />{{ $t('导入') }}
            </bk-button>
            <bk-button theme="primary" class="mr-[10px]" @click="fastInputHandle"
                v-if="!isTenant">
                <i class="user-icon icon-add-2 mr8" />
                {{ $t('快速录入') }}
            </bk-button>
            <bk-button v-if="!isTenant">{{ $t('拉取已有用户') }}</bk-button>
            <bk-checkbox class="ml-[16px] h-[32px]"
                :label="$t('仅显示本级用户')"
                v-model="recursive"
                @change="initTenantsUserList"
            />
            <bk-input
                class="header-right"
                v-model="keyword"
                :placeholder="$t('搜索用户名、全名')"
                type="search"
                clearable
                @enter="handleEnter"
                @clear="handleClear"
            />
        </div>
        <bk-table
            class="organization-table-main"
            height="100%"
            :border="['outer']"
            :columns="columns"
            :data="tableData"
            :pagination="pagination"
            v-bkloading="{ loading: isLoading }"
            row-hover="auto"
            @select="handleSelectTable"
            @select-all="handleSelectAll"
        >
            <template #prepend v-if="!isTenant && selectList.length">
                <div class="table-total">
                    <span>当前已选择 <b>{{selectList.length}}</b> 条数据，可以批量</span>
                    <label
                        v-for="(item, index) in operationList.filter(item => item.isShow)"
                        :key="index"
                        class="table-operate ml-[12px]"
                        @click="() => {
                            currentHandle = item;
                            item.handle(true);
                        }"
                    >{{$t(item.label)}}</label>   
                </div>
            </template>
            <template
                v-for="(column, ind) in columnsRender"
                :key="column.label"
            >
                <bk-table-column
                    :label="column.label"
                    :type="column.type"
                    :field="column.field"
                    :width="column.width"
                    :index="ind"
                >
                <template #default="{ row, column, index }">
                    <span v-if="column?.field === 'username'"
                        @click="() => editInfoHandle(row)">
                        <label class="table-operate">{{row[column?.field]}}</label>
                    </span>
                    <span v-else-if="column?.field === 'status'" class="status-main">
                        <label :class="`status-label ${row.status}`"></label>
                        {{statusEnum[row.status]}}
                    </span>
                    <span v-else-if="column?.field === 'operation'">
                        <label class="table-operate" @click="() => editInfoHandle(row, true)">{{$t('编辑')}}</label>
                        <bk-popover
                            ext-cls="operate-popover"
                            :ref="(el) => setItemRef(el, `dropdownRef${index}`)"
                            theme="light"
                            trigger="click"
                            :arrow="false"
                            placement="bottom"
                            allowHtml
                        >
                            <template #content>
                                <ul class="operate-menu-list">
                                    <li
                                        class="operate-list-item"
                                        v-for="(item, ind) in rowOperation"
                                        :key="ind"
                                        @click="() => {
                                            detailsInfo = row;
                                            dropdownRefs[`dropdownRef${index}`]?.hide();
                                            item.handle(false, row);
                                        }"
                                    >
                                        {{ operationLabel(item, row) }}
                                    </li>
                                </ul>
                            </template>
                            <div class="operate-popover-main">
                                <i class="user-icon icon-more ml8" />
                            </div>
                        </bk-popover>
                    </span>
                    <label v-else>{{formatField(row[column?.field])}}</label>
                </template>
                </bk-table-column>
            </template>
        </bk-table>
    </div>
    <!-- 移动至组织/添加至组织弹框 -->
    <bk-dialog
      :is-show="moveDialogShow"
      :title="currentHandle.label"
      :theme="'primary'"
      :size="'normal'"
      @closed="() => moveDialogShow = false"
      @confirm="() => confirmOperations()"
    >
        <bk-form
            class="example"
            form-type="vertical"
        >
            <bk-form-item :label="$t('选择组织')">
                <bk-select
                    v-model="selectedValue"
                    class="bk-select"
                    filterable
                    multiple
                    auto-focus
                    :clearable="false"
                    @select="handleSelect"
                >
                    <bk-option
                        v-for="(item, index) in dataSource"
                        :id="item.id"
                        :key="index"
                        :name="item.name"
                        :disabled="item.disabled"
                    />
                </bk-select>
            </bk-form-item>
        </bk-form>
    </bk-dialog>
    <!-- 重置密码弹框 -->
    <bk-dialog
      :is-show="passwordDialogShow"
      :title="$t('重置密码')"
      :theme="'primary'"
      :size="'normal'"
      :height="200"
      @closed="() => passwordDialogShow = false"
      @confirm="resetPasswordConfirm"
    >
        <bk-form
            class="example"
            form-type="vertical"
        >
            <bk-form-item :label="$t('新密码')" required>
                <bk-input :style="{width: '80%'}"
                    v-model="password"
                    type="password"
                    :placeholder="$t('至少六位，需保护英文、数字与符号中的两种')"
                    clearable
                />
                <bk-button outline theme="primary" @click="randomPasswordHandle">{{$t('随机生成')}}</bk-button>
            </bk-form-item>
        </bk-form>
    </bk-dialog>
    <!-- 快速录入弹框 -->
    <FastInputDialog v-model:isShow="fastInputDialogShow"
      @success="fastInputSuccess" />
    <!-- 编辑用户 -->
    <bk-sideslider
      :width="640"
      :is-show="editDetailsShow"
      :title="isDetailSlider ? $t('编辑用户') : $t('用户详情')"
      :before-close="handleBeforeClose"
      quick-close
    >
      <EditDetails
        v-if="isDetailSlider"
        :details-info="detailsInfo"
        @updateUsers="updateUsers"
        @handleCancelEdit="handleCancelEdit" />
      <ViewUser :user-data="detailsInfo" v-else />
    </bk-sideslider>
    <!-- 导入弹框 -->
    <ImportDialog
      v-model:isShow="importDialogShow"
      :currentDataSourceId="dataSourceId"
      @success="initTenantsUserList"
    />
  </template>
  
<script setup lang="ts">
  import { ref, reactive, computed, inject, onMounted, onBeforeMount, watch } from 'vue';
  import { InfoBox, Message } from 'bkui-vue';
  import { Upload } from 'bkui-vue/lib/icon';
  import { t } from '@/language/index';
  import FastInputDialog from './fast-input-dialog.vue';
  import EditDetails from '../../virtual-account/EditDetails.vue';
  import ImportDialog from '@/components/import-dialog/import-dialog.vue'
//   import EditDetailsInfo from '../details/EditDetailsInfo.vue'
  import ViewUser from '../details/ViewUser.vue';
  import { randomPasswords } from '@/http';
  import {
    getTenantsUserList,
    getFieldsTips,
    resetTenantsUserPassword,
    updateTenantsUserStatus,
    delTenantsUser,
    batchDeleteUser,
    departmentsList,
    batchDelete,
    batchUpdate,
    batchCreate,
    batchDelUpdate
  } from '@/http/organizationFiles';
  import useAppStore from '@/store/app';

  const appStore = useAppStore();
  const recursive = ref(true);
  const isLoading = ref(false);
  const editLeaveBefore = inject('editLeaveBefore');
  const editDetailsShow = ref(false);
  const dropdownRefs = ref({});
  const keyword = ref('');
  const selectedValue = ref([]);
  const isDetailSlider = ref(false);
  /** 是否为租户层级 */
  const isTenant = computed(() => {
    return appStore.currentOrg?.id === appStore.currentTenant?.id;
  });
  const detailsInfo = ref({});
  const selectList = ref([]);
  const password = ref('');
  const dataSource = ref([
    {
      value: 'climbing',
      label: '爬山',
    },
    {
      value: 'running',
      label: '跑步',
    }]);
  const moveDialogShow = ref(false);
  const currentHandle = ref({});
  const passwordDialogShow = ref(false);
  const fastInputDialogShow = ref(false);
  const importDialogShow = ref(false);
  /** 是否为本地数据源 */
  const isLocalDataSource = computed(() => {
    return appStore.currentTenant?.data_source?.plugin_id === 'local';
  });
  const dataSourceId = computed(() => {
    return appStore.currentTenant?.data_source?.id;
  })
  const defaultOperation = reactive([
    {
      label: t('删除'),
      isShow: isLocalDataSource.value,
      handle: (isBatch, item) => {
          InfoBox({
            title: isBatch ? t('确认批量删除用户？') : t('确认删除用户？'),
            height: 184,
            onConfirm: async () => {
                if (isBatch) {
                    await batchDeleteUser(getBatchUserIds(true));
                    selectList.value = [];
                } else {
                    await delTenantsUser(detailsInfo.value.id);
                }
                initTenantsUserList();
            },
          });
      }
    },
  ]);
  const operationList = reactive([...[
    {
      label: t('移出当前组织'),
      isShow: true,
      handle: () => {
        InfoBox({
            title: t('确认将选中的用户移出当前组织'),
            height: 184,
            onConfirm: async () => {
                const params = {
                    user_ids: getBatchUserIds(),
                    source_department_id: appStore.currentOrg.id
                }
                await batchDelete(params);
                moveDialogShow.value = false;
                initTenantsUserList();
            }
        });
      }
    },
    {
      label: t('移至目标组织'),
      isShow: true,
      confirmFn: batchUpdate,
      handle: () => {
        handleOperations(true, t('移至目标组织'));
      }
    },    
    {
      label: t('追加目标组织'),
      isShow: true,
      confirmFn: batchCreate,
      handle: () => {
        handleOperations(true, t('追加目标组织'));
      }
    },
    {
      label: t('清空并加入组织'),
      isShow: true,
      confirmFn: batchDelUpdate,
      handle: () => {
        handleOperations(false, t('清空并加入组织'));
      }
    }, 
  ], ...defaultOperation]);
  const rowOperation = reactive([...[       
    {
      label: t('停用'),
      key: 'status',
      handle: (isBatch, item) => {
        const isEnabled = item.status === 'enabled';
        InfoBox({
            title: isEnabled ? t('确定停用当前组织架构') : t('确定启用当前组织架构'),
            subTitle: isEnabled ? t('停用后，用户将无法看到该组织架构信息') : t('启用后，用户将看到该组织架构信息'),
            height: 184,
            onConfirm: async () => {
                await updateTenantsUserStatus(item.id);
                initTenantsUserList();
            }
        });
      }
    },
    {
      label: t('重置密码'),
      handle: () => {
        passwordDialogShow.value = true;
      }
    },
  ], ...defaultOperation]);
  const pagination = reactive({ count: 0, limit: 10, current: 1 })
  const isScrollLoading = ref(false);
  const statusEnum = reactive({
    enabled: t('正常'),
    disabled: t('停用'),
    expired: t('冻结')
  });
  const columns= reactive([
    {
        label: t("用户名"),
        field: "username",
    },
    {
        label: t("全名"),
        field: "full_name",
    },
    {
        label: t("账号状态"),
        field: "status"
    },
    {
        label: t("邮箱"),
        field: "email",
    },
    {
        label: t("手机号"),
        field: "phone",
    },
    {
        label: t("所属组织"),
        field: "departments",
    }
  ]);
  const tableData = ref([]);
  /** 判断当前表格需要展示的列 */
  const columnsRender = computed(() => {
    let columnsList = [];
    columnsList = (isTenant.value || isLocalDataSource.value) ? columns : [...[{
        width: 40,
        minWidth: 40,
        type: "selection"
    }], ...columns]
    return isLocalDataSource.value ? columnsList : [...columnsList, ...[{
        label: "操作",
        field: "operation",
    }]];
  });

  const getBatchUserIds = (isArray = false) => {
    const userId = [];
    selectList.value.map(item => userId.push(item.id));
    if (isArray) {
      return userId.join(',');
    }
    return userId;
  }
  /** 点击移动/移动至组织按钮 */
  const handleOperations = async (status, title) => {
    moveDialogShow.value = true;
    const res = await departmentsList();
    dataSource.value = res.data;
  };

  const confirmOperations = async () => {
    InfoBox({
        title: t(`确认将选中的用户${currentHandle.value.label}`),
        height: 184,
        onConfirm: async () => {
            const params = {
                user_ids: getBatchUserIds(),
                target_department_ids: selectedValue.value,
                source_department_id: appStore.currentOrg.id
            };
            await currentHandle.value.confirmFn(params);
            moveDialogShow.value = false;
            initTenantsUserList();
        }
    });
  }

  const operationLabel = (item, row) => {
    if (item.key === 'status') {
        return row.status === 'enabled' ? t('停用') : t('启用')
    }
    return item.label;
  };
  /** 格式化要展示的字段 */
  const formatField = (field) => {
    if (Array.isArray(field)) {
      return field.join('、') || '--';
    }
    return field || '--';
  }

  watch(() => appStore.currentOrg, (val) => {
    !!val && initTenantsUserList();
  });
  
  const initTenantsUserList = async () => {
    try {
        selectList.value = [];
        isLoading.value = true;
        // isDataError.value = false;
        const params = {
          page: pagination.current,
          page_size: pagination.limit,
          keyword: keyword.value,
          department_id: isTenant.value ?  0 : appStore.currentOrg.id,
          recursive: !recursive.value
        };
        const res = await getTenantsUserList(appStore.currentTenant.id, params);
        // if (res.data?.count === 0) {
        //   searchVal.value === '' ? isDataEmpty.value = true : isEmptySearch.value = true;
        // }
        pagination.count = res.data?.count;
        tableData.value = res.data?.results;
    } catch (e) {
        console.warn(e);
        // isDataError.value = true;
    } finally {
        isLoading.value = false;
    }
  };
  const setItemRef = (el, key) => {
    if (el) {
      dropdownRefs.value[key] = el
    }
  }
  /** 生成随机密码 */
  const randomPasswordHandle = async () => {
    const res = await randomPasswords({data_source_id: appStore.currentOrg.data_source.id});
    password.value = res.data?.password;
  };
  /** 重置密码 */
  const resetPasswordConfirm = async () => {
    try {
        const param = { password: password.value };
        await resetTenantsUserPassword(detailsInfo.value.id, param);
        passwordDialogShow.value = false;
        Message({ theme: 'success', message: $t('重置密码成功') });
        initTenantsUserList();
    } catch (e) {
        console.warn(e);
    }
  }
  /** 点击快速录入按钮 */
  const fastInputHandle = () => {
    fastInputDialogShow.value = true;
  }
  const fastInputSuccess = () => {
    fastInputDialogShow.value = false;
    initTenantsUserList();
  };
  const handleEnter = () => {
    pagination.current = 1;
    initTenantsUserList();
  };

  const handleClear = () => {
    keyword.value = '';
    pagination.current = 1;
    initTenantsUserList();
  };
  const handleSelect = (v) => {
    console.log(v);
  };
  // 勾选数据行
  const handleSelectTable = ({ row, checked }) => {
    checked ? selectList.value.push(row) : selectList.value = selectList.value.filter(item => item.id !== row.id);
  };

  // 勾选所有数据行
  const handleSelectAll = ({ checked, data }) => {
    selectList.value = checked ? data : [];
  };
  const handleBeforeClose = async () => {
    let enableLeave = true;
    if (window.changeInput) {
        enableLeave = await editLeaveBefore();
    }
    editDetailsShow.value = false;
    if (!enableLeave) {
        return Promise.resolve(enableLeave);
    }
  };
  // 更新虚拟用户列表
  const updateUsers = (message: string) => {
    editDetailsShow.value = false;
    window.changeInput = false;
    Message({ theme: 'success', message });
    // initTenantsUserList();
  };

  const handleCancelEdit = () => {
    window.changeInput = false;
    editDetailsShow.value = false;
  };
  const editInfoHandle = (row, isDetail = false) => {
    isDetailSlider.value = isDetail;
    detailsInfo.value = row;
    editDetailsShow.value = true;
  }
</script>
<style lang="less">
    .operate-popover {
        padding: 5px 0 !important;
    }
</style>
<style lang="less" scoped>
    .organization-table {
        .table-search {
            width: 100%;
            position: relative;
            display: flex;
            .header-right {
                width: 30%;
                min-width: 400px;
                position: absolute;
                right: 0;
            }
        }
        .organization-table-main {
            background: #fff;
            .table-total {
                width: 100%;
                height: 32px;
                line-height: 32px;
                background: #F0F1F5;
                text-align: center;
                color: #63656E;
            }
            .icon-more {
                display: inline-block;
                width: 24px;
                height: 24px;
                font-size: 16px;
                line-height: 24px;
                margin-left: 8px;
                cursor: pointer;
                &:hover {
                    background: #F0F1F5;
                    border-radius: 50%;
                }
            }
            .table-operate {
                cursor: pointer;
                color: #3A84FF;
            }
            .operate-popover-main {
                display: inline-block;
            }
            .status-label {
                display: inline-block;
                width: 13px;
                height: 13px;
                border-radius: 50%;
                background: #3fc06d29;
                position: relative;
                top: 2px;
                margin-right: 3px;
                &::before {
                    content: '';
                    display: inline-block;
                    border-radius: 50%;
                    width: 7px;
                    height: 7px;
                    background: #3FC06D;
                    position: absolute;
                    left: 50%;
                    top: 50%;
                    transform: translate(-50%, -50%);
                }
                &.disabled {
                    background: #979ba529;
                    &::before {
                        background: #979BA5;
                    }
                }
                &.expired {
                    background: #ff9c0129;
                    &::before {
                        background: #FF9C01;
                    }
                }
            }
        }
    }
    .operate-menu-list {
        .operate-list-item {
            color: #63656E;
            height: 32px;
            line-height: 32px;
            padding: 0 12px;
            &:hover {
                background: #F5F7FA;
            }
        }
    }
</style>
  