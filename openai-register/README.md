# OpenAI 自动注册脚本

基于 GPTMail 临时邮箱 + OAuth 流程自动注册 OpenAI 账号。

## 环境要求
- Python 3.9+（建议虚拟环境）
- 依赖：`curl_cffi`

## 运行步骤
1. 激活虚拟环境：`source venv/bin/activate`（若已创建）
2. 安装依赖：`pip install curl_cffi`
3. 执行示例：
   ```bash
   GPTMAIL_API_KEY=你的key python openai_register.py --proxy http://127.0.0.1:7890
   ```
   如果不需要代理，去掉 `--proxy` 即可。
   参数说明：
   - `--proxy` 可选，填你的代理；不需要可省略。
   - `--once` 只跑一次，默认循环。
   - `--sleep-min/--sleep-max` 循环模式下两次任务的随机等待。

获取 GPTMail Key：可到 https://mail.chatgpt.org.uk 自行申请。

## 工作流程概览
- 调用 GPTMail 创建临时邮箱、轮询验证码
- 走 OpenAI OAuth 授权，提交验证码、创建账户、选择 workspace
- 最终保存 token 至 `token_xxx_timestamp.json`

## 配置点
- `GPTMAIL_API_KEY` 必填；可选 `GPTMAIL_BASE_URL`（默认 https://mail.chatgpt.org.uk）、`GPTMAIL_TIMEOUT`、`GPTMAIL_PREFIX`、`GPTMAIL_DOMAIN`
- 如需代理，命令行传 `--proxy`

## 输出
- 生成的 token JSON 会写到当前目录，如 `token_test_example_1700000000.json`

## 常见问题
- 邮箱收不到验证码：换代理或重试，mail.tm 偶尔延迟。
- 403/地区限制：代理需要非 CN/HK。
- 未获取到 workspace：重试，确保验证码正确。
