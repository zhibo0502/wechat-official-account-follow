# Verification and recovery

Read this reference only when the ordinary exact-name profile flow is insufficient.

## Evidence levels

Use the strongest available label without overstating it:

- `searched`: an exact account card was returned.
- `profile_verified`: the opened profile identity matched the target.
- `ui_followed`: the profile refreshed to `已关注`.
- `database_verified`: an approved read-only adapter resolved the requested public name to one `gh_...` identity after the UI action.

Database verification is optional. It must be bounded to requested public names, read-only, secret-free, and fail closed on missing or multiple identities. Never publish raw database material, keys, private contacts, chats, or unrelated account names.

## Alias evidence

Record an alias only when one of these paths is current and unambiguous:

1. Search groups the configured name under an account card whose actual name differs, and the profile operator or description matches the intended organization.
2. An official article for the configured name exposes a publisher link whose profile identifies the intended organization.
3. The user explicitly states the replacement account, and current profile or database readback confirms it is already followed.

Store `configured_name`, `actual_name`, evidence level, and a short public reason. Apply the mapping only to that target.

## Article-to-profile recovery

When no account card exists:

1. Open a clearly first-party article without clicking Follow.
2. Inspect the article publisher link, not promotional text in the body.
3. If the publisher is the intended account, open its profile and resume the normal profile verification flow.
4. If the article promotes another account but is published by a different account, stop. The publisher Follow button belongs to the publisher.

## Stop ledger

On a stop condition, retain:

- last fully verified target;
- current target and stage;
- exact visible reason;
- completed batch counts;
- whether the last action outcome is known.

Resume from the first unverified target after the user resolves login or CAPTCHA state. Re-observe the window and never reuse old coordinates or accessibility indexes.
