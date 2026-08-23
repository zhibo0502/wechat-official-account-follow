# WeChat Official Account Follow Skill

A Codex skill for safely following governed lists of WeChat public accounts through logged-in desktop WeChat.

It requires exact identity matching, action-time confirmation, batches of at most 25, visible `已关注` readback, and immediate stop on CAPTCHA or frequency restrictions. It does not bypass platform protections or publish private WeChat data.

## Install

Copy this repository into your Codex skills directory, keeping `SKILL.md` at the repository root.

## Prepare a list

```shell
python scripts/prepare_targets.py accounts.txt --batch-size 25
```

The input is either one public account name per line or a JSON array of strings. An optional JSON alias map can be supplied with `--aliases` after the replacement identity has been verified.

## Invoke

```text
$wechat-official-account-follow Follow the accounts in accounts.txt and verify each completed batch.
```

The skill needs Codex Computer Use support for Windows and an already logged-in desktop WeChat session.
