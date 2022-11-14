# 蓝鲸用户管理
![](docs/images/logo.png)

---
[![license](https://img.shields.io/badge/license-mit-green.svg?style=flat)](https://github.com/TencentBlueKing/bk-user/blob/master/LICENSE)
[![Release Version](https://img.shields.io/badge/bk--user-2.3.4-green)](https://github.com/TencentBlueKing/bk-user/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-green.svg)](https://github.com/TencentBlueKing/bk-user/pulls)

简体中文 | [English](readme_en.md)

蓝鲸用户管理是蓝鲸智云提供的企业组织架构和用户管理解决方案，为企业统一登录提供认证源服务。

## 总览

- [架构设计](docs/architecture.md)
- [代码目录](docs/develop_guide.md)

## 功能

- 支持多层级的组织架构管理
- 支持通过多种方式同步数据：OpenLDAP、Microsoft Active Directory(MAD)、Excel 表格等
- 支持用户密码周期管理、密码强度校验、用户登录试错限制、邮件发送随机密码等安全措施

详细介绍请参考[功能说明](https://bk.tencent.com/docs/document/6.0/146/6638)

## 快速开始

- [Helm 快速部署指引](/deploy/helm/bk-user/README.md)
- [本地开发部署指引](/docs/develop_guide.md)

## 路线图

- [版本日志](https://github.com/TencentBlueKing/bk-user/releases)

## 支持

- [产品白皮书](https://bkdocs-1252002024.file.myqcloud.com/ZH/6.0/%E7%94%A8%E6%88%B7%E7%AE%A1%E7%90%86/%E7%94%A8%E6%88%B7%E7%AE%A1%E7%90%86.pdf)
- [蓝鲸论坛](https://bk.tencent.com/s-mart/community)

## 蓝鲸社区
- [BK-CI](https://github.com/Tencent/bk-ci)：蓝鲸持续集成平台是一个开源的持续集成和持续交付系统，可以轻松将你的研发流程呈现到你面前。
- [BK-BCS](https://github.com/Tencent/bk-bcs)：蓝鲸容器管理平台是以容器技术为基础，为微服务业务提供编排管理的基础服务平台。
- [BK-CMDB](https://github.com/Tencent/bk-cmdb)：蓝鲸配置平台（蓝鲸CMDB）是一个面向资产及应用的企业级配置管理平台。
- [BK-PaaS](https://github.com/Tencent/bk-PaaS)：蓝鲸PaaS平台是一个开放式的开发平台，让开发者可以方便快捷地创建、开发、部署和管理SaaS应用。
- [BK-SOPS](https://github.com/Tencent/bk-sops)：标准运维（SOPS）是通过可视化的图形界面进行任务流程编排和执行的系统，是蓝鲸体系中一款轻量级的调度编排类SaaS产品。

## 贡献
对于项目感兴趣，想一起贡献并完善项目请参阅 [Contributing Guide](docs/contributing.md)。

[腾讯开源激励计划](https://opensource.tencent.com/contribution) 鼓励开发者的参与和贡献，期待你的加入。

## 协议

基于 MIT 协议， 详细请参考[LICENSE](LICENSE)
