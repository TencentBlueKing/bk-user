<template>
  <div class="bg-white px-[12px] h-[52px] flex shadow-[0_3px_4px_0_#0000000a] pt-[10px] z-10 relative">
    <bk-input
      v-model="search"
      type="search"
      :clearable="true"
      @enter="handleSearch"
      @search="handleSearch"
      @clear="handleClear"
    ></bk-input>
    <div class="user-icon icon-refresh bg-[#F0F1F5] h-[32px] w-[32px] ml-[8px] !leading-[32px] cursor-pointer">
    </div>
    <div
      v-if="searchDialogVisible"
      class="absolute top-[45px] max-h-[500px] overflow-auto w-[394px] bg-white shadow-[0_2px_6px_0_#0000001a] border">
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
              @click="selected = item"
            >
              <div class="leading-[20px]">
                <span class="text-[#313238] pr-[8px]">
                  {{ item.username }}
                  ({{ item.full_name }})
                </span>
                <span class="text-[#FF9C01]">@{{ item.tenant_name }}</span>
              </div>
              <bk-overflow-title class="text-[#979BA5] leading-[20px]">
                {{ item.organization_paths[0] }}
              </bk-overflow-title>
              <span
                v-if="item.status === 'disabled'"
                class="bg-[#F0F1F5] radius-[2px] absolute top-[18px] right-[12px] py-[2px] px-[8px] text-[#63656E]"
              >
                {{ $t('已停用') }}
              </span>
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
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import { searchOrganization, searchUser } from '@/http/organizationFiles';
import useAppStore from '@/store/app';

const appStore = useAppStore();

const search = ref('');
const orgs = ref([]);
const users = ref([]);
const searchDialogVisible = ref(false);
const searchLoading = ref(false);
const selected = ref({});

const handleSearch = () => {
  if (search.value.length > 1) {
    searchData();
  }
};

const handleClear = () => {
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
  console.log(org);
  selected.value = org;
  searchDialogVisible.value = false;
  appStore.currentOrg = { ...org };
};
</script>
