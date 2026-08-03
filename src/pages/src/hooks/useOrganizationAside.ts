import { ref } from 'vue';

import { getDepartmentsList } from '@/http/organizationFiles';
import useOrganizationStore from '@/store/organization';
import { IOrg } from '@/types/organization';

export default function useOrganizationAside() {
  const organizationStore = useOrganizationStore();
  const treeRef = ref();
  const treeData = ref<IOrg[]>([]);
  /** 根部门请求缓存（按租户），同一租户下多数据源展开时复用，切换租户时清除。 */
  let rootDepartmentsCache: { tenantId: string; data: Promise<IOrg[]> } | null = null;

  /** 格式化为 bk-tree 可用的数据结构，并用数据源维度生成唯一节点 key。 */
  const formatDataSourceTreeData = (
    data = [] as IOrg[],
    dataSourceId?: number,
  ): IOrg[] => data
    .map((item) => {
      const sourceId = item.data_source_id ?? dataSourceId;
      return {
        ...item,
        nodeType: 'department',
        departmentId: item.id,
        treeKey: `department:${sourceId}:${item.id}`,
        async: item.has_children,
      };
    });

  /** 当前租户的数据源作为部门树的固定一级节点。 */
  const buildSourceTree = (): IOrg[] => organizationStore.currentTenant.data_sources.map(source => ({
    id: source.id,
    name: source.name,
    data_source_id: source.id,
    nodeType: 'source',
    treeKey: `source:${source.id}`,
    logo: source.logo,
    plugin_id: source.plugin_id,
    async: true,
  }));

  /** 获取指定租户的根部门列表。 */
  const getRootDepartments = async (tenantId: string) => {
    if (!rootDepartmentsCache || rootDepartmentsCache.tenantId !== tenantId) {
      const data = getDepartmentsList(0, tenantId)
        .then(res => res.data)
        .catch((error) => {
          rootDepartmentsCache = null;
          throw error;
        });
      rootDepartmentsCache = { tenantId, data };
    }
    return rootDepartmentsCache.data;
  };

  /** 清除根部门请求缓存（切换租户时调用）。 */
  const clearRootDepartmentsCache = () => {
    rootDepartmentsCache = null;
  };

  /** 获取远程数据 */
  const getRemoteData = async (item: Partial<IOrg>, currentTenantId: string) => {
    const dataSourceId = Number(item.data_source_id);

    // 数据源节点，获取根部门列表
    if (item.nodeType === 'source') {
      const rootDepartments = await getRootDepartments(currentTenantId);
      return formatDataSourceTreeData(rootDepartments, dataSourceId);
    }

    // 部门节点，获取子部门列表
    const res = await getDepartmentsList(item.id, currentTenantId);
    return formatDataSourceTreeData(res.data, dataSourceId);
  };

  const getPrefixIcon = (item: { children?: any[] }, renderType: string) => {
    if (renderType === 'node_action') {
      return 'default';
    }

    return {
      node: 'span',
      className: 'bk-sq-icon icon-file-close pr-1',
      style: {
        color: '#A3C5FD',
      },
    };
  };

  const isTargetNode = (item: IOrg, id: number | string, dataSourceId?: number) => item.nodeType === 'department'
    && item.id === id
    && (dataSourceId === undefined || item.data_source_id === dataSourceId);

  const findNode = (
    item: IOrg,
    id: number | string,
    dataSourceId?: number,
  ): IOrg | null => {
    if (item.treeKey === id || isTargetNode(item, id, dataSourceId)) {
      return item;
    }
    if (item.children) {
      for (const child of item.children) {
        const result = findNode(child, id, dataSourceId);
        if (result) {
          return result;
        }
      }
    }
    return null;
  };

  /**
   * 添加子组织
   */
  const addNode = (id: number, node: IOrg) => {
    const dataSourceId = node.data_source_id ?? organizationStore.selectedOrg.dataSourceId;
    const [formattedNode] = formatDataSourceTreeData([node], dataSourceId);
    const sourceNode = treeData.value.find(item => (
      item.nodeType === 'source' && item.data_source_id === dataSourceId
    ));

    // id 为 0 表示添加到当前数据源根节点。
    if (id === 0 && sourceNode) {
      if (!sourceNode.children) {
        sourceNode.children = [];
      }
      sourceNode.children.push(formattedNode);
      return;
    }

    for (const item of treeData.value) {
      const current = findNode(item, id, dataSourceId);
      if (current) {
        if (!current.children) {
          current.children = [];
        }
        current.children.push(formattedNode);
        break;
      }
    }
  };

  /**
   * 删除组织
   */
  const deleteDept = (id: number, list: IOrg[], dataSourceId?: number): boolean => {
    for (let i = 0; i < list.length; i++) {
      const item = list[i];
      if (isTargetNode(item, id, dataSourceId)) {
        list.splice(i, 1);
        return true;
      }
      if (item.children && deleteDept(id, item.children, dataSourceId)) {
        return true;
      }
    }
    return false;
  };

  const deleteNode = (id: number) => {
    deleteDept(id, treeData.value, organizationStore.selectedOrg.dataSourceId);
  };

  /**
   * 重命名
   * @param node
   */
  const updateNode = (node: IOrg) => {
    for (const item of treeData.value) {
      const current = findNode(
        item,
        node.id,
        node.data_source_id ?? organizationStore.selectedOrg.dataSourceId,
      );
      if (current) {
        current.name = node.name;
        break;
      }
    }
  };

  return {
    treeRef,
    treeData,
    buildSourceTree,
    formatDataSourceTreeData,
    getRemoteData,
    clearRootDepartmentsCache,
    getPrefixIcon,
    addNode,
    deleteNode,
    updateNode,
  };
};
