<template>
  <div>
    <LabelContent :label="$t('用户名冲突规则')">
      <span v-if="config.rule === 'unchanged'">
        {{ $t('不配置，发生冲突时手动处理') }}
      </span>
      <span v-else-if="config.rule === 'add_affix'">
        {{ $t('为新数据源统一添加前后缀') }}
      </span>
      <div
        v-if="config.rule === 'add_affix'"
        class="bg-[#F5F7FA] p-[12px] mt-[2px] text-[#494B50] text-[14px] flex items-center"
      >
        <template v-if="config.prefix">
          <span>{{ $t('新用户名 ( username )') }} =</span>
          <div class="bg-[#DCDEE5] rounded-[2px] px-[8px] h-[22px] leading-[22px] mx-[8px]">
            {{ config.prefix }}
          </div>
          <span>{{ $t('用户名 ( username )') }}</span>
        </template>
        <template v-else-if="config.suffix">
          <span>{{ $t('新用户名 ( username )') }} =</span>
          <span class="mx-[8px]">{{ $t('用户名 ( username )') }}</span>
          <div class="bg-[#DCDEE5] rounded-[2px] px-[8px] h-[22px] leading-[22px]">
            {{ config.suffix }}
          </div>
        </template>
      </div>
    </LabelContent>
  </div>
</template>

<script setup lang="ts">
import LabelContent from '@/components/layouts/LabelContent.vue';

interface UsernameGenerateConfig {
  rule: 'unchanged' | 'add_affix';
  prefix?: string;
  suffix?: string;
}

interface IProps {
  config: UsernameGenerateConfig;
}

defineProps<IProps>();
</script>
