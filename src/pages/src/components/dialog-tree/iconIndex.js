export default {
  name: 'Icon',
  props: {
    type: {
      type: String,
      required: true,
    },
    bk: {
      type: Boolean,
      default: false,
    },
  },

  render(h) {
    const classes = {
      'iam-icon': true,
    };
    if (this.bk) {
      delete classes['iam-icon'];
      classes['bk-icon'] = true;
      classes[`icon-${this.type}`] = true;
    } else {
      classes[`iamcenter-${this.type}`] = true;
    }
    return h('i', {
      class: classes,
      props: this.$attrs,
      on: this.$listeners,
    });
  },
};
