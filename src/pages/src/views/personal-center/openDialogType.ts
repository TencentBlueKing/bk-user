export enum OpenDialogMode {
  Edit = 'edit',
  Verify = 'verify'
};

export enum OpenDialogType {
  email = 'email',
  phone = 'phone'
};

export enum OpenDialogSelect {
  inherit = 'true',
  custom = 'custom',
};

export enum openDialogResult {
  success = 'success',
  fail = 'danger'
};

export enum emailEidtable {
  YES = 'editable_directly',
  Verify = 'need_verify',
  No = 'not_editable'
};

export enum phoneEidtable {
  YES = 'editable_directly',
  Verify = 'need_verify',
  No = 'not_editable',
};

export enum formItemPropName {
  inheritEmail = 'inherit-email',
  inheritPhone = 'inherit-phone',
  customEmail = 'custom-email',
  customPhone = 'custom-phone',
  captcha = 'captcha',
};
