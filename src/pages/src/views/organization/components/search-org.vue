<template>
  <div class="bg-white px-[12px] h-[52px] flex shadow-[0_3px_4px_0_#0000000a] pt-[10px] z-10 relative">
    <bk-input
      v-model="search"
      type="search"
      :placeholder="$t('请输入至少2个字符搜索')"
      :clearable="true"
      @change="handleSearch"
      @clear="handleClear"
    ></bk-input>
    <div
      class="user-icon icon-refresh bg-[#F0F1F5] h-[32px] w-[32px] ml-[8px] !leading-[32px] cursor-pointer"
      @click="handleRefresh"
    >
    </div>
    <div
      v-if="searchDialogVisible"
      class="fixed top-[98px] max-h-[500px] overflow-auto w-[394px] bg-white shadow-[0_2px_6px_0_#0000001a] border">
      <div v-bkloading="{ loading: searchLoading }">
        <section v-if="orgs.length || users.length" class="py-[8px]">
          <div v-if="orgs.length">
            <div class="text-[#979BA5] leading-[32px] px-[12px]">{{ $t('组织') }}</div>
            <div
              v-for="item in orgs"
              :key="item.id"
              :class="{ 'bg-[#E1ECFF]': selected.id === item.id }"
              class="py-[6px] hover:bg-[#F5F7FA] cursor-pointer px-[12px]"
              @click="handleOrgSelect(item)"
            >
              <div class="leading-[20px]">
                <span class="text-[#313238] pr-[8px]">{{ item.name }}</span>
                <span v-is-multiple-tenant class="text-[#FF9C01]">@{{ item.tenant_name }}</span>
              </div>
              <bk-overflow-title class="text-[#979BA5] leading-[20px]">
                {{ item.organization_path }}
              </bk-overflow-title>
            </div>
          </div>

          <div v-if="orgs.length && users.length" class="border-t border-[#EAEBF0] mx-[12px] my-[4px]"></div>

          <div v-if="users.length">
            <div class="text-[#979BA5] leading-[32px] px-[12px]">{{ $t('用户') }}</div>
            <div
              v-for="item in users"
              :key="item.id"
              :class="{ 'bg-[#E1ECFF]': selected.id === item.id }"
              class="py-[6px] hover:bg-[#F5F7FA] cursor-pointer px-[12px] relative"
              @click="handleUserSelect(item)"
            >
              <div class="leading-[20px]">
                <DisplayName :user-id="item.id" class="text-[#313238] pr-[8px]" />
                <span v-is-multiple-tenant class="text-[#FF9C01]">@{{ item.tenant_name }}</span>
              </div>
              <div class="inline-flex w-full">
                <bk-overflow-title
                  class="text-[#979BA5] leading-[20px]"
                  :class="{
                    'w-[333px]': !!item.organization_paths.length,
                    'w-[270px]': !!(item.organization_paths.length && item.status === 'disabled')
                  }"
                >
                  {{ item.organization_paths[0] }}
                </bk-overflow-title>
                <bk-tag
                  v-if="item.organization_paths.length > 1"
                  theme="info"
                  class="inline-block !m-0 h-[20px] !ml-[2px]"
                  v-bk-tooltips="{ content: item.organization_paths.join('\n') }"
                >
                  +{{ item.organization_paths.length }}
                </bk-tag>
                <span
                  v-if="item.status === 'disabled'"
                  class="bg-[#F0F1F5] radius-[2px] absolute top-[18px] right-[12px] py-[2px] px-[8px] text-[#63656E]"
                >
                  {{ $t('已停用') }}
                </span>
              </div>
            </div>
          </div>
        </section>
        <section v-else>
          <bk-exception
            type="search-empty"
            class="py-[24px]"
            scene="part"
            :description="$t('暂无搜索结果')"
          ></bk-exception>
        </section>
      </div>
    </div>

    <!-- 查看/编辑用户 -->
    <div v-if="showSideBar">
      <bk-sideslider
        ext-cls="details-edit-wrapper"
        :width="640"
        :is-show="detailsConfig.isShow"
        :title="detailsConfig.title"
        :before-close="handleBeforeClose"
        render-directive="if"
        quick-close
      >
        <template #header>
          <span>{{ detailsConfig.title }}</span>
          <!-- <bk-button>删除</bk-button> -->
        </template>
        <view-user :user-data="state.userInfo" />
      </bk-sideslider>
    </div>
  </div>
</template>

<script setup lang="ts">
import { bkTooltips as vBkTooltips, Message } from 'bkui-vue';
import type { IMessage } from 'bkui-vue/lib/message/messageConstructor';
import { inject, reactive, ref } from 'vue';

import ViewUser from './view-user.vue';

