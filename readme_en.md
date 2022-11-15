# BlueKing Organization Management
![](docs/images/logo.png)

---
[![license](https://img.shields.io/badge/license-mit-green.svg?style=flat)](https://github.com/TencentBlueKing/bk-user/blob/master/LICENSE)
[![Release Version](https://img.shields.io/badge/bk--user-2.3.3-green)](https://github.com/TencentBlueKing/bk-user/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-green.svg)](https://github.com/TencentBlueKing/bk-user/pulls)

[简体中文](readme.md) | English

`Bk-User` is an organization-management solution provided by [Tencent BlueKing](https://bk.tencent.com), which provides data source for unified login of enterprises.

## Overview

- [Architecture](docs/architecture.md)
- [Structure](docs/develop_guide.md)

## Features

- Support multi-level organizational structure management
- Support for synchronizing data in a variety of ways, including: OpenLDAP、Microsoft Active Directory(MAD)、Excel
- Supports multiple security measures such as user password cycle management, password strength verification, user login trial and error restrictions, and email sending random passwords

For details, please refer to [features](https://bk.tencent.com/docs/document/6.0/146/6638)


## Getting Started

- [Deploy by Helm](/deploy/helm/bk-user/README.md)
- [Local Developing](/docs/develop_guide.md)

## Roadmap

- [Changelog](https://github.com/TencentBlueKing/bk-user/releases)

## Supporting

- [White Paper](https://bkdocs-1252002024.file.myqcloud.com/ZH/6.0/%E7%94%A8%E6%88%B7%E7%AE%A1%E7%90%86/%E7%94%A8%E6%88%B7%E7%AE%A1%E7%90%86.pdf)
- [BlueKing Official Forum](https://bk.tencent.com/s-mart/community)

## BlueKing Community
- [BK-CI](https://github.com/Tencent/bk-ci): BlueKing Continuous Integration is a continuous integration and continuous delivery system that can easily present your R & D process to you.
- [BK-BCS](https://github.com/Tencent/bk-bcs): BlueKing Container Service is an orchestration platform for microservices based on container technology.
- [BK-BCS-SaaS](https://github.com/Tencent/bk-bcs-saas): SaaS of BlueKing Container Service is based on two modes, the native Kubernetes mode and the Mesos self-developed mode. It provides highly scalable, flexible and easy-to-use container management service for users.
- [BK-CMDB](https://github.com/Tencent/bk-cmdb): BlueKing Configuration Management DataBase (BlueKing CMDB) is an enterprise level configuration management platform for assets and applications.
- [BK-PaaS](https://github.com/Tencent/bk-PaaS): BlueKing PaaS is an open development platform that allows developers to create, develop, deploy and manage SaaS applications quickly and easily.
- [BK-SOPS](https://github.com/Tencent/bk-sops): BlueKing Standard OPS (SOPS) is a light-weighted SaaS product in the Tencent BlueKing product system designed for the orchestration and execution of tasks through a graphical interface.

## Contributing
- If you have good comments or suggestions, welcome to give us Issues or Pull Requests to contribute to the BlueKing open source community. For more information about BlueKing node management, branch management, Issue and PR specification. Please read the [Contributing Guide](docs/contributing.md).
- [Tencent Open Source Incentive Program](https://opensource.tencent.com/contribution) encourages developers to participate and contribute, and we look forward to your participation.

## License

Based on MIT, please refer to [LICENSE](LICENSE)
