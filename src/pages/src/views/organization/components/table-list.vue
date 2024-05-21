<template>
    <div class="organization-table px-[24px] py-[24px]">
        <div class="table-search mb-[16px]">
            <bk-button v-if="isTenantStatus && isLocalDataSource" @click="() => importDialogShow = true">
                <Upload class="mr-[8px] text-[16px]" />{{ $t('导入') }}
            </bk-button>
            <bk-button theme="primary" class="mr-[10px]" @click="fastInputHandle"
                v-if="!isTenantStatus">
                <i class="user-icon icon-add-2 mr8" />
                {{ $t('快速录入') }}
            </bk-button>
            <bk-button v-if="!isTenantStatus"
              @click="handleGetUsersDialog">{{ $t('拉取已有用户') }}</bk-button>
            <bk-checkbox class="ml-[16px] h-[32px]"
                :label="$t('仅显示本级用户')"
                v-model="recursive"
                @change="initTenantsUserList"
            />
            <bk-input
                class="header-right"
                v-model="keyword"
                :placeholder="$t('搜索用户名、姓名')"
                type="search"
                clearable
                @enter="handleEnter"
                @clear="handleClear"
            />
        </div>
        <bk-table
            height="100%"
            class="organization-table-main"
            :border="['outer']"
            :data="tableData"
            :pagination="pagination"
            v-bkloading="{ loading: isLoading }"
            row-hover="auto"
            remote-pagination
            :columns="columnsRender"
            @select="handleSelectTable"
            @select-all="handleSelectAll"
            @page-limit-change="pageLimitChange"
            @page-value-change="pageCurrentChange"
        >
          <template #empty>
            <Empty
              :is-data-empty="isDataEmpty"
              :is-search-empty="isEmptySearch"
              :is-data-error="isDataError"
              @handle-empty="handleClear"
              @handle-update="initTenantsUserList"
            />
          </template>
          <template #prepend v-if="selectList.length">
              <div class="table-total">
                  <span>{{ $t('当前已选择')}} <b>{{selectList.length}}</b> {{ $t('条数据，可以批量')}}</span>
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
        </bk-table>
    </div>
    <!-- 拉取已有用户 -->
    <bk-dialog
      :is-show="getUsersDialogShow"
      :title="$t('拉取已有用户')"
      :theme="'primary'"
      :size="'normal'"
      @closed="() => getUsersDialogShow = false"
      @confirm="() => confirmGetUser()"
    >
      <bk-select
        v-model="getUsersValue"
        class="user-select-main"
        :list="getUserList"
        filterable
        multiple
        auto-focus
        :clearable="false"
        id-key="id"
        display-key="username"
        :remoteMethod="remoteMethod"
        :placeholder="$t('2个字符起搜索')"
        @select="handleSelect"
      >
        <template #optionRender="{ item }" class="test">
          <div class="user-info-option">
            <p class="text-[#313238]">{{ item.username }}({{ item.full_name }})</p>
            <p class="text-[#979BA5] mt-[6px]">{{item.organization_paths.join('、')}}</p>
          </div>
        </template>
      </bk-select>
    </bk-dialog>
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
                        :disabled="chooseDepartments.includes(item.name)"
                    />
                </bk-select>
            </bk-form-item>
        </bk-form>
    </bk-dialog>
    <!-- 重置密码弹框 -->
    <bk-dialog
      :width="500"
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
                    :placeholder="passwordTips"
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
      render-directive="if"
      quick-close
      transfer
    >
      <EditDetails
        v-if="isDetailSlider"
        :details-info="editDetailsInfo"
        @updateUsers="updateUsers"
        @handleCancelEdit="handleCancelEdit" />
      <ViewUser :user-data="editDetailsInfo" v-else />
    </bk-sideslider>
    <!-- 导入弹框 -->
    <ImportDialog
      v-model:isShow="importDialogShow"
      :currentDataSourceId="dataSourceId"
      @success="initTenantsUserList"
    />
  </template>
  
