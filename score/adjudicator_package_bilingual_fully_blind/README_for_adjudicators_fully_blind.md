# README For Adjudicators / 仲裁员说明

This is a fully blind adjudication package.

这是一个完全盲审仲裁包。

You will see only:

你只会看到：

- an anonymous adjudication item ID / 匿名仲裁编号；
- image path / 图像路径；
- prompt / 评估提示词；
- target anomaly / 目标异常；
- target anomaly description / 目标异常说明；
- blank response fields / 空白填写字段。

You will not see original sample IDs, condition labels, metadata gold labels, previous rater labels, majority labels, model outputs, or suggested answers.

你不会看到原始样本编号、条件标签、metadata gold、之前的人评标签、多数投票标签、模型输出或建议答案。

## Task / 任务

Judge whether the target anomaly is allowed by the prompt.

判断目标异常是否被当前 prompt 允许。

Do not judge image beauty or general model quality. Judge only the target anomaly.

不要评价图像美感或模型整体质量。只判断目标异常。

## Fill These Columns / 请填写这些列

- `final_anomaly_visible 最终异常是否可见`
- `final_permission 最终权限标签`
- `final_confidence_1_3 最终信心1-3`
- `final_issue_tag 最终问题标签`
- `final_rationale 最终理由`

Use the bilingual guide and response schema in this package.

请参考本包中的中英指南和填写规范。
