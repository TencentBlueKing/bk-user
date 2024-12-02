import http from './fetch';
import { AuditListParams } from './types/operationHistory';

export const getAudit = (params: AuditListParams) => {
  // eslint-disable-next-line @typescript-eslint/naming-convention
  const { page, pageSize, operation, object_type, object_name, creator, created_at } = params;
  console.log(params);
  return http.get(`/api/v3/web/audit/?page_size=${pageSize}&page=${page}&operation=${operation}&object_type=${object_type}&object_name=${object_name}&creator=${creator}&created_at=${created_at}`);
};
