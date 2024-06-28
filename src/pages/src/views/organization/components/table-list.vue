<template>
    <div class="organization-table px-[24px] py-[24px]">
        <div class="table-search mb-[16px]">
            <bk-button v-if="!isCollaborativeUsers && isTenantStatus && isLocalDataSource"
              class="mr-[16px] button-upload"
              @click="() => importDialogShow = true">
                <Upload class="mr-[8px] text-[16px] icon-upload" />{{ $t('导入') }}
            </bk-button>
            <bk-button theme="primary" class="mr-[10px]" @click="fastInputHandle"
                v-if="isShowBtn">
                <i class="user-icon icon-add-2 mr8" />
                {{ $t('快速录入') }}
            </bk-button>
            <bk-button class="mr-[16px]" v-if="isShowBtn"
              @click="handleGetUsersDialog">{{ $t('拉取已有用户') }}</bk-button>
            <bk-checkbox class="h-[32px] ml-[2px]"
                :label="$t('仅显示本级用户')"
                v-model="recursive"
                @change="reloadList"
            />
            <bk-input
                class="header-right"
                v-model="keyword"
                :placeholder="$t('输入用户名、姓名、邮箱、手机号码搜索')"
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
            :columns="tableColumns"
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
              @handle-update="reloadList"
            />
          </template>
          <template #prepend v-if="selectList.length">
              <div class="table-total">
                  <span>{{ $t('当前已选择')}} <b>{{selectList.length}}</b> {{ $t('条数据，可以批量')}}</span>
                  <label
                      v-for="(item, index) in prependData.filter(item => item.isShow)"
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
        multiple-mode="tag"
        display-key="username"
        :remoteMethod="remoteMethod"
        @select="handleSelect"
      >
        <template #optionRender="{ item }" class="test">
          <div class="user-info-option pt-[5px] pb-[5px]">
            <p class="text-[#313238]">{{ item.username }}({{ item.full_name }})</p>
            <p class="text-[#979BA5] mt-[6px]">
                <bk-overflow-title
                  :style="{display: 'inline-block'}"
                  class="text-[#979BA5] leading-[20px]"
                  :class="{
                    'w-[370px]': !!item.organization_paths.length,
                    'w-[270px]': !!(item.organization_paths.length && item.status === 'disabled')
                  }"
                >
                  {{ item.organization_paths[0] }}
                </bk-overflow-title>
                <bk-tag
                v-if="item.organization_paths.length > 1"
                theme="info"
                class="inline-block !m-0 h-[20px] !ml-[2px]"
                v-bk-tooltips="{ content: item.organization_paths.join('\n'), boundary: 'parent' }"
              >
                +{{ item.organization_paths.length }}
              </bk-tag>
            </p>
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
      <div class="mb-[16px] text-[#979BA5]">{{moveTips}}</div>
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
                    idKey="id"
                    displayKey="name"
                    collapse-tags
                    @select="handleSelect"
                >
                <bk-option
                  v-for="item in dataSource"
                  :key="item.id"
                  :disabled="chooseDepartments.includes(item.name)"
                  v-bk-tooltips="{content: $t('已在当前部门'), disabled: !chooseDepartments.includes(item.name), boundary: 'parent'}"
                  :value="item.id"
                  :name="item.name"
                  :label="item.name" />
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
      @closed="resetPasswordClose"
      @confirm="resetPasswordConfirm"
    >
        <bk-form
            class="example"
            form-type="vertical"
        >
            <bk-form-item :label="$t('新密码')" required>
              <passwordInput :style="{width: '80%'}"  v-model="password" clearable
                  :placeholder="passwordTips.join('、')"
                  v-bk-tooltips="{ content: passwordTips.join('\n'), theme: 'light' }"
                  @input="inputPassword"
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
    <template #header>
      <div class="w-full">{{isDetailSlider ? $t('编辑用户') : $t('用户详情')}}</div>
      <bk-button v-if="!isDetailSlider && !isCollaborativeUsers && isLocalDataSource" class="mr-[20px]" @click="(data) => handleEditDetails(editDetailsInfo)">{{$t('编辑')}}</bk-button>
    </template>
      <EditDetails
        v-if="isDetailSlider"
        :details-info="editDetailsInfo"
        @updateUsers="updateUsers"
        @handleCancelEdit="handleCancelEdit" />
      <ViewUser :user-data="detailsInfo" :detail="editDetailsInfo" v-else />
    </bk-sideslider>
    <!-- 导入弹框 -->
    <ImportDialog
      v-model:isShow="importDialogShow"
      :currentDataSourceId="dataSourceId"
      @success="reloadList"
    />
  </template>
  
