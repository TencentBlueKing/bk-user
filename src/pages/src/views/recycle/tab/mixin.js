export default {
  props: {
    dataList: {
      type: Array,
      required: true,
    },
    count: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      tableSearchKey: '',
      isDisabled: true,
      setting: {
        max: 3,
        fields: [],
        selectedFields: [],
        size: 'small',
      },
      pagination: {
        current: 1,
        count: 1,
        limit: 10,
      },
      batchSelectedList: [],
      selectedList: [],
      deleteText: '',
      isError: false,
      categoryIds: '',
    };
  },
  watch: {
    count: {
      immediate: true,
      handler(val) {
        this.pagination.count = val;
      },
    },
  },
  methods: {
    handleBatchDelete() {
      this.categoryIds = this.batchSelectedList.map(item => item.id).join(',');
      this.deleteDialog.isShow = true;
    },
    handleDelete(row) {
      this.categoryIds = row.id;
      this.deleteDialog.isShow = true;
    },
    handleSelect(selection) {
      this.batchSelectedList = selection;
    },
    handleSelectionChange(selection) {
      this.isDisabled = selection.length === 0;
      this.batchSelectedList = selection;
    },
    // 确认删除
    confirmDelete() {
      this.$store.dispatch('setting/categoriesHardDelete', {
        category_ids: this.categoryIds,
      }).then((res) => {
        if (res.result) {
          this.messageSuccess(this.$t('删除成功'));
        }
      })
        .catch((e) => {
          console.warn(e);
          this.deleteDialog.isShow = false;
        })
        .finally(() => {
          this.deleteDialog.isShow = false;
        });
    },
    updateSelectList(list) {
      this.activeList = list;
    },
    handleErrorNumber(val) {
      this.isError = val > 0;
    },
    handleEnter(key) {
      this.$emit('searchList', key, this.pagination.limit, this.pagination.current);
    },
    handleClear(key) {
      this.$emit('searchList', key, this.pagination.limit, this.pagination.current);
    },
    handlePageChange(page) {
      this.pagination.current = page;
      this.$emit('searchList', this.tableSearchKey, this.pagination.limit, this.pagination.current);
    },
    handlePageLimitChange(limit) {
      this.pagination.limit = limit;
      this.$emit('searchList', this.tableSearchKey, this.pagination.limit, this.pagination.current);
    },
    handleSettingChange({ fields, size }) {
      this.setting.size = size;
      this.setting.selectedFields = fields;
    },
  },
};
