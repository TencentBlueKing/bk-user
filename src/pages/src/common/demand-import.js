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
import Vue from 'vue';
import {
  bkBadge,
  bkButton,
  bkCheckbox,
  bkCheckboxGroup,
  bkCol,
  bkCollapse,
  bkCollapseItem,
  bkContainer,
  bkDatePicker,
  bkDialog,
  bkDropdownMenu,
  bkException,
  bkForm,
  bkFormItem,
  bkInfoBox,
  bkInput,
  bkLoading,
  bkMessage,
  bkNavigation,
  bkNavigationMenu,
  bkNavigationMenuItem,
  bkNotify,
  bkOption,
  bkOptionGroup,
  bkPagination,
  bkPopover,
  bkProcess,
  bkProgress,
  bkRadio,
  bkRadioGroup,
  bkRadioButton,
  bkRoundProgress,
  bkRow,
  bkSearchSelect,
  bkSelect,
  bkSideslider,
  bkSlider,
  bkSteps,
  bkSwitcher,
  bkTab,
  bkTabPanel,
  bkTable,
  bkTableColumn,
  bkTagInput,
  bkTag,
  bkTimePicker,
  bkTimeline,
  bkTransfer,
  bkTree,
  bkUpload,
  bkClickoutside,
  bkTooltips,
  bkSwiper,
  bkRate,
  bkAnimateNumber,
  bkVirtualScroll,
  bkOverflowTips,
  bkVersionDetail,
  bkResizeLayout,
  bkIcon,
  bkTableSettingContent,
  bkLink,
} from 'bk-magic-vue';

// bkDiff 组件体积较大且不是很常用，因此注释掉。如果需要，打开注释即可
// import { bkDiff } from 'bk-magic-vue'

// components use
Vue.use(bkBadge);
Vue.use(bkButton);
Vue.use(bkCheckbox);
Vue.use(bkCheckboxGroup);
Vue.use(bkCol);
Vue.use(bkCollapse);
Vue.use(bkCollapseItem);
Vue.use(bkContainer);
Vue.use(bkDatePicker);
Vue.use(bkDialog);
Vue.use(bkDropdownMenu);
Vue.use(bkException);
Vue.use(bkForm);
Vue.use(bkFormItem);
Vue.use(bkInput);
Vue.use(bkNavigation);
Vue.use(bkNavigationMenu);
Vue.use(bkNavigationMenuItem);
Vue.use(bkOption);
Vue.use(bkOptionGroup);
Vue.use(bkPagination);
Vue.use(bkPopover);
Vue.use(bkProcess);
Vue.use(bkProgress);
Vue.use(bkRadio);
Vue.use(bkRadioGroup);
Vue.use(bkRadioButton);
Vue.use(bkRoundProgress);
Vue.use(bkRow);
Vue.use(bkSearchSelect);
Vue.use(bkSelect);
Vue.use(bkSideslider);
Vue.use(bkSlider);
Vue.use(bkSteps);
Vue.use(bkSwitcher);
Vue.use(bkTab);
Vue.use(bkTabPanel);
Vue.use(bkTable);
Vue.use(bkTableColumn);
Vue.use(bkTagInput);
Vue.use(bkTag);
Vue.use(bkTimePicker);
Vue.use(bkTimeline);
Vue.use(bkTransfer);
Vue.use(bkTree);
Vue.use(bkUpload);
Vue.use(bkSwiper);
Vue.use(bkRate);
Vue.use(bkAnimateNumber);
Vue.use(bkVersionDetail);
Vue.use(bkVirtualScroll);
// bkDiff 组件体积较大且不是很常用，因此注释了。如果需要，打开注释即可
// Vue.use(bkDiff)

// directives use
Vue.use(bkClickoutside);
Vue.use(bkTooltips);
Vue.use(bkLoading);
bkOverflowTips.setDefaultProps({
  delay: [400, 0],
});
Vue.use(bkOverflowTips);
Vue.use(bkResizeLayout);
Vue.use(bkIcon);
Vue.use(bkTree);
Vue.use(bkTableSettingContent);
Vue.use(bkLink);

// Vue prototype mount
Vue.prototype.$bkInfo = bkInfoBox;
Vue.prototype.$bkMessage = bkMessage;
Vue.prototype.$bkNotify = bkNotify;
