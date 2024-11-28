<template>
  <bk-dialog
    :width="640"
    :height="485"
    :is-show="isShow"
    :title="$t('快速录入')"
    :theme="'primary'"
    :size="'medium'"
    :dialog-type="'process'"
    :current="currentId"
    :total-step="objectSteps.length"
    :confirm-text="$t('确定录入')"
    @closed="closed"
    @confirm="confirm"
    @next="handleNext"
    @prev="handlePrev"
  >
    <div class="fast-input-dialog">
      <bk-steps
        class="fast-input-step"
        :cur-step="currentId"
        :steps="objectSteps"
      />
      <div
        v-if="currentId === 1"
        style="margin-top: 18px"
      >
        <div class="info-content theme">
          <i class="user-icon icon-info-i theme-icon" />
          <p>{{$t('快速将用户录入到')}}「{{currentOrgName}}」，{{$t('如需添加到其他组织，请使用')}}
            <label
              class="text-[#3A84FF] cursor-pointer"
              @click="importClick">{{$t('「导入」')}}</label>
            {{$t(' 功能。')}}
          </p>
          <p>{{$t('录入字段为 ')}}
            <label
              class="text-[#3A84FF] cursor-pointer"
              @click="() => goToSetting('field')">{{$t('设置 > 字段设置')}}</label>
            {{$t(' 中配置。')}}
          </p>
        </div>
        <div class="info-content">
          <p>{{$t('录入格式：')}}<label class="info-txt">
            <label v-for="(item, ind) in tipsInfo" :key="ind">
              <label
                v-bk-tooltips="{ content: item.tips, disabled: !item.tips }"
                :class="{ tips: item.tips }">
                {{item.display_name}}
              </label><label v-if="ind !== tipsInfo.length - 1"> + </label>
            </label>
          </label></p>
          <p>{{$t('信息之间使用逗号区隔，换行可输入多个用户，最多支持输入100个用户')}}</p>
        </div>
        <bk-form
          ref="formRef"
          form-type="vertical"
          :model="formData"
          :rules="rules"
        >
          <bk-form-item
            label=""
            property="val"
          >
            <bk-input
              v-model="formData.val"
              type="textarea"
              :rows="6"
              :resize="false"
              :placeholder="$t('输入案例：zhangsan, 张三, 10000@qq.com, 15709998877')"
            />
          </bk-form-item>
        </bk-form>
      </div>
      <bk-table
        v-else
        v-bkloading="{ loading: isLoading }"
        style="margin-top: 18px"
        :min-height="290"
        :columns="showColumns"
        :data="tableData"
        stripe
      >
      </bk-table>
    </div>
  </bk-dialog>
</template>

<script setup lang="tsx">
import { bkTooltips as vBkTooltips } from 'bkui-vue';
import { computed, nextTick, ref, watch } from 'vue';

import { useValidate } from '@/hooks';
import { batchCreatePreview, getFieldsTips, operationsCreate } from '@/http/organizationFiles';
import { t } from '@/language/index';
import router from '@/router';
import useAppStore from '@/store/app';
const props = defineProps({
  isShow: {
    type: Boolean,
    default: false,
  },
});
const emit = defineEmits(['update:isShow', 'success', 'click-import']);
const appStore = useAppStore();
const tipsInfo = ref('');
const validate = useValidate();
const rules = {
  val: [validate.required],
};
const formRef = ref('');
const tableData = ref([]);
const formData = ref({
  val: '',
});
const objectSteps = ref([
  { title: t('录入用户'), icon: 1 },
  { title: t('预览确认'), icon: 2 },
]);
const isLoading = ref(false);
const currentId = ref(1);
const currentOrgName = computed(() => appStore.currentOrg?.name);
watch(() => props.isShow, async (val) => {
  if (val) {
    currentId.value = 1;
    formData.value.val = '';
    nextTick(() => {
      formRef.value?.clearValidate();
    });
    const res = await getFieldsTips();
    tipsInfo.value = (res.data || []);
    tableData.value = [];
  }
});
const showColumns = computed(() => {
  const columns = [];
  tipsInfo.value.map(item => columns.push({ label: item.display_name, field: item.name }));
  return columns;
});
const handleNext = async () => {
  formRef.value.validate();
  if (!!formData.value.val && (currentId.value < objectSteps.value.length)) {
    isLoading.value = true;
    const param = {
      user_infos: formData.value.val.split('\n'),
      department_id: appStore.currentOrg.id,
    };
    try {
      const res = await batchCreatePreview(param);
      tableData.value = res.data.map(item => Object.assign(item, item.extras));
      currentId.value += 1;
    } catch (e) {
      console.warn(e);
    } finally {
      isLoading.value = false;
    }
  }
};
const handlePrev = () => {
  if (currentId.value > 1) {
    currentId.value -= 1;
  }
};
const confirm = async () => {
  const param = {
    user_infos: formData.value.val.split('\n'),
    department_id: appStore.currentOrg.id,
  };
  await operationsCreate(param);
  emit('success');
};
const closed = () => {
  emit('update:isShow', false);
};
const goToSetting = (name) => {
  router.push({ name, query: {
    isLink: true,
  } });
};

const importClick = () => {
  closed();
  emit('click-import');
};
</script>
<style lang="less" scoped>
.fast-input-dialog {
  .fast-input-step {
    width: 60%;
    margin: 0 auto;
  }

  .info-content {
    padding: 12px;
    margin: 12px 0;
    font-size: 12px;
    color: #63656E;
    background: #F5F7FA;
    border-radius: 2px;

    .info-txt {
      color: #313238;

      .tips {
        border-bottom: 1px dashed #979BA5;
      }
    }

    p {
      line-height: 24px;
    }
  }

  .theme {
    position: relative;
    padding: 6px 12px 6px 30px;
    background: #F0F8FF;
    border: 1px solid #C5DAFF;
    border-radius: 2px;

    .theme-icon {
      position: absolute;
      top: 12px;
      left: 8px;
      font-size: 14px;
      color: #3A84FF;
    }
  }
}

:deep(.bk-dialog-next) {
  float: none;
  color: #fff;
  background-color: #3A84FF;
}
</style>
