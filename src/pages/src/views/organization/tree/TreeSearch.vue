<!--
  - Tencent is pleased to support the open source community by making Bk-User 蓝鲸用户管理 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
  -
  - License for Bk-User 蓝鲸用户管理:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->
<template>
  <div class="search-content-wrapper">
    <div class="search-box">
      <input type="text"
             :placeholder="$t('搜索')"
             v-model="searchKey"
             @input="debounceSearch"
             @keydown.up="selectUp"
             @keydown.down="selectDown"
             @keydown.enter="selectEnter" />
      <i class="icon icon-user-search"></i>
      <i v-show="searchKey" class="bk-icon icon-close-circle-shape" @click="closeSearch"></i>
      <div class="search-result" v-if="hasSelected">
        <div class="result-content">
          <div class="result-text">
            <span class="title">{{searchResult.groupName}}：</span>
            <span class="name" :class="{ 'chang-en': $i18n.locale === 'en' }">{{findSelectedText()}}</span>
          </div>
          <i class="icon icon-user-close" @click.stop="closeSearch"></i>
        </div>
      </div>
    </div>
    <div class="search-match" @click.stop>
      <div v-show="searchLoading" class="bk-loading king-loading">
        <div class="bk-loading-wrapper">
          <div class="bk-loading1">
            <div class="point point1" style="background: #63656e;"></div>
            <div class="point point2" style="background: #63656e;"></div>
            <div class="point point3" style="background: #63656e;"></div>
            <div class="point point4" style="background: #63656e;"></div>
          </div>
        </div>
      </div>
      <div class="search-wrapper" ref="searchWrapper"
           v-if="searchResult && searchList.length && !searchLoading" data-test-id="groupData">
        <ul class="groups-container">
          <li class="match-list" v-for="(group, groupIndex) in searchList" :key="'group' + groupIndex">
            <!-- 组织 -->
            <template v-if="group.type === 'department'">
              <div class="match-group">
                <span>{{$t('组织')}}</span>
                <template v-if="group.items.length > departmentLimitLength">
                  <span class="collapse-toggle" v-if="isDepartmentCollapsed"
                        @click="isDepartmentCollapsed = false">{{ $t('查看更多') }}</span>
                  <span class="collapse-toggle" v-else @click="isDepartmentCollapsed = true">{{ $t('收起') }}</span>
                </template>
              </div>
              <div data-test-id="departmentData">
                <ul class="items-container">
                  <li class="match-item"
                      v-for="(item, index) in group.items"
                      v-show="index < departmentLimitLength || !isDepartmentCollapsed"
                      :key="'department' + index"
                      :class="{ 'active': (activeType === 'department' && activeIndex === index) }"
                      @click="handleSelect(item)">
                    <p class="item-title">{{ item.name }}</p>
                    <p class="item-detail">{{ getDepartmentDetail(item) }}</p>
                  </li>
                </ul>
              </div>
            </template>
            <!-- 用户 -->
            <template v-if="group.type === 'user'">
              <div class="match-group">
                <span>{{$t('用户')}}</span>
                <template v-if="group.items.length > userLimitLength">
                  <span class="collapse-toggle" v-if="isUserCollapsed"
                        @click="isUserCollapsed = false">{{ $t('查看更多') }}</span>
                  <span class="collapse-toggle" v-else @click="isUserCollapsed = true">{{ $t('收起') }}</span>
                </template>
              </div>
              <div data-test-id="userDetailData">
                <ul class="items-container">
                  <li class="match-item"
                      v-for="(item, index) in group.items"
                      v-show="index < userLimitLength || !isUserCollapsed"
                      :key="'user' + index"
                      :class="{ 'active': (activeType === 'user' && activeIndex === index) }"
                      @click="handleSelect(item)">
                    <p class="item-title">
                      {{ item.username + '(' + item.display_name + ') ' }}
                      <span class="category-label">{{item.category_name}}</span>
                    </p>
                    <p class="item-detail">{{ getUserDetail(item) }}</p>
                  </li>
                </ul>
              </div>
            </template>
          </li>
          <li class="match-list" v-if="resultLength >= searchLength">
            <div class="match-group">{{$t('完善关键字搜索更多内容')}}</div>
          </li>
        </ul>
      </div>
      <p class="no-data" v-show="!searchList.length && isNodata && !searchLoading">{{$t('没有找到相关的结果')}}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      searchKey: '',
      // 预期返回多少条数据，越少越快
      searchLength: 40,
      // 实际返回的数据条数
      resultLength: 0,
      searchLoading: false,
      // 本次搜索的 id，过时的搜索不会触发行为
      searchId: 0,
      // debounce 变量
      timer: null,
      // 搜索结果是否为空
      isNodata: false,
      // 搜索结果
      searchList: [],
      // 当前默认选中的搜索结果
      searchResult: null,
      // 用户是否确定选择了搜索结果
      hasSelected: false,
      activeType: '',
      activeIndex: 0,
      // 限制长度，超过此长度默认折叠搜索项
      departmentLimitLength: 3,
      isDepartmentCollapsed: true,
      userLimitLength: 5,
      isUserCollapsed: true,
    };
  },
  methods: {
    getDepartmentDetail(itemInfo = this.searchResult) {
      return this.dealDepartmentPath(`${itemInfo.category_name}：${itemInfo.full_name}`);
    },
    getUserDetail(itemInfo = this.searchResult) {
      const { groupType, groupName } = itemInfo;
      if (groupType === 'username') {
        if (itemInfo.departments.length) {
          return this.dealDepartmentPath(`${itemInfo.category_name}：${itemInfo.departments[0].full_name}`);
        }
        return itemInfo.category_name;
      }
      return `${groupName}：${itemInfo[groupType]}`;
    },
    dealDepartmentPath(path) {
      const length = path.length;
      // 目前的宽度最多展示28个汉字
      if (length <= 28) {
        return path;
      }
      const array = path.split('');
      const deleteCount = length - 27;
      array.splice(13, deleteCount, '...');
      return array.join('');
    },
    findSelectedText(itemInfo = this.searchResult) {
      const groupType = itemInfo.groupType;
      if (groupType === 'department') {
        return itemInfo.full_name;
      }
      return itemInfo[groupType];
    },
    // 搜索 debounce
    debounceSearch() {
      clearTimeout(this.timer);
      if (!this.searchKey.trim().length) {
        this.closeSearch();
        return;
      }
      // 用户输入 a 500mm后搜索 a，在搜索的过程中输入了 b，在 500mm + b搜索时间 的这段时间里，搜索 a 的结果不处理，loading 不消失，即便还没到 500mm 也在 loading
      this.searchId += 1;
      this.timer = setTimeout(() => {
        this.handleSearch();
      }, 500);
    },
    async handleSearch() {
      try {
        const searchKey = this.searchKey.trim();
        this.searchLoading = true;
        const searchId = this.searchId;
        const res = await this.$store.dispatch('organization/getSearchResult', {
          searchKey,
          searchLength: this.searchLength,
        });
        if (searchId !== this.searchId || !this.searchKey.length) {
          return;
        }
        let resultLength = 0;

        const departmentArray = [];
        const userArray = [];
        res.data.forEach((group) => {
          if (group.items.length > 0) {
            resultLength += group.items.length;
            group.items.forEach((item) => {
              item.groupType = group.type;
              item.groupName = group.display_name;
              if (item.groupType === 'department') {
                departmentArray.push(item);
              } else {
                userArray.push(item);
              }
            });
          }
        });

        this.searchList = [];
        if (departmentArray.length) {
          this.searchList.push({
            type: 'department',
            items: departmentArray,
          });
        }
        if (userArray.length) {
          this.searchList.push({
            type: 'user',
            items: userArray,
          });
        }
        this.resultLength = resultLength;

        this.isDepartmentCollapsed = departmentArray.length > this.departmentLimitLength;
        this.isUserCollapsed = userArray.length > this.userLimitLength;
        this.isNodata = (!resultLength && searchKey.length !== 0);

        if (resultLength > 0) {
          const firstGroup = this.searchList[0];
          this.searchResult = firstGroup.items[0];
          this.activeIndex = 0;
          this.activeType = firstGroup.type;
        }
        // 这里不能放到 finally 因为逻辑不一定走到这里来，搜索 a 的过程中键入了 b，a 的搜索结果将被放弃
        // 这样做是因为如果键入 b，在 debounce 的这 500mm 里比如第 300mm 结果返回了，我们关闭了 loading 展示结果，200mm 后又开启 搜索 b 的 loading
        // 感觉就是我输入 b 后，loading => a 结果短暂出现 => loading => 出现 b 结果
        // 根据 searchId 优化后就是我输入 b 后 => loading => b 结果出现
        this.searchLoading = false;
      } catch (e) {
        console.warn(e);
        this.searchList = [];
        this.isNodata = true;
        this.searchLoading = false;
      }
    },
    // 删除搜索的结果
    closeSearch() {
      this.searchKey = '';
      this.searchLoading = false;
      this.searchList = [];
      this.searchResult = null;
      this.activeIndex = 0;
      this.activeType = '';
      this.isNodata = false;
      if (this.hasSelected === true) {
        this.$emit('searchTree', this.searchResult);
      }
      this.hasSelected = false;
    },
    selectUp() {
      this.activeIndex -= 1;
      for (let i = 0; i < this.searchList.length; i++) {
        if (this.searchList[i].type === this.activeType && this.activeIndex === -1) {
          // 移动到上一组
          if (i === 0) {
            // 当前为第一组，不移动
            this.activeIndex = 0;
          } else {
            // 移动到上一组
            this.activeType = this.searchList[i - 1].type;
            let isCollapsed;
            let limitLength;
            if (this.activeType === 'department') {
              isCollapsed = this.isDepartmentCollapsed;
              limitLength = this.departmentLimitLength;
            } else if (this.activeType === 'user') {
              isCollapsed = this.isUserCollapsed;
              limitLength = this.userLimitLength;
            }
            if (!isCollapsed) {
              limitLength = this.searchList[i - 1].items.length;
            }
            this.activeIndex = limitLength - 1;
          }
          return;
        }
      }
      this.calculateScroll('start');
    },
    selectDown() {
      this.activeIndex += 1;
      for (let i = 0; i < this.searchList.length; i++) {
        if (this.searchList[i].type === this.activeType) {
          // 确认移动的分组
          let isCollapsed;
          let limitLength;
          if (this.activeType === 'department') {
            isCollapsed = this.isDepartmentCollapsed;
            limitLength = this.departmentLimitLength;
          } else if (this.activeType === 'user') {
            isCollapsed = this.isUserCollapsed;
            limitLength = this.userLimitLength;
          }
          if (!isCollapsed) {
            limitLength = this.searchList[i].items.length;
          }
          if (this.activeIndex === limitLength) {
            // 当前组最后一个项目
            if (i === this.searchList.length - 1) {
              // 当前是最后一组，不移动
              this.activeIndex -= 1;
            } else {
              // 移动到下一组
              this.activeIndex = 0;
              this.activeType = this.searchList[i + 1].type;
            }
            return;
          }
        }
      }
      // 让scroll跟着index走
      this.calculateScroll('end');
    },
    selectEnter() {
      if (this.searchList.length === 0) return;
      let itemInfo = {};
      // 根据 groupType 和 activeIndex 找到搜索项
      for (let i = 0; i < this.searchList.length; i++) {
        if (this.searchList[i].type === this.activeType) {
          itemInfo = this.searchList[i].items[this.activeIndex];
          break;
        }
      }
      this.handleSelect(itemInfo);
    },
    // 点击搜索的结果： 1.this.searchResult抛给父级  2.加载对应的tree以及用户列表信息
    handleSelect(itemInfo) {
      if (this.isNodata) {
        return;
      }
      this.searchResult = itemInfo;
      this.searchList = [];
      this.hasSelected = true;
      this.$emit('searchTree', this.searchResult);
    },
    calculateScroll(type) {
      this.$nextTick(() => {
        const searchPanelPosInfo = document.querySelector('.search-match').getBoundingClientRect();
        const activeItemPosInfo = document.querySelector('.match-list .active').getBoundingClientRect();
        const minY = searchPanelPosInfo.top;
        const maxY = minY + 400;
        const topIsVisible = activeItemPosInfo.top >= minY && activeItemPosInfo.top < maxY;
        const bottomIsVisible = activeItemPosInfo.top + 36 >= minY && activeItemPosInfo.top + 36 < maxY;
        if (!(topIsVisible && bottomIsVisible)) {
          document.querySelector('.match-list .active').scrollIntoView({
            block: type,
          });
        }
      });
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../../../scss/mixins/scroller';

.search-content-wrapper {
  position: relative;
  width: calc(100% - 40px);
  margin: 20px;
  font-size: 12px;
}

.search-box {
  position: relative;
  background: #fff;

  input {
    padding-left: 35px;
    padding-right: 28px;
    display: block;
    width: 100%;
    height: 32px;
    line-height: 32px;
    color: #656770;
    border-radius: 2px;
    border: 1px solid #c4c6cc;
    transition: border linear .2s;

    &:focus {
      border-color: #3c96ff;
    }
  }

  .icon-user-search {
    position: absolute;
    left: 10px;
    top: 8px;
    font-size: 16px;
    color: #a0a4ad;
  }

  .icon-close-circle-shape {
    position: absolute;
    right: 8px;
    top: 9px;
    cursor: pointer;
    font-size: 14px;
    color: #c4c6cc;

    &:hover {
      color: #979ba5;
    }
  }

  .search-result {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 20;

    .result-content {
      position: relative;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin: 4px;
      width: calc(100% - 8px);
      height: 24px;
      line-height: 22px;
      color: rgba(115, 121, 135, 1);
      border: 1px solid #c4c6cc;
      border-radius: 2px;
      background: #fafbfd;

      .result-text {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        outline: none !important;

        .title {
          padding-left: 10px;
        }

        // .name {
        // }
      }

      .icon {
        width: 32px;
        padding: 0 10px;
        cursor: pointer;
      }
    }
  }
}

.search-match {
  position: absolute;
  top: 40px;
  left: 0;
  width: 380px;
  border-radius: 2px;
  background: #fff;
  z-index: 10;

  .king-loading {
    position: static;
    width: 100%;
    height: 62px;
    border: 1px solid #dcdee5;
    box-shadow: 0 2px 6px rgba(51, 60, 72, .1);

    .bk-loading1 {
      transform: scale(.7);
    }
  }

  .search-wrapper {
    position: static !important;
    max-height: 420px;
    overflow: hidden;
    overflow-y: auto;
    border: 1px solid #dcdee5;
    box-shadow: 0 2px 6px rgba(51, 60, 72, .1);

    @include scroller($backgroundColor: #e6e9ea, $width: 4px);
  }

  .match-list {
    color: #63656e;
    line-height: 16px;

    .match-group {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin: 0 20px;
      padding: 8px 0;
      color: #c4c6cc;

      .collapse-toggle {
        color: #3a84ff;
        cursor: pointer;
      }
    }

    &:not(:first-child) .match-group {
      border-top: 1px solid #f0f1f5;
    }

    .match-item {
      display: block;
      padding: 10px 20px 12px;
      cursor: pointer;

      &.active,
      &:hover {
        background: #e1ecff;
      }

      .item-title {
        margin-bottom: 4px;
        font-weight: bold;
        color: #63656e;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;

        .category-label {
          font-weight: normal;
          background: #f0f1f5;
          padding: 2px 4px;
        }
      }

      .item-detail {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        color: #979ba5;
      }
    }
  }

  .no-data {
    text-align: center;
    min-height: 62px;
    line-height: 60px;
    font-size: 14px;
    color: #979ba5;
    border: 1px solid #dcdee5;
    box-shadow: 0 2px 6px rgba(51, 60, 72, .1);
  }
}
</style>
