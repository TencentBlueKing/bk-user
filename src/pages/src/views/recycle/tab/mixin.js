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
    isDataEmpty: {
      type: Boolean,
      required: false,
    },
    isSearchEmpty: {
      type: Boolean,
      required: false,
    },
    isDataError: {
      type: Boolean,
      required: false,
    },
  },
  data() {
    return {
      tableSearchKey: '',
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
      deleteText: '',
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
    handleEnter(key) {
      this.$emit('searchList', key, this.pagination.limit, this.pagination.current);
    },
    handleClear(key) {
      this.tableSearchKey = key;
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
