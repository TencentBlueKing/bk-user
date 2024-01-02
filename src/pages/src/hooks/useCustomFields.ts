export const useCustomFields = (data, customFields) => {
  const entries = Object.entries(data);
  const extras = customFields?.map(item => ({
    ...item,
    value: entries.find(([key]) => key === item.name)?.[1] || '',
  })) || [];

  return extras;
};
