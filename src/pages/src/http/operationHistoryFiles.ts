import http from './fetch';
import { AuditListData, AuditListParams } from './types/operationHistory';
interface ResponseData<T> {
  data: T
}

export const getAudit = (params: AuditListParams) => http.get<ResponseData<AuditListData>>('/api/v3/web/audit/', params);
