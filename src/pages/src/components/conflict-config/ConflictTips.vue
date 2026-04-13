<template>
  <div>
    <template v-if="type === 'simple'">
      <template v-if="!hasOtherDataSource">
        <div class="flex items-center px-[16px] py-[8px] rounded-[2px]">
          <i class="user-icon icon-info-i text-[14px] text-[#979BA5] mr-[8px]" />
          <span class="text-[12px] text-[#63656E] leading-[20px]">
            {{ $t('若后续存在入多个数据源的需求，建议您提前为用户名设置统一的冲突规则') }}
          </span>
        </div>
      </template>
      <template v-else>
        <div class="flex items-center px-[16px] py-[8px] rounded-[2px]">
          <i class="user-icon icon-remind-fill text-[14px] text-[#EA3636] mr-[8px]" />
          <span class="text-[12px] text-[#63656E] leading-[20px]">
            {{ $t('当前租户下发现其他数据源，请完成字段冲突时的规则配置') }}
          </span>
        </div>
      </template>
    </template>
    <template v-else>
      <template v-if="!hasOtherDataSource">
        <bk-alert theme="info">
          {{ $t('若后续存在入多个数据源的需求，建议您提前为用户名设置统一的冲突规则') }}
        </bk-alert>
      </template>
      <template v-else>
        <bk-alert theme="danger">
          {{ $t('当前租户下发现其他数据源，请完成字段冲突时的规则配置') }}
        </bk-alert>
      </template>
    </template>
  </div>
</template>

<script lang="ts" setup>
interface IProps {
  type?: 'simple' | 'alert';
  hasOtherDataSource?: boolean;
}

withDefaults(defineProps<IProps>(), {
  type: 'simple',
  hasOtherDataSource: false,
});

</script>
