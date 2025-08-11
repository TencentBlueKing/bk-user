import {
  PersonalCenterUsersData,
  PersonalCenterUserVisibleFieldsData,
} from '@/http/types/personalCenterFiles';

type CustomField = PersonalCenterUserVisibleFieldsData['custom_fields'][number];
export interface ExtrasCustomFields extends CustomField {
  value: string | string[]
}

export const useCustomFields = (data: PersonalCenterUsersData['extras'], customFields: PersonalCenterUserVisibleFieldsData['custom_fields']): ExtrasCustomFields[] => {
  const entries = Object.entries(data);
  const extras = customFields?.map(item => ({
    ...item,
    value: entries.find(([key]) => key === item.name)?.[1] || '',
  })) || [];

  return extras;
};
