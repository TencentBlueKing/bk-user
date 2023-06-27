/**
* by making 蓝鲸智云-用户管理(Bk-User) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License");
* you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and limitations under the License.
*/
/* eslint-disable no-unused-vars */
const methods = {
  install(Vue, options) {
    Vue.prototype.$getMessageByRules = function (that, passwordRules) {
      const { passwordMinLength, passwordMustIncludes } = passwordRules;
      const valueList = {
        letter: '大小写字母',
        lower: '小写字母',
        upper: '大写字母',
        int: '数字',
        special: '特殊字符（除空格）',
      };
      // 如果密码规则同时包含大小写字母
      let ruleList = [...passwordMustIncludes];
      if (ruleList.includes('lower') && ruleList.includes('upper')) {
        ruleList = ruleList.filter(item => item !== 'lower' && item !== 'upper');
        ruleList.unshift('letter');
      }

      const message = ruleList.map(item => that.$t(valueList[item])).join('，');
      return that.$t('密码长度为') + passwordMinLength + that.$t('-32个字符，必须包含') + message;
    };
    Vue.prototype.$validatePassportByRules = function (passport, passwordRules) {
      let { passwordMinLength } = passwordRules;
      // 首先判断一下长度
      if (passwordMinLength < 8 || passwordMinLength > 32) {
        passwordMinLength = 8;
      }
      if (passport.length < passwordMinLength || passport.length > 32) {
        return false;
      }
      // 需要判断的规则
      const ruleMaps = {
        lower: /(?=.*?[a-z])/,
        upper: /(?=.*?[A-Z])/,
        int: /(?=.*?[0-9])/,
        special: /(?=.*?[_#?~.,!@$%^&*-])/,
      };
      const regList = [];
      passwordRules.passwordMustIncludes.forEach((rule) => {
        regList.push(ruleMaps[rule]);
      });
      // 对密码进行验证
      for (let i = 0; i < regList.length; i++) {
        if (!passport.match(regList[i])) {
          return false;
        }
      }
      return true;
    };
    // 将对象转成带 region 的对象数组给 server
    Vue.prototype.$convertObjectToArray = function (obj) {
      try {
        const arrayData = [];
        Object.entries(obj).forEach((regionArray) => {
          const region = regionArray[0];
          Object.entries(regionArray[1]).forEach((regionData) => {
            const key = regionData[0];
            if (regionData[0] === 'dynamic_fields_mapping') {
              const value = {};
              if (regionData[1].length) {
                regionData[1].forEach((item) => {
                  if (item.key && item.value) {
                    const extendKey = item.key;
                    const extendValue = item.value;
                    this.$set(value, extendKey, extendValue);
                  }
                });
              }
              arrayData.push({ key, value, region });
            } else {
              const value = regionData[1];
              arrayData.push({ key, value, region });
            }
          });
        });
        return arrayData;
      } catch (e) {
        console.warn('参数错误', e);
      }
    };
    // 将从 server 获取的带 region 的对象数组转成对象
    Vue.prototype.$convertArrayToObject = function (arr) {
      try {
        const objectData = {};
        arr.forEach((regionObject) => {
          const { region, key, value } = regionObject;
          if (!objectData[region]) {
            objectData[region] = {};
          }
          objectData[region][key] = value;
          if (regionObject.key === 'dynamic_fields_mapping') {
            const valueList = [];
            Object.entries(regionObject.value).forEach((regionData) => {
              const key = regionData[0];
              const value = regionData[1];
              valueList.push({ key, value });
            });
            objectData[region][regionObject.key] = valueList;
          } else {
            const { key, value } = regionObject;
            if (!objectData[region]) {
              objectData[region] = {};
            }
            objectData[region][key] = value;
          }
        });
        return objectData;
      } catch (e) {
        console.warn('参数错误', e);
      }
    };

    Vue.prototype.$convertPassportRes = function (obj) {
      const objectData = {};
      const enabledKeys = ['max_password_history', 'freeze_after_days'];
      const list = [];
      let num = null;
      obj.forEach((regionArray) => {
        try {
          if (enabledKeys.includes(regionArray.key)) {
            const { key, value, enabled } = regionArray;
            this.$set(objectData, key, { value, enabled });
          } else {
            const { key, value } = regionArray;
            this.$set(objectData, key, value);
          }
        } catch (e) {
          console.warn('数据结构异常', e);
        }
      });
      Object.entries(objectData.exclude_elements_config).forEach((k) => {
        list.push(k[0]);
        num = k[1];
      });
      objectData.exclude_elements_config = list;
      this.$set(objectData, 'password_rult_length', num);
      return objectData;
    };

    Vue.prototype.$convertPassportInfoArray = function (arr, arr2) {
      try {
        const arrayData = [];
        const num = arr2.password_rult_length;
        Object.entries(arr).forEach((regionArray) => {
          const key = regionArray[0];
          let value = regionArray[1];
          let enabled = true;
          const obj = {};
          if (regionArray[1] && regionArray[1].value) {
            value = regionArray[1].value;
            enabled = regionArray[1].enabled;
          } else if (key === 'exclude_elements_config') {
            if (value.length) {
              Object.entries(value).forEach((k) => {
                this.$set(obj, k[1], num);
              });
              value = obj;
            } else {
              value = {};
            }
          } else if (key === 'password_rult_length') {
            return;
          }
          arrayData.push({ key, value, enabled });
        });
        return arrayData;
      } catch (e) {
        console.warn('数据结构异常', e);
      }
    };

    Vue.prototype.$convertPassportInfoObject = function (obj) {
      try {
        const objectData = {};
        const enabledKeys = ['max_password_history', 'freeze_after_days'];
        Object.entries(obj).forEach((regionArray) => {
          Object.entries(regionArray[1]).forEach((regionData) => {
            const key = regionData[0];
            const value = regionData[1];
            if (enabledKeys.includes(key)) {
              const enabled = true;
              this.$set(objectData, key, { value, enabled });
            } else {
              this.$set(objectData, key, value);
            }
          });
        });
        objectData.exclude_elements_config = [];
        this.$set(objectData, 'password_rult_length', '');
        return objectData;
      } catch (e) {
        console.warn('数据结构异常', e);
      }
    };

    Vue.prototype.$convertCustomField = function (arr) {
      try {
        const arrayData = [];
        arr.forEach((regionArray) => {
          if (!regionArray.builtin) {
            arrayData.push(regionArray);
          }
        });
        return arrayData;
      } catch (e) {
        console.warn('数据结构异常', e);
      }
    };

    Vue.prototype.$convertAccountRes = function (obj) {
      const objectData = {};
      obj.forEach((regionArray) => {
        try {
          const { key, value } = regionArray;
          this.$set(objectData, key, value);
        } catch (e) {
          console.warn('数据结构异常', e);
        }
      });
      return objectData;
    };

    Vue.prototype.$convertAccountInfo = function (arr) {
      try {
        const arrayData = [];
        Object.entries(arr).forEach((regionArray) => {
          const key = regionArray[0];
          const value = regionArray[1];
          const enabled = true;
          arrayData.push({ key, value, enabled });
        });
        return arrayData;
      } catch (e) {
        console.warn('数据结构异常', e);
      }
    };

    Vue.prototype.$convertDefault = function (arr) {
      try {
        const objectData = {};
        arr.forEach((regionObject) => {
          const { region, key, choices } = regionObject;
          if (!objectData[region]) {
            // 创建 region
            objectData[region] = {};
          }
          // 字段默认值
          objectData[region][key] = regionObject.default;

          const choicesArray = ['ssl_encryption', 'basic_pull_node', 'group_pull_node', 'bk_fields', 'mad_fields'];
          if (choicesArray.includes(key)) {
            this.$store.commit('catalog/updateChoices', {
              ...this.$store.state.catalog.choices,
              [key]: choices,
            });
          }
        });
        return objectData;
      } catch (e) {
        console.warn('参数错误', e);
      }
    },

    // 获取字符串长度，中文为 2 个字符长度
    Vue.prototype.$getStringLength = function (string) {
      // 匹配所有的中文
      const chineseReg = /[\u4E00-\u9FA5]/;
      let length = 0;
      for (let i = 0; i < string.length; i++) {
        if (chineseReg.test(string[i])) {
          length += 2;
        } else {
          length += 1;
        }
      }
      return length;
    };

    // 转换字符串尖括号
    Vue.prototype.$xssVerification = function (data) {
      if (typeof data === 'number') {
        data = data.toString();
      }
      return data.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    };
  },
};

export default methods;
