---
name: wechat-official-account-follow
description: Batch-follow governed WeChat official-account lists through logged-in desktop WeChat with exact identity matching, action-time confirmation, CAPTCHA stop conditions, and verifiable coverage. Use for subscribing to public accounts or service accounts; do not use for article scraping, unfollowing, private contacts, or CAPTCHA bypass.
---

# WeChat Official Account Follow

Turn a user-supplied public-account list into a verified subscription ledger.

## Workflow

1. Read the available Computer Use skill before controlling Windows. Use its supported Windows API only.
2. Normalize and deduplicate the target list. For large lists, run `scripts/prepare_targets.py`; default to batches of at most 25.
3. Inspect the logged-in desktop WeChat state without changing it. Count exact targets already followed when reliable readback is available.
4. Present the imminent batch scope and request action-time confirmation immediately before the first Follow action. One confirmation may cover a clearly enumerated batch or full list.
5. For each target:
   - Search its exact public name.
   - Accept an exact-name account card labeled 公众号, 服务号, or 订阅号.
   - Open the profile and confirm its displayed identity before clicking Follow.
   - Treat 已关注 as a successful no-op.
   - Click Follow only within the confirmed scope, then refresh until 已关注 is visible.
6. Stop the batch immediately on a CAPTCHA, robot check, frequency restriction, login failure, ambiguous identity, unexpected window, or unknown action outcome. Report the last proven account and do not retry the risky action blindly.
7. Verify each completed batch. UI readback proves the Follow state; an approved read-only local identity adapter may additionally prove that the public identity landed in the client database.
8. Report requested, newly followed, already followed, alias-mapped, unavailable, ambiguous, and verified counts separately.

## Identity rules

- Similar names are different accounts. Never choose by logo, popularity, or search rank alone.
- An alias is valid only when current evidence connects the configured name to the actual account. Open the profile and verify the operator or official description. Record both names.
- If search exposes only an official article, open it read-only and inspect the publisher link. Follow only when that publisher is the intended target; promotional text mentioning another account is not identity evidence.
- A video channel is not a substitute for a public account unless the user explicitly changes the target type.

Read [references/verification.md](references/verification.md) when aliases, article-to-profile recovery, database readback, or failure recovery is needed.

## Boundaries

- Keep private contacts, chats, cookies, tokens, database keys, local paths, and account identifiers out of logs and published artifacts.
- Use normal WeChat UI behavior. CAPTCHA solving, fingerprint spoofing, stealth browsers, and rate-limit evasion are outside this skill.
- Following changes the user's account subscription state. Authorization for research or list preparation does not authorize Follow actions.
- Do not change the source list or replace an unavailable target unless the user supplies the replacement or current first-party evidence proves a rename.

## Completion

Complete only when every target is classified and every claimed subscription has a visible 已关注 readback or stronger approved evidence. A partial run must name every unresolved target and its exact stopping reason.
