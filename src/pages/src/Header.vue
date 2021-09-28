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
  <div class="header-container">
    <div class="header-left">
      <h1 class="title-logo" @click="goHome">
        <i class="user-icon icon-user-logo-i"></i>
        <span class="title">{{ $t('蓝鲸用户管理') }}</span>
      </h1>
      <p class="nav-list">
        <a href="javascript:void(0);"
           :class="$route.name === 'organization' && 'router-link-active'"
           @click="goTo('organization')">{{ $t('组织架构') }}
        </a>
        <a href="javascript:void(0);"
           :class="$route.name === 'catalog' && 'router-link-active'" @click="goTo('catalog')">{{ $t('用户目录') }}</a>
        <a href="javascript:void(0);"
           :class="$route.name === 'audit' && 'router-link-active'" @click="goTo('audit')">{{ $t('审计') }}</a>
        <a href="javascript:void(0);"
           :class="$route.name === 'setting' && 'router-link-active'" @click="goTo('setting')">{{ $t('设置') }}</a>
      </p>
    </div>
    <div class="header-right" data-test-id="list_menuInfo">
      <bk-dropdown-menu ref="dropdownHelp"
                        align="center"
                        @show="showHelpDropdown = true"
                        @hide="showHelpDropdown = false">
        <div class="question-icon-trigger" :class="showHelpDropdown && 'active'" slot="dropdown-trigger">
          <div class="icon-circle-container">
            <span class="bk-icon icon-question-circle-shape"></span>
          </div>
        </div>
        <ul class="bk-dropdown-list" slot="dropdown-content">
          <li>
            <a :href="docUrl" target="_blank">{{ $t('产品文档') }}</a>
            <a href="javascript:void(0);" @click.stop="openVersionLog">{{ $t('版本日志') }}</a>
            <a href="https://bk.tencent.com/s-mart/community" target="_blank">{{ $t('问题反馈') }}</a>
          </li>
        </ul>
      </bk-dropdown-menu>
      <span class="name">{{ userInfo.username }}</span>
    </div>
    <!-- 版本日志 -->
    <bk-version-detail
      :show.sync="showVersionLog"
      :version-list="versionList"
      :current-version="versionList[0] ? versionList[0].title : ''"
      :get-version-detail="handleGetVersionDetail"
      :get-version-list="handleGetVersionList">
      <div v-if="selectedVersion" class="version-log-slot">
        <h2 class="title">【{{ selectedVersion }}】{{ $t('版本更新明细') }}</h2>
        <div v-for="(detail, project) in selectedVersionChangeLogs" :key="project">
          <h3 v-if="project">{{ project }}</h3>
          <p v-for="(item, index) in detail" :key="index" class="content">{{ item }}</p>
        </div>
      </div>
      <div v-else class="version-log-slot empty">
        <bk-exception class="exception-wrap-item exception-part" type="empty" scene="part"></bk-exception>
      </div>
    </bk-version-detail>
  </div>
</template>

<script>
export default {
  data() {
    return {
      showHelpDropdown: false,
      showVersionLog: false,
      versionList: [], // 版本日志列表
      selectedVersion: '', // 当前选择的版本
      selectedVersionChangeLogs: [], // 当前选择的版本北荣
      docUrl: window.BK_DOC_URL,
      userInfo: { // 登录用户信息
        logo: '',
        username: '',
      },
    };
  },
  created() {
    this.initUserInfo();
  },
  methods: {
    async initUserInfo() {
      try {
        const res = await this.$store.dispatch('getUserInfo');
        this.userInfo = res.data;
      } catch (e) {
        console.warn(e);
      }
    },
    goTo(route) {
      if (this.$route.name === route) {
        this.$emit('reloadRouter');
      } else {
        this.$router.push({
          name: route,
        });
      }
    },
    goHome() {
      if (this.$route.name === 'organization') {
        location.reload();
      } else {
        this.$router.push({
          name: 'organization',
        });
      }
    },
    openVersionLog() {
      this.$refs.dropdownHelp.hide();
      this.showVersionLog = true;
    },
    async handleGetVersionList() {
      try {
        const res = await this.$store.dispatch('getVersionLog');
        const typeMap = {
          NEW: this.$t('新增'),
          FIX: this.$t('修复'),
          OPTIMIZATION: this.$t('优化'),
        };
        const projectMap = {
          SaaS: 'SaaS',
          API: 'API',
          __Global__: '',
        };
        this.versionList = res.data.versions.map((item) => {
          const changeLogs = {};
          item.changeLogs.forEach((projectDetail) => {
            const { project, detail } = projectDetail;
            const projectChanges = [];
            const projectSub = projectMap[project];

            detail.forEach((changeLog) => {
              const { content, type } = changeLog;
              const typeText = typeMap[type];
              content.forEach((rowText) => {
                projectChanges.push(typeText + rowText);
              });
            });
            changeLogs[projectSub] = projectChanges;
          });
          return {
            title: item.version,
            date: item.date,
            changeLogs,
          };
        });
      } catch (e) {
        console.warn(e);
      }
    },
    handleGetVersionDetail(val) {
      this.selectedVersion = val.title;
      this.selectedVersionChangeLogs = val.changeLogs;
      return Promise.resolve();
    },
  },
};
</script>

<style lang="scss" scoped>
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  margin-bottom: 20px;
  padding: 0 25px;
  min-width: 1180px;
  height: 60px;
  background: #182132;

  .header-left {
    display: flex;
    align-items: center;
    font-weight: 400;

    .title-logo {
      display: flex;
      align-items: center;
      color: #fff;
      cursor: pointer;

      > .icon-user-logo-i {
        color: #458df4;
        font-size: 30px;
      }

      > .title {
        margin-left: 10px;
        font-size: 18px;
        font-weight: 600;
        color: #979ba5;
      }
    }

    .nav-list {
      font-size: 14px;
      height: 60px;

      a {
        position: relative;
        display: inline-block;
        vertical-align: middle;
        line-height: 60px;
        padding: 0 10px;
        text-align: center;
        color: rgba(151, 155, 165, 1);
        background: #182132;
        transition: all .3s;

        &:first-child {
          margin-left: 90px;
        }

        &.router-link-active {
          color: #fff;
          background: #26304a;
          transition: all .3s;
        }

        &:hover {
          color: #fff;
          transition: all .3s;
        }
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;

    .name {
      height: 19px;
      line-height: 19px;
      font-size: 14px;
      color: #96a2b9;
      cursor: default;
    }

    .question-icon-trigger {
      height: 60px;
      display: flex;
      justify-content: center;
      align-items: center;
      margin: 0 6px;
      cursor: pointer;

      .icon-circle-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 32px;
        height: 32px;
        border-radius: 16px;
        transition: all .2s;

        .bk-icon {
          color: #979ba5;
          font-size: 16px;
          transition: all .2s;
        }
      }

      &:hover,
      &.active {
        .icon-circle-container {
          background: #252f43;
          transition: all .2s;

          .bk-icon {
            color: #3a84ff;
            transition: all .2s;
          }
        }
      }
    }
  }
}

.version-log-slot {
  .title {
    margin: 18px 0;
  }

  .content {
    margin: 14px 0;
  }

  &.empty {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 90%;
  }
}
</style>
