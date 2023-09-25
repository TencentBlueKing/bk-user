<script setup lang="ts">
const columns = [
  {
    label: '序号',
    type: 'index',
    sort: {
      value: 'asc',
    },
    width: 50,
    minWidth: 80,
  },
  {
    label: '名称/内网IP',
    field: 'ip',
  },
  {
    label: '来源',
    field: 'source',
    width: 80,
    filter: {
      list: [
        {
          text: 'QQ',
          value: 'QQ',
        },
        {
          text: '微信',
          value: '微信',
        },
        {
          text: 'Email',
          value: 'Email',
        },
      ],
    },
  },
  {
    label: '创建时间',
    field: 'create_time',
    sort: 'custom',
  },
  {
    label: '状态',
    field: 'status',
    sort: true,
  },
];
const tableData =  [
  {
    ip: '192.168.0.1',
    source: 'QQ',
    status: '创建中',
    create_time: '2018-05-25 15:02:24',
    selected: false,
  },
  {
    ip: '192.168.0.2',
    source: '微信',
    status: '正常',
    create_time: '2018-05-25 15:02:24',
    selected: false,
  },
  {
    ip: '192.168.0.3',
    source: 'QQ',
    status: '创建中',
    create_time: '2018-05-25 15:02:24',
    selected: false,
  },
  {
    ip: '192.168.0.3',
    source: 'QQ',
    status: '创建中',
    create_time: '2018-05-25 15:02:24',
    selected: true,
  },
  {
    ip: '192.168.0.3',
    source: 'QQ',
    status: '创建中',
    create_time: '2018-05-25 15:02:24',
    selected: false,
  },
];
</script>

<template>
  <bk-table
    row-hover="auto"
    :columns="columns"
    :data="tableData"
    show-overflow-tooltip
  />
</template>

<style lang="postcss" scoped>

</style>
