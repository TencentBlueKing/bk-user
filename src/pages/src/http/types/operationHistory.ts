export interface AuditListParams {
  page: number,
  page_size: number
  operation: string,
  object_type: string,
  object_name: string,
  creator: string,
  start_at: string,
  end_at: string,
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
