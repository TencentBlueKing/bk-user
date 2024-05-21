<template>
  <div class="opt-more absolute right-[12px] top-0" v-clickoutside="handleClickOutside">
    <bk-dropdown
      trigger="manual"
      :is-show="dropdownVisible"
    >
      <span
        class="user-icon icon-more !leading-[32px] p-[2px] hover:bg-[#DCDEE5] rounded-[2px]"
        @click="dropdownVisible = !dropdownVisible">
      </span>
      <template #content>
        <bk-dropdown-menu>
          <bk-dropdown-item
            v-for="item in deptDropdownList"
            :key="item.name"
            @click.prevent="item.action(dept)"
          >
            {{ item.name }}
          </bk-dropdown-item>
          <div v-if="!isCollaboration">
            <div class="border-t border-[#EAEBF0] mx-[12px] my-[4px]"></div>
            <bk-dropdown-item
              @click.prevent="handleDelete"
            >
              {{ $t('删除组织') }}
            </bk-dropdown-item>
          </div>
        </bk-dropdown-menu>
      </template>
    </bk-dropdown>


    <bk-dialog
      :is-show="orgDialogVisible"
      :title="isAddSubOrg ? $t('添加子组织') : $t('重命名')"
      height="200"
      @closed="orgDialogVisible = false"
      @confirm="handleOrg"
    >
      <bk-form form-type="vertical" class="mt-[10px]">
        <bk-form-item
          :label="$t('组织名称')"
          :required="true"
        >
          <bk-input v-model="deptName"></bk-input>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
  </div>
</template>


<script setup lang="ts">
import { clickoutside as vClickoutside, InfoBox } from 'bkui-vue';
import { computed, h, ref } from 'vue';

import { addDepartment, deleteDepartment, updateDepartment } from '@/http/organizationFiles';
import { t } from '@/language/index';
import router from '@/router';

const props = defineProps({
  dept: {
    type: Object,
    default: () => ({}),
  },
  tenant: {
    type: Object,
    default: () => ({}),
  },
  isCollaboration: {
    type: Boolean,
    default: false,
  },
});

const emits = defineEmits(['updateNode', 'addNode', 'deleteNode']);

const deptName = ref(props.dept.name);

const dropdownVisible = ref(false);

const orgDialogVisible = ref(false);
const isAddSubOrg = ref(false);

const defaultDropdownList = ref<any[]>([
  {
    name: t('添加子组织'),
    action: () => {
      dropdownVisible.value = false;
      isAddSubOrg.value = true;
      orgDialogVisible.value = true;
      deptName.value = '';
    },
  },
  {
    name: t('重命名'),
    action: () => {
      dropdownVisible.value = false;
      isAddSubOrg.value = false;
      orgDialogVisible.value = true;
    },
  },
]);

const collaborationDropdownList = ref<any[]>([
  {
    name: t('协同配置'),
    action: () => {
      router.push({
        name: 'collaboration',
        query: {
          tab: 'other',
        },
      });
    },
  },
]);

const deptDropdownList = computed(() => (props.isCollaboration
  ? collaborationDropdownList.value
  : defaultDropdownList.value));

const handleClickOutside = () => {
  setTimeout(() => {
    dropdownVisible.value = false;
  });
};

/**
 * 删除
 */
const handleDelete = () => {
  dropdownVisible.value = false;
  InfoBox({
    title: t('确认删除该组织？'),
    subTitle: h(
      'div',
      {},
      [
        h(
          'p',
          {
            style: {
              color: '#313238',
              paddingBottom: '10px',
            },
          },
          `${t('组织')}: ${props.dept.name}`,
        ),
        h(
          'p',
          {},
          t('删除该组织同时会删除其下用户与子组织，请谨慎操作'),
        ),
      ],
    ),
    onConfirm: () => {
      deleteDepartment(props.dept.id).then(() => {
        emits('deleteNode', props.dept.id);
      });
    },
  });
};

/**
 * @description 创建租户部门/更新租户部门
 */
const handleOrg = () => {
  orgDialogVisible.value = false;
  if (isAddSubOrg.value) {
    const newOrg = {
      name: deptName.value,
      parent_department_id: props.dept.id,
    };
    addDepartment(props.tenant.id, newOrg).then((res) => {
      const node = {
        id: res.data.id,
        name: deptName.value,
        has_children: false,
      };
      emits('addNode', props.dept.id, node);
    });
  } else {
    updateDepartment(props.dept.id, { name: deptName.value }).then(() => {
      const node = {
        ...props.dept,
        name: deptName.value,
      };
      emits('updateNode', node);
    });
  }
};
</script>
