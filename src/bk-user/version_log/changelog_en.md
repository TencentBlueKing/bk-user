<!-- 2024-06-20 -->
## V3.0.1
### New Features
- **[Login Security]** Added "Prohibit multiple sessions for the same user" feature to enhance session security.
- **[Personal Center]** Added support for binding WeCom/WeChat Official Account in the Personal Center.

### Optimizations
- **[User Selector]** Comprehensively optimized the new organization structure user selector component, improving the user search and selection experience.
- **[Data Source Sync]** Optimized data source synchronization capabilities. HTTP data source now supports APIGateway authentication, and also supports incremental synchronization, improving user experience during data source sync.
- **[Security Protection]** Optimized login security logic for built-in administrator temporary links and password validity periods, reducing the risk of security brute-force attacks through built-in administrator credentials.
- **[Security Protection]** Added "User Sensitive Fields" protection scheme, providing desensitization or permission control for specified fields.
- **[Organization Structure]** Supports adding sub-organizations directly under the tenant node, unifying the multi-tenant and single-tenant operation experience.
- **[Timezone Standards]** Introduced a brand new timezone selection component and enhanced the validation logic for geographic timezones.

### Bug Fixes
- **[Data Source Sync]** Fixed the issue where required fields were not properly validated in the batch user import function.
- **[Organization Structure]** Fixed the issue where department organization path calculation or display was incorrect for users within tenants in specific scenarios.
- **[Notification & Sync]** Fixed the issue where email sender validation was missing or incorrect when local identity source sends notifications.
- **[Organization Structure]** Fixed the issue where organization name displayed abnormally after modifying it on the page.
- **[Global]** Fixed several testing issues in 3.x multi-tenant mode.

---

<!-- 2024-04-24 -->
## V3.0.0
### New Features
- **[Multi-Tenant Architecture]** Brand new support for SaaS-based multi-tenant management, enabling logical isolation of data and configuration between different tenants within the platform.
- **[Cross-Tenant Collaboration]** Added cross-tenant collaboration policy configuration capability to adapt to complex organizational structures of group enterprises.
- **[Organization & Accounts]** Introduced a brand new organizational structure system, supporting flexible department tree management and drag-and-drop adjustments. Added an independent "Virtual Account" module for managing service accounts or temporary personnel of non-real-name/non-employee types.
- **[Data Source & Configuration]** Enhanced data source configuration capabilities, supporting flexible access and synchronization of multiple external identity providers (IDP). Added custom configuration functionality for user attribute fields. Redesigned the permission model for platform administrators and tenant administrators.
- **[Login & Authentication]** Added unified login source management function, allowing administrators to flexibly configure independent login methods (such as local password, WeCom QR code, OA single sign-on) for different user data sources, achieving a unified authentication entry for heterogeneous account systems.
- **[Security Audit]** Added platform operation history function, completely recording all key operations (such as adding/deleting users, modifying permissions, configuration changes) by administrators and users in the user management platform, providing data support for security audits and event tracing.
- **[Message Notification]** Added message notification configuration function, supporting configuration and automatic sending of reminders to users via email, SMS and other channels for scenarios such as account activation and password expiration, improving account security and user experience.
- **[Open API]** Launched the brand new Open API v3, restructured the interface design specifications, and improved integration capabilities with other platforms in the BlueKing ecosystem.
- **[Internationalization]** Full site supports Chinese-English language switching.
