export interface AuditListParams {
  page: number,
  pageSize: number
  operation: string,
  object_type: string,
  object_name: string,
  creator: string,
  created_at: string
}

export interface AuditListData {
  count: number,
  results: {
    operation: string,
    object_type: string,
    object_name: string,
    creator: string,
    created_at: string,
  }[],
}
