# 2.2.x 升级注意事项

## 旧版本 v1 APIs 已被移除

在更早的用户管理版本中存在 `v1` 版本的 API，一些旧版本的服务可能有所依赖，但是由于 `v1` 版本存在一些问题：
- 协议较为潦草，不易扩展
- 代码基础薄弱，年代久远，不易维护

考虑到上述因素，我们决定在开源版中去掉了这部分 API 支持。

如果仍旧依赖 `v1` API，**请暂缓升级到 `2.3.x` 版本**，并积极推动相关服务的改造升级， 使用 `v2` 版本 API 完全替代。

## `no_page` 参数将从 v2 APIs 中移除

在企业版/社区版 2.2.x 中，存在 `no_page` 参数用来全量拉取某一类资源，例如拉取全量的用户信息，用作产品页面上的人员选择器(**已有完美通用方案，请迁移**)。

由于全量拉取的数据量较大，而且一些使用场景的拉取频次较高，导致了不少问题：
- 人员选择器拉取速度慢，页面卡死
- 占满用户管理 API 服务的 worker，导致 API 性能整体下降

所以在开源的版本中，我们将去除 `no_page` 参数，仅会在 2.3.x 的前几个版本中保留，请尽快迁移，具体方案可以参考本文下一节。

### 迁移方案

在去掉全量拉取数据参数之后，我们只支持通过**分页**的方式进行数据拉取操作。
所以如果你的产品仍有需求获取到全量数据，请通过分页方式批量拉取数据。

Python 示例

(来源: [用户管理 SaaS 分页拉取](https://github.com/TencentBlueKing/bk-user/blob/master/src/saas/bkuser_shell/common/viewset.py#L99))

```python
def get_paging_results(list_func: Callable, page_size: int = 50, **kwargs) -> list:
        """按照 id 排序分页拉取"""

        # 后端 API 服务中 id 都是自增的，所以按照 id 排序，新增内容只会往列表最后插入
        first_results = list_func(page_size=page_size, ordering="id", **kwargs)
        count = first_results["count"]
        paging_results: list = first_results["results"]

        if count <= page_size:
            return paging_results

        # 剩余的迭代拉取次数(减去第一次)
        post_times = int(math.ceil(count / page_size)) - 1
        modified_during_list = False
        for i in range(post_times):
            # 从第二页开始拉取
            r = list_func(page_size=page_size, ordering="id", page=i + 2, **kwargs)
            paging_results.extend(r["results"])

            if r["count"] != count:
                modified_during_list = True

        if modified_during_list:
            # 当前使用的 count/page 的分页方式并不能保证后端在循环分页请求期间数据有更新
            # 由于通过 SaaS 重新刷新的操作是廉价的，所以我们并不针对这样小概率的场景做额外的操作
            logger.warning("data changed during listing %s", list_func)

        return paging_results
```

默认地，我们设置了 [每页最大条目数 2000](https://github.com/TencentBlueKing/bk-user/blob/master/src/api/bkuser_core/config/common/system.py#L65) ，可以通过部署的环境变量修改。