<script setup lang="tsx">
  import { ref, reactive, computed, inject, onMounted, onBeforeMount, watch } from 'vue';
  import { InfoBox, Message } from 'bkui-vue';
  import Empty from '@/components/Empty.vue';
  import { Upload } from 'bkui-vue/lib/icon';
  import { t } from '@/language/index';
  import FastInputDialog from './fast-input-dialog.vue';
  import EditDetails from './edit-detail.vue';
  import ImportDialog from '@/components/import-dialog/import-dialog.vue'
  import ViewUser from '../details/ViewUser.vue';
  import { randomPasswords } from '@/http';
  import { getFields } from '@/http/settingFiles';
  import {
    getTenantsUserList,
    getFieldsTips,
    resetTenantsUserPassword,
    updateTenantsUserStatus,
    delTenantsUser,
    batchDeleteUser,
    optionalDepartmentsList,
    batchDelete,
    batchUpdate,
    batchCreate,
    batchDelUpdate,
    getTenantsUserDetail,
    getOrganizationPaths,
    getUsersList,
    passwordRule
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
  const isTenantStatus = computed(() => {
    return appStore.currentOrg?.id === appStore.currentTenant?.id;
  });
  const isDataError = ref(false);
  const isEmptySearch = ref(false);
  const detailsInfo = ref({});
  const selectList = ref([]);
  const password = ref('');
  const dataSource = ref([]);
  const moveDialogShow = ref(false);
  const currentHandle = ref({});
  const passwordDialogShow = ref(false);
  const fastInputDialogShow = ref(false);
  const importDialogShow = ref(false);
  const editDetailsInfo = ref({});
  const getUsersDialogShow = ref(false);
  const getUsersValue = ref([]);
  const getUserList = ref([]);
  const chooseDepartments = ref([]);
  const passwordTips = ref('');
  /** 是否为本地数据源 */
  const isLocalDataSource = computed(() => {
    return appStore.currentTenant?.data_source?.plugin_id === 'local';
  });
  const dataSourceId = computed(() => {
    return appStore.currentTenant?.data_source?.id;
  });
  const isEnabledPassword = computed(() => {
    return appStore.currentTenant?.data_source?.enable_password;
  })

  const editInfoHandle = async (row, isDetail = false) => {
    isDetailSlider.value = isDetail;
    detailsInfo.value = row;
    const [useRes, fieldsRes] = await Promise.all([
        getTenantsUserDetail(row.id),
        getFields(),
    ]);
    const data = useRes.data;
    const extrasList = fieldsRes.data.custom_fields;
    extrasList.map(item => item.value = data.extras[item.name]);
    Object.assign(data, {
      departments: getIdList(data?.departments),
      leaders: getIdList(data?.leaders),
      extras: extrasList
    })
    editDetailsInfo.value = data;
    editDetailsShow.value = true;
  }
  const defaultOperation = reactive([
    {
      label: t('删除'),
      isShow: !isLocalDataSource.value,
      handle: (isBatch, item) => {
          InfoBox({
            title: isBatch ? t('确认批量删除用户？') : t(`确认删除用户${detailsInfo.value.username}？`),
            subTitle: t('删除后，用户将被彻底删除，无法恢复'),
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
                    user_ids: getBatchUserIds(true),
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
            title: isEnabled ? t(`确定停用用户${detailsInfo.value.full_name} ？`) : t(`确定启用用户${detailsInfo.value.full_name} ？`),
            subTitle: isEnabled ? t('停用后，用户将无法登录') : t('启用后，用户将恢复登录'),
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
      disabled: isEnabledPassword.value,
      handle: () => {
        passwordDialogShow.value = true;
        passwordRule(detailsInfo.value.id).then(res => {
          passwordTips.value = res.data?.password_rule_tips;
        });
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
  const isDataEmpty = ref(false);
  const columns = reactive([
    {
        width: 40,
        minWidth: 40,
        type: "selection"
    },
    {
        label: t("用户名"),
        field: "username",
        render: ({ row, column }) => (
          <span class="table-operate" onClick={() => editInfoHandle(row)}>{row[column?.field]}</span>
        )
    },
    {
        label: t("姓名"),
        field: "full_name",
    },
    {
        label: t("账号状态"),
        field: "status",
        render: ({ row, column }) => (<span class="status-main">
            <label class={`status-label ${row.status}`}></label>
            {statusEnum[row.status]}
        </span>)
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
        render: ({ row, column }) => {
          // const tips = '';
          // const config = {
          //   content: '提示信息',
          //   onShow: () => {
          //     const res = getOrganizationPaths(row.id);
          //     console.log(res, '---')
          //   },
          // }
          return <span >{row[column?.field].join('、') || '--'}</span>
        }
    }
  ]);
  const tableData = ref([]);
  const renderOperation = ({ row, column, index }) => {
    return (<span>
        <label class="table-operate" onClick={() => editInfoHandle(row, true)}>{t('编辑')}</label>
        <bk-popover
          ext-cls="operate-popover"
          ref={(el) => setItemRef(el, `dropdownRef${index}`)}
          theme="light"
          trigger="click"
          arrow={false}
          placement="bottom"
          allowHtml
          v-slots={{
            content: () => (
              <ul class="operate-menu-list">
                {
                  rowOperation.map((item, ind) => <li
                    class={["operate-list-item", {disabled: item.disabled}]}
                    key="ind"
                    onClick={() => {
                        if (item.disabled) {
                          return;
                        }
                        detailsInfo.value = row;
                        dropdownRefs.value[`dropdownRef${index}`]?.hide();
                        item.handle(false, row);
                    }}>
                    { operationLabel(item, row) }
                  </li>)
                }
              </ul>
            )
          }}>
          <div class="operate-popover-main">
            <i class="user-icon icon-more ml8" />
          </div>
        </bk-popover>
    </span>)
  }
  const hasOperationColumns = [...columns, ...[{
    label: t("操作"),
    field: "operation",
    render: renderOperation
  }]]
  /** 判断当前表格需要展示的列 */
  const columnsRender = computed(() => {
    return isLocalDataSource.value ? hasOperationColumns : columns;
  });

  /** 点击拉取已有用户按钮 */
  const handleGetUsersDialog = () => {
    getUsersValue.value = [];
    getUsersDialogShow.value = true;
    getUserList.value = [];
  }

  const remoteMethod = async (word) => {
    if (word.length > 1) {
      const res = await getUsersList({tenant_id: appStore.currentTenant.id, keyword: word});
      getUserList.value = res.data;
    }
  }
  /** 确认拉取已有用户 */
  const confirmGetUser = async () => {
    try {
      const param = {
        target_department_ids: [appStore.currentOrg.id], 
        user_ids: getUsersValue.value
      }
      const res = await batchCreate(param);
      getUsersDialogShow.value = false;
      Message({ theme: 'success', message: t('拉取已有用户成功') });
      handleClear();
    } finally {
      isLoading.value = false;
    }
  }

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
    chooseDepartments.value = [];
    moveDialogShow.value = true;
    selectedValue.value = [];
    dataSource.value = [];
    selectList.value.map(item => chooseDepartments.value.push(...item.departments));
    const res = await optionalDepartmentsList();
    dataSource.value = res.data;
  };

  const confirmOperations = async () => {
    const params = {
      user_ids: getBatchUserIds(),
      target_department_ids: selectedValue.value,
      source_department_id: appStore.currentOrg.id
    };
    await currentHandle.value.confirmFn(params);
    moveDialogShow.value = false;
    handleClear();
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
    console.log(appStore.currentOrg, 'appStore.currentOrg')
    const { id, isTenant } = appStore.currentOrg;
    try {
        tableData.value = [];
        selectList.value = [];
        isLoading.value = true;
        isDataError.value = false;
        const params = {
          page: pagination.current,
          page_size: pagination.limit,
          keyword: keyword.value,
          department_id: isTenant ?  0 : appStore.currentOrg.id,
          recursive: !recursive.value
        };
        const res = await getTenantsUserList(isTenant ? id : appStore.currentTenant.id, params);
        if (res.data?.count === 0) {
          keyword.value === '' ? isDataEmpty.value = true : isEmptySearch.value = true;
        }
        pagination.count = res.data?.count;
        tableData.value = res.data?.results;
    } catch (e) {
        console.warn(e);
        isDataError.value = true;
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
    const res = await randomPasswords({data_source_id: appStore.currentTenant.data_source.id});
    password.value = res.data?.password;
  };
  /** 重置密码 */
  const resetPasswordConfirm = async () => {
    try {
        const param = { password: password.value };
        await resetTenantsUserPassword(detailsInfo.value.id, param);
        passwordDialogShow.value = false;
        handleClear();
        Message({ theme: 'success', message: t('重置密码成功') });
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
    handleClear();
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
    handleClear();
  };
  const pageLimitChange = (limit: number) => {
    pagination.limit = limit;
    pagination.current = 1;
    initTenantsUserList();
  };

  const pageCurrentChange = (current: number) => {
    pagination.current = current;
    initTenantsUserList();
  };

  const handleCancelEdit = () => {
    window.changeInput = false;
    editDetailsShow.value = false;
  };
  const getIdList = (data, key = 'id') => {
    if (!Array.isArray(data)) {
        return;
    }
    const values = data.reduce((acc, obj) => {
        if (key in obj) {
            acc.push(obj[key]);
        }
        return acc;
    }, []);
    return values;
  };
</script>
<style lang="less">
.operate-popover {
      padding: 5px 0 !important;
  }
  .organization-table-main {
    .bk-table-head thead th {
      &:first-child {
        text-align: center;
      }
    }
  }
  .organization-table {
    height: 100%;
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
  .user-select-main {

  }
  .operate-menu-list {
      .operate-list-item {
          color: #63656E;
          height: 32px;
          line-height: 32px;
          padding: 0 12px;
          cursor: pointer;
          &:hover {
              background: #F5F7FA;
          }
          &.disabled {
            color: #c4c6cc;
            cursor: not-allowed;
          }
      }
  }
</style>
  