<script setup lang="tsx">
  import { ref, reactive, computed, inject, onMounted, onBeforeMount, watch, nextTick } from 'vue';
  import { InfoBox, Message } from 'bkui-vue';
  import Empty from '@/components/Empty.vue';
  import { Upload} from 'bkui-vue/lib/icon';
  import { t } from '@/language/index';
  import FastInputDialog from './fast-input-dialog.vue';
  import EditDetails from './edit-detail.vue';
  import ImportDialog from '@/components/import-dialog/import-dialog.vue'
  import ViewUser from '../details/ViewUser.vue';
  import { randomPasswords } from '@/http';
  import { getFields } from '@/http/settingFiles';
  import passwordInput from '@/components/passwordInput.vue';
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
  const moveTips = ref('');
  /** 是否为租户层级 */
  const isTenantStatus = computed(() => {
    return appStore.currentOrg?.id === appStore.currentTenant?.id;
  });
  /** 是否为协同租户 */
  const isCollaborativeUsers = computed(() => {
    return appStore.currentTenant?.id !== appStore.currentOrg?.tenantId
  })
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
  const passwordTips = ref([]);
  const isPassword = ref(false);
  /** 是否为本地数据源 */
  const isLocalDataSource = computed(() => {
    console.log(appStore.currentTenant, appStore.currentTenant?.data_source?.plugin_id === 'local')
    return appStore.currentTenant?.data_source?.plugin_id === 'local';
  });
  const dataSourceId = computed(() => {
    return appStore.currentTenant?.data_source?.id;
  });
  const isEnabledPassword = computed(() => {
    return appStore.currentTenant?.data_source?.enable_password;
  })

  const isShowBtn = computed(() => {
    return !isCollaborativeUsers.value && !isTenantStatus.value && isLocalDataSource.value
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
      department_ids: getIdList(data?.departments),
      leader_ids: getIdList(data?.leaders),
      extras: extrasList
    })
    editDetailsInfo.value = data;
    editDetailsShow.value = true;
  }
  const handleEditDetails = (row) => {
    editInfoHandle(row, true)
  };
  const defaultOperation = reactive([
    {
      label: t('删除'),
      isShow: !isLocalDataSource.value,
      handle: (isBatch, item) => {
          InfoBox({
            title: isBatch ? t('确认批量删除用户？') : t(`确认删除用户：${detailsInfo.value.username}？`),
            subTitle: t('删除后，用户将被彻底删除，无法恢复'),
            height: 184,
            theme: 'danger',
            infoType: 'warning',
            onConfirm: async () => {
                if (isBatch) {
                    await batchDeleteUser(getBatchUserIds(true));
                    selectList.value = [];
                } else {
                    await delTenantsUser(detailsInfo.value.id);
                }
                reloadList();
            },
          });
      }
    },
  ]);
  const moveOperation = reactive([
    {
      label: t('移至目标组织'),
      isShow: true,
      confirmFn: batchCreate,
      handle: () => {
        handleOperations(true, t('移至目标组织'), t('将'), t('从当前组织移出，并追加到以下组织'));
      }
    }
  ])
  const operationList = reactive([...[
    {
      label: t('移出当前组织'),
      isShow: true,
      handle: () => {
        InfoBox({
            title:`${t('确认将选中的用户移出')}${appStore.currentOrg.name}`,
            height: 184,
            onConfirm: async () => {
                const params = {
                    user_ids: getBatchUserIds(true),
                    source_department_id: appStore.currentOrg.id
                }
                await batchDelete(params);
                moveDialogShow.value = false;
                reloadList();
            }
        });
      }
    },   
    {
      label: t('追加目标组织'),
      isShow: true,
      confirmFn: batchCreate,
      handle: () => {
        handleOperations(true, t('追加目标组织'), t('将'), t('追加到以下组织'));
      }
    },
    {
      label: t('清空并加入组织'),
      isShow: true,
      confirmFn: batchDelUpdate,
      handle: () => {
        handleOperations(false, t('清空并加入组织'), t('清空'), t('的现有组织，并加入到以下组织'));
      }
    }, 
  ], ...moveOperation, ...defaultOperation]);
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
            infoType: 'warning',
            theme: 'danger',
            onConfirm: async () => {
                await updateTenantsUserStatus(item.id);
                reloadList();
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
          passwordTips.value = res.data?.rule_tips;
        });
      }
    },
  ], ...defaultOperation]);
  const prependData = computed(() => {
    return appStore.currentOrg.isTenant ? [...moveOperation, ...defaultOperation] : operationList;
  })
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
        label: t("用户名"),
        field: "username",
        showOverflowTooltip: true,
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
        render: ({ row }) => (
          <span>{row.phone_country_code ? `(+${row.phone_country_code}) ${row.phone}` : row.phone}</span>
        )
    },
    {
        label: t("所属组织"),
        field: "departments",
        render: ({ row, column }) => {
          const config = {
            content: (row?.organization_paths || []).join('\n'),
            disabled: row[column?.field]?.length === 0
          }
          return <span v-bk-tooltips={config}>{(row[column?.field] || []).join('、') || '--'}</span>
        }
    }
  ]);
  const tableData = ref([]);
  const renderOperation = ({ row, column, index }) => {
    if (isLocalDataSource.value) {
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
                    v-bk-tooltips={{
                      content: t('当前租户未启用账密登录，无法修改密码'),
                      disabled: !item.disabled
                    }}
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
    return rowOperation.slice(0, 1).map(item => <label class="table-operate"
      onClick={() => {
        detailsInfo.value = row;
        item.handle(false, row);
    }}>{ operationLabel(item, row) }</label>)
  }
  const selectionColumns = reactive([{
      width: 40,
      minWidth: 40,
      type: "selection"
  }]);
  const operationColumns = reactive([{
    label: t("操作"),
    field: "operation",
    render: renderOperation
  }]);
  const hasOperationColumns = [...columns, ...operationColumns]
  /** 判断当前表格需要展示的列 */
  const columnsRender = computed(() => {
    return isLocalDataSource.value ? [...selectionColumns, ...hasOperationColumns] : hasOperationColumns;
  });
  const tableColumns = computed(() => {
    return isCollaborativeUsers.value ? columns : columnsRender.value;
  })
  const getUserListFun = async (word) => {
    const res = await getUsersList({tenant_id: appStore.currentTenant.id, keyword: word});
    getUserList.value = res.data;
  }
  /** 点击拉取已有用户按钮 */
  const handleGetUsersDialog = () => {
    getUsersValue.value = [];
    getUsersDialogShow.value = true;
    getUserList.value = [];
    getUserListFun();
  }

  const remoteMethod = (word = '') => {
    if (word.length > 1) {
      getUserListFun(word);
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
  const handleOperations = async (status, title, prefix, suffix) => {
    chooseDepartments.value = [];
    moveDialogShow.value = true;
    selectedValue.value = [];
    dataSource.value = [];
    const users = [];
    selectList.value.map(item => {
      chooseDepartments.value.push(...item.departments);
      users.push(item.full_name);
    });
    const isMore = users.length > 3;
    const showStr = isMore ? `...${t('等')}${users.length}${t('个用户')}` : '';
    moveTips.value = `${prefix}${users.slice(0,3).join('、')}${showStr}${suffix}`;
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
    !!val && reloadList();
  });
  
  const initTenantsUserList = async () => {
    isDataEmpty.value = false;
    isEmptySearch.value = false;
    const { id, isTenant, tenantId } = appStore.currentOrg;
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
        const res = await getTenantsUserList(isTenant ? id : tenantId, params);
        if (res.data?.count === 0) {
          isDataEmpty.value = keyword.value === '';
          isEmptySearch.value = keyword.value !== '';
        }
        pagination.count = res.data?.count;
        tableData.value = res.data?.results;
        tableData.value.map(item => {
          getOrganizationPaths(item.id).then(res => {
            const organization_paths = res?.data?.organization_paths;
            item.organization_paths = organization_paths;
          });
        });
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
        handleClear();
        resetPasswordClose()
        Message({ theme: 'success', message: t('重置密码成功') });
    } catch (e) {
        console.warn(e);
    }
  }
  /** 取消重置密码 */
  const resetPasswordClose = () => {
    passwordDialogShow.value = false
    password.value = ''
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
    reloadList();
  };
  const handleSelect = (v) => {
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
    editDetailsShow.value = !enableLeave;
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
  const reloadList = () => {
    pagination.current = 1;
    initTenantsUserList();
  }
  const pageLimitChange = (limit: number) => {
    pagination.limit = limit;
    reloadList();
  };

  const pageCurrentChange = (current: number) => {
    pagination.current = current;
    initTenantsUserList();
  };

  const handleCancelEdit = () => {
    handleBeforeClose();
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

  const inputPassword = (val) => {
  password.value = val;
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
    position: relative;
    display: flex;
    width: 100%;

    .button-upload:hover {
      border-color: #3A84ff;

      .icon-upload {
        color: #3A84ff;
       }
    }
    .header-right {
      position: absolute;
      right: 0;
      width: 30%;
      min-width: 400px;
    }
  }

  .organization-table-main {
    background: #fff;

    .table-total {
      width: 100%;
      height: 32px;
      line-height: 32px;
      color: #63656E;
      text-align: center;
      background: #F0F1F5;
    }

    .icon-more {
      display: inline-block;
      width: 24px;
      height: 24px;
      margin-left: 8px;
      font-size: 16px;
      line-height: 24px;
      cursor: pointer;

      &:hover {
        background: #F0F1F5;
        border-radius: 50%;
      }
    }

    .table-operate {
      color: #3A84FF;
      cursor: pointer;
    }

    .operate-popover-main {
      display: inline-block;
    }

    .status-label {
      position: relative;
      top: 2px;
      display: inline-block;
      width: 13px;
      height: 13px;
      margin-right: 3px;
      background: #3fc06d29;
      border-radius: 50%;

      &::before {
        position: absolute;
        top: 50%;
        left: 50%;
        display: inline-block;
        width: 7px;
        height: 7px;
        background: #3FC06D;
        border-radius: 50%;
        content: '';
        transform: translate(-50%, -50%);
      }

      &.disabled {
        background: #979ba529;

        &::before {
          background: #979BA5;
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

    &.expired {
      background: #ff9c0129;

      &::before {
        background: #FF9C01;
      }
    }
  }
  }
}
}

.user-info-option {
  &.disabled {
    color: #c4c6cc;
    cursor: not-allowed;
  }
}

.operate-menu-list {
  .operate-list-item {
    height: 32px;
    padding: 0 12px;
    line-height: 32px;
    color: #63656E;
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
<style lang="less" scoped>
:deep(.copy-icon) {
  right: 25px !important;
}
</style>
  