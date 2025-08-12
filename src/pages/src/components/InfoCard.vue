<template>
  <div class="mt-[24px]">
    <ul class="details-info">
      <li class="py-[16px] px-[24px] mb-[16px] bg-[#fff] rounded-[2px] shadow-[0_2px_4px_0_#1919290d]">
        <div class="flex items-baseline justify-between">
          <p class="text-[14px] font-bold">
            {{ title }}
          </p>
        </div>
        <slot></slot>
      </li>
    </ul>
  </div>
</template>

<script lang="ts" setup>
interface IProps {
  title: string
}
defineProps<IProps>();
</script>
