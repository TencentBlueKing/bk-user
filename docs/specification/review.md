# Reviewing for Bk-User

我们坚信 code review 所带来的价值：不仅可以提高质量、代码的可读性，同时也能不断提高开发者的水平，
促进开发者的编码能力，做出更好的设计。

以下是蓝鲸团队 review issues 和 PRs/MRs 的相关指引。

- [欢迎PRs/MRs](#欢迎PRs/MRs)
- [代码审查人员](#代码审查人员)
- [审查细节](#审查细节)
  - [持有PR](#持有PR/MR)
- [合并](#合并)

## 欢迎PRs/MRs

最重要的一条：欢迎在任何时候，反馈问题、反馈需求

提交前相关规范请审阅 [commit-spec](./commit.md)

## 代码审查人员

Code review 会让特性与问题解决稍稍延后，同时也会造成额外审阅工作。因此蓝鲸团队希望积极参与项目相关人员也是
积极的审阅者，同时也期望相关的审阅者也具备相关领域的专业知识，以期提高处理效率。

## 审查细节

当 PR/MR 被提交之后，审查人员需要对该 PR/MR 进行快速分类，例如关闭重复，识别是否存在简单的用户错误，打上标签，
确认该 PR/MR 由哪些更具专业知识的审查人员进行审查。

如果 PR/MR 被拒绝了，审查人员需要向发起者提供足够的信息反馈，解释为什么会被关闭。

在评审的过程中，PR/MR 的发起者请积极回答审查人员的疑问，进行评论。如有需要，对提交内容进行合理的调整。

审查人员在工作日内对于 PR/MR 处理要及时。在非工作日内，大家必须意识到，相关的处理会有所延时。

### 持有PR/MR

所有的参与人员不可能永远在处理相关的需求，如果审查人员因为时间关系没能立刻处理，建议在PR/MR的讨论中反馈处理时间。
对于 PR/MR 的作者，合理的做法是和审查人员积极磋商合理的截止时间，或者是否有其他专业的审查人员可以处理，协商PR/MR
的交接。

## 合并

PR/MR 达成以下标准时会被合并:

* 审查人员没有提出反对或者整改意见
* 所有反对的建议或者调整的建议已经合理处理
* 至少有一个分支的维护者赞成合入 (LGTM)
* 具备相关的文档和测试
