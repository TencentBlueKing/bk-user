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
                <span class="text-[#FF9C01]">@{{ item.tenant_name }}</span>
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
                <span class="text-[#313238] pr-[8px]">
                  {{ item.username }}
                  ({{ item.full_name }})
                </span>
                <span class="text-[#FF9C01]">@{{ item.tenant_name }}</span>
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
import { bkTooltips as vBkTooltips } from 'bkui-vue';
import { defineEmits, inject, reactive, ref } from 'vue';

import ViewUser from './view-user.vue';

import { useCustomFields } from '@/hooks';
import { getTenantsUserDetail, searchOrganization, searchUser } from '@/http/organizationFiles';
import { getFields } from '@/http/settingFiles';
import { t } from '@/language/index';
import useAppStore from '@/store/app';

const emit = defineEmits(['select']);
const appStore = useAppStore();

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
const orgs = ref([]);
const users = ref([]);
const searchDialogVisible = ref(false);
const searchLoading = ref(false);
const selected = ref({});

const handleSearch = () => {
  if (search.value.length > 1) {
    searchData();
  } else {
    searchDialogVisible.value = false;
    appStore.isSearchTree = false;
  }
};

const handleClear = () => {
  appStore.isSearchTree = false;
  search.value = '';
  searchDialogVisible.value = false;
};

const searchData = () => {
  searchDialogVisible.value = true;
  searchLoading.value = true;
  const payload = {
    keyword: search.value,
  };
  Promise.all([searchOrganization(payload), searchUser(payload)])
    .then(([orgData, userData]) => {
      orgs.value = orgData.data || [];
      users.value = userData.data || [];
    })
    .catch((err) => {
      console.log(err);
    })
    .finally(() => {
      searchLoading.value = false;
    });
};

const handleOrgSelect = (org) => {
  appStore.isSearchTree = true;
  selected.value = org;
  searchDialogVisible.value = false;
  appStore.currentOrg = { ...org };
  emit('select');
};

const handleUserSelect = async (user) => {
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
  appStore.reloadIndex += 1;
};
</script>
