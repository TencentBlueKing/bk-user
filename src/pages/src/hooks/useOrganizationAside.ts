
import { ref, watch } from 'vue';

import { getDepartmentsList } from '@/http/organizationFiles';
import useAppStore from '@/store/app';
import { IOrg } from '@/types/organization';

const appStore = useAppStore();

export default function useOrganizationAside(currentTenant: any) {
  const treeData = ref<any>({});

  const formatTreeData = (data = []) => {
    data.forEach((item) => {
      if (item.has_children) {
        item.children = [{}];
        item.async = true;
      }
    });
    return data;
  };

  const getRemoteData = async (item: IOrg) => {
    const res = await getDepartmentsList(item.id, currentTenant.value?.id);
    return formatTreeData(res?.data);
  };

  const handleNodeClick = (item: IOrg) => {
    appStore.currentOrg = item;
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

  /**
   * 添加子组织
   */
  const addNode = (id, node) => {
    const findNode = (item: IOrg, id: number) => {
      if (item.id === id) {
        return item;
      }
      if (item.children) {
        for (const child of item.children) {
          const result = findNode(child, id);
          if (result) {
            return result;
          }
        }
      }
      return null;
    };

    for (const item of treeData.value) {
      const current = findNode(item, id);
      if (current) {
        if (current.children) {
          current.children.push(node);
        } else {
          current.children = [node];
        }
      }
    }
  };

  /**
   * 重命名
   * @param node
   */
  const updateNode = (node: IOrg) => {
    const findNode = (item: IOrg, id: number) => {
      if (item.id === id) {
        return item;
      }
      if (item.children) {
        for (const child of item.children) {
          const result = findNode(child, id);
          if (result) {
            return result;
          }
        }
      }
      return null;
    };

    for (const item of treeData.value) {
      const current = findNode(item, node.id);
      if (current) {
        current.name = node.name;
      }
    }
  };

  return {
    treeData,
    handleNodeClick,
    getRemoteData,
    getPrefixIcon,
    addNode,
    updateNode,
  };
};
