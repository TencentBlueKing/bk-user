import axios from 'axios';
import Cookies from 'js-cookie';

/**
 * 上传 Excel 文件到指定数据源进行导入
 */
export const useDataSourceImport = () => {
  const uploadImport = async (dataSourceId: number, file: File, overwrite = false) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('overwrite', String(overwrite));
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-CSRFToken': Cookies.get(window.CSRF_COOKIE_NAME),
        'x-requested-with': 'XMLHttpRequest',
      },
      withCredentials: true,
    };
    const url = `${window.AJAX_BASE_URL}/api/v3/web/data-sources/${dataSourceId}/operations/import/`;
    return axios.post(url, formData, config);
  };

  return { uploadImport };
};