import DisplayName from '@/components/display-name.vue';
import { useCustomFields } from '@/hooks';
import { getTenantsUserDetail, searchOrganization, searchUser } from '@/http/organizationFiles';
import { getFields } from '@/http/settingFiles';
import { SearchOrganizationItemData, SearchUserItemData } from '@/http/types/organizationFiles';
import { t } from '@/language/index';
import useOrganizationStore from '@/store/organization';

const emit = defineEmits(['select']);
const organizationStore = useOrganizationStore();

const editLeaveBefore = inject('editLeaveBefore');

const detailsConfig = reactive({
  isShow: false,
  title: '',
});

const showSideBar = ref(false);
// 销毁侧栏，防止tips不消失
const hideSideBar = () => {
  setTimeout(() => {
    showSideBar.value = false;
  }, 300);
};
const state = reactive({
  userInfo: {},
});

const search = ref('');
const orgs = ref<SearchOrganizationItemData[]>([]);
const users = ref<SearchUserItemData[]>([]);
const searchDialogVisible = ref(false);
const searchLoading = ref(false);
const selected = ref({});

const handleSearch = () => {
  if (search.value.length === 0) {
    searchDialogVisible.value = false;
    organizationStore.isSearchTree = false;
    return;
  }
  searchData();
};

const handleClear = () => {
  organizationStore.isSearchTree = false;
  search.value = '';
  searchDialogVisible.value = false;
};

const searchData = () => {
  searchDialogVisible.value = true;
  searchLoading.value = true;
  const payload = {
    keyword: search.value,
  };
  const httpConfig = { customMessage: true };
  Promise.allSettled([searchOrganization(payload, httpConfig), searchUser(payload, httpConfig)])
    .then((results) => {
      const orgResult = results[0];
      const userResult = results[1];
      // 处理组织数据
      if (orgResult.status === 'fulfilled') {
        orgs.value = orgResult.value.data || [];
      }
      // 处理用户数据
      if (userResult.status === 'fulfilled') {
        users.value = userResult.value.data || [];
      }
      // 处理错误信息
      const orgError = orgResult.status === 'rejected' ? orgResult.reason : null;
      const userError = userResult.status === 'rejected' ? userResult.reason : null;
      if (orgError || userError) {
        const orgErrorMessage = orgError?.[1]?.suggestion;
        const userErrorMessage = userError?.[1]?.suggestion;
        // 如果两个错误信息相同，只展示一次
        if (orgErrorMessage && userErrorMessage && orgErrorMessage === userErrorMessage) {
          console.error(orgError?.[0]);
          console.error(userError?.[0]);
          const messageConfig = orgError?.[1];
          handleShowErrorMessage(messageConfig);
        } else {
          // 错误信息不同，各自展示
          if (orgError) {
            console.error(orgError?.[0]);
            const messageConfig = orgError?.[1];
            handleShowErrorMessage(messageConfig);
          }
          if (userError) {
            console.error(userError?.[0]);
            const messageConfig = userError?.[1];
            handleShowErrorMessage(messageConfig);
          }
        }
      }
    })
    .finally(() => {
      searchLoading.value = false;
    });
};

const handleShowErrorMessage = (messageConfig: IMessage) => {
  Message({
    theme: 'error',
    message: messageConfig,
    delay: 10000,
    extCls: 'message-fix-fixed',
    actions: [
      {
        id: 'assistant',
        disabled: true,
      },
    ],
  });
};

const handleOrgSelect = (org: SearchOrganizationItemData) => {
  organizationStore.isSearchTree = true;
  selected.value = org;
  searchDialogVisible.value = false;
  organizationStore.updateSelectedOrg({
    tenantId: org.tenant_id,
    tenantName: org.tenant_name,
    tenantLogo: organizationStore.getTenantLogo(org.tenant_id),
    dataSourceId: org.data_source_id,
    deptId: org.id,
    deptName: org.name,
    organizationPath: org.organization_path,
  });
  emit('select');
};

const handleUserSelect = async (user: SearchUserItemData) => {
  searchDialogVisible.value = false;
  showSideBar.value = true;
  const [userRes, fieldsRes] = await Promise.all([
    getTenantsUserDetail(user.id),
    getFields(),
  ]);
  state.userInfo = userRes.data;
  state.userInfo.extras = useCustomFields(state.userInfo?.extras, fieldsRes.data.custom_fields);
  detailsConfig.title = t('用户详情');
  detailsConfig.isShow = true;
};

const handleBeforeClose = async () => {
  let enableLeave = true;
  if (window.changeInput) {
    enableLeave = await editLeaveBefore();
    if (enableLeave) {
      detailsConfig.isShow = false;
      hideSideBar();
    }
  } else {
    detailsConfig.isShow = false;
    hideSideBar();
  }
  if (!enableLeave) {
    return Promise.resolve(enableLeave);
  }
};

const handleRefresh = () => {
  handleClear();
  organizationStore.reloadIndex += 1;
};
</script>
