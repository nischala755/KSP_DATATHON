# Final submission checklist

## Team and deck

- [ ] Team name, leader, size and members filled on slide 1
- [ ] Problem-statement wording matches the official selected statement
- [ ] All `{TEAM INPUT}` markers removed
- [ ] No slide uses text smaller than 22 pt
- [ ] Official KSP, Zoho and H2S branding retained
- [ ] Real product screenshots replace screenshot instructions
- [ ] Every synthetic-data and benchmark qualifier remains visible
- [ ] PowerPoint and exported PDF both open correctly

## Links

- [x] Public GitHub repository: `https://github.com/nischala755/KSP_DATATHON`
- [ ] Three-minute demo video uploaded and publicly viewable
- [ ] Catalyst development URL tested in an incognito browser
- [ ] Catalyst production URL created from the console
- [ ] Final production URL placed on slide 13
- [ ] API `/health` and app homepage tested after production promotion
- [ ] QR codes generated and scanned from a phone

## Security

- [ ] Previously exposed Mistral and Sarvam keys revoked
- [ ] Fresh keys stored only as server-side Catalyst environment variables
- [ ] `.env` not committed
- [ ] Demo JWT and audit secrets replaced in Catalyst
- [ ] No tokens, terminal histories or personal accounts appear in screenshots/video

## Evidence

- [x] Backend tests pass
- [x] Frontend production build passes
- [x] Local 50-request benchmark recorded
- [ ] AppSail logs show healthy startup
- [ ] Live `/api/health` reports 500 seeded cases
- [ ] Live chat returns grounded citations
- [ ] Live audit chain verifies

