export default {
  methods: {
    // 展开子级并添加上背景 改变右侧的title
    updateChildren(item) {
      this.$store.dispatch('organization/getDataById', {
        id: item.id,
      }).then((res) => {
        if (!res.result) {
          return;
        }
        if (this.isAddChild) {
          item.showChildren = true;
        } else {
          item.showChildren = !item.showChildren;
        }
        this.isAddChild = false;
        res.data.children.forEach((element) => {
          this.filterTreeData(element, item, item.isLocalDepartment);
        });
        this.$set(item, 'children', res.data.children);
        this.$set(item, 'expanded', true);
      })
        .catch((e) => {
          console.warn(e);
        });
    },
    // 递归处理后台返回的数据
    filterTreeData(tree, directParent, isLocalDepartment = null) {
      // 通过判断存在 type 确定用户目录，手动添加 has_children
      this.$set(tree, 'async', tree.has_children);
      if (tree.type) {
        this.$set(tree, 'has_children', !!tree.departments.length);
      }
      this.$nextTick(() => {
        if (!tree.level) {
          this.$set(tree, 'level', directParent.level + 1);
        }
      });
      // 组织节点添加一个类型标记
      if (isLocalDepartment !== null) {
        tree.isLocalDepartment = isLocalDepartment;
      }
      tree.directParent = directParent;
      this.$set(tree, 'showOption', false);
      // 激活背景蓝色
      this.$set(tree, 'showBackground', false);
      // 展示子级组织
      this.$set(tree, 'showChildren', false);
      this.$set(tree, 'showLoading', false);

      if (tree.children && tree.children.length) {
        tree.children.forEach((item) => {
          this.filterTreeData(item, tree, isLocalDepartment);
        });
      }
    },
  },
};
