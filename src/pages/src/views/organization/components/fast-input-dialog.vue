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
                <p>{{$t('快速将用户录入到当前组织，如需添加到其他组织，请使用「导入」功能。')}}</p>
                <p>{{$t('录入字段为 设置 > 字段设置 中配置，如需修改可去 字段设置 修改。')}}</p>
            </div>
            <div class="info-content">
                <p>{{$t('录入格式：')}}<label class="info-txt">{{tipsInfo}}</label></p>
                <p>{{$t('信息之间使用逗号区隔，换行可输入多个用户')}}</p>
            </div>
            <bk-input
                v-model="val"
                type="textarea"
                :rows="4"
                :placeholder="$t('输入案例：zhangsan, 张三, 10000@qq.com, 15709998877')"
                :maxlength="100"
            />
        </div>
        <bk-table v-else 
            v-bkloading="{ loading: isLoading }"
            style="margin-top: 18px"
            :height="290"
            :columns="columns"
            :data="tableData"
            stripe
        >
        </bk-table>
    </div>
  </bk-dialog>
</template>

<script setup lang="ts">
  import { ref, watch } from 'vue';
  import { t } from '@/language/index';
  import useAppStore from '@/store/app';
  import { getFieldsTips, batchCreatePreview, operationsCreate } from '@/http/organizationFiles';
  const props = defineProps({
    isShow: {
      type: Boolean,
      default: false
    }
  });
  const appStore = useAppStore();
  const tipsInfo = ref('');
  const columns= [
    {
        label: t("用户名"),
        field: "username",
    },
    {
        label: t("全名"),
        field: "full_name",
    },
    {
        label: t("邮箱"),
        field: "email",
        width: 200
    },
    {
        label: t("手机号"),
        field: "phone"
    }
  ];
  const tableData = ref([]);
  const val = ref('');
  const emit = defineEmits(['update:isShow', 'success']);
  const objectSteps = ref([
    { title: t('录入用户'), icon: 1 },
    { title: t('预览确认'), icon: 2 },
  ]);
  const isLoading = ref(false);
  const currentId = ref(1);
  watch(() => props.isShow, async (val) => {
    if (val) {
      const res = await getFieldsTips();
      tipsInfo.value = (res.data || []).map(item => item.display_name).join(' + ') || '--';
    }
  })
  const handleNext = async () => {
    if (currentId.value < objectSteps.value.length) {
      currentId.value += 1;
      isLoading.value = true;
      const param = {
        user_infos: val.value.split('\n'),
        department_id: appStore.currentOrg.id,
      }
      try {
        const res = await batchCreatePreview(param);
        tableData.value = res.data;
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
        user_infos: val.value.split('\n'),
        department_id: appStore.currentOrg.id,
    }
    await operationsCreate(param);
    emit('success');
  }
  const closed = () => {
    emit('update:isShow', false)
  }
</script>
<style lang="less" scoped>
.fast-input-dialog {
    .fast-input-step {
        width: 60%;
        margin: 0 auto;
    }
    .info-content {
        margin: 12px 0;
        padding: 12px;
        font-size: 12px;
        background: #F5F7FA;
        border-radius: 2px;
        color: #63656E;
        .info-txt {
            color: #313238;
        }
        p {
            line-height: 24px;
        }
    }
    .theme {
        background: #F0F8FF;
        border: 1px solid #C5DAFF;
        border-radius: 2px;
        padding: 6px 12px 6px 30px;
        position: relative;
        .theme-icon {
            position: absolute;
            left: 8px;
            top: 12px;
            color: #3A84FF;
            font-size: 14px;
        }
    }
}

</style>
  