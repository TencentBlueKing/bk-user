<template>
  <div class="opt-more" v-clickoutside="handleClickOutside">
    <bk-dropdown
      trigger="manual"
      :is-show="dropdownVisible"
    >
      <span
        class="user-icon icon-more !leading-[32px] p-[2px]"
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
        </bk-dropdown-menu>
      </template>
    </bk-dropdown>


    <bk-dialog
      :is-show="orgDialogVisible"
      :title="isAddSubOrg ? $t('添加子组织') : $t('重命名')"
      @closed="orgDialogVisible = false"
      @confirm="handleOrg"
    >
      <bk-form form-type="vertical">
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
import { clickoutside as vClickoutside } from 'bkui-vue';
import { computed, ref   } from 'vue';

import { addDepartment, updateDepartment } from '@/http/organizationFiles';
import { t } from '@/language/index';
import { copy } from '@/utils';

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

const emits = defineEmits(['updateNode', 'addNode']);

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
    name: t('复制组织ID'),
    action: () => copy(props.dept.id),
  },
  {
    name: t('复制组织名称'),
    action: () => copy(props.dept.name),
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
