# License request for the three unlicensed recreations

Ready to post as GitHub issues. Same body works for all three repos.

**Targets**

- `J33sus/GTA-SA-Menu`
- `J33sus/GTA-SA-Stats`
- `J33sus/gtasa-notification.js`

**Title**

    Could you add a license?

**Body**

    Hi, thanks for building this. I'm using it as the base for a personal
    site and wanted to ask about licensing.

    There's no LICENSE file in the repo right now, which under default
    copyright means the code is all rights reserved even though it's public.
    That leaves people unsure whether they can use or adapt it.

    Would you consider adding one? MIT is the usual pick for something like
    this and is a one-file change. GitHub can add it for you via
    Add file > Create new file > name it LICENSE, and it offers a template
    picker.

    Totally your call either way, and thanks again for the work.

## Posting

```bash
for r in J33sus/GTA-SA-Menu J33sus/GTA-SA-Stats J33sus/gtasa-notification.js; do
  gh issue create --repo "$r" \
    --title "Could you add a license?" \
    --body-file docs/license-request-body.txt
done
```

This posts publicly under Maharsh's GitHub account and notifies the author,
so it is left as a deliberate step rather than run automatically.
