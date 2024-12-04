import http from './fetch';
import { AuditListData, AuditListParams } from './types/operationHistory';
interface ResponseData<T> {
  data: T
}

export const getAudit = (params: AuditListParams) => {
  // eslint-disable-next-line @typescript-eslint/naming-convention
  const { page, pageSize, operation, object_type, object_name, creator, created_at } = params;
  return http.get<ResponseData<AuditListData>>(`/api/v3/web/audit/?page_size=${pageSize}&page=${page}&operation=${operation}&object_type=${object_type}&object_name=${object_name}&creator=${creator}&created_at=${created_at}`);
};
