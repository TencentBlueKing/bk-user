import http from './fetch';
import { ResponseData } from './types';
import { AuditListData, AuditListParams } from './types/operationHistory';

export const getAudit = (params: AuditListParams) => http.get<ResponseData<AuditListData>>('/api/v3/web/audit/', params);
