Subject: FINN build challenge submission

Hello ENAM team,

I built **FINN: the signal, then the person**, a phone-first investor desk. It watches an 18-stock mock portfolio, lifts the few meaningful NSE filings above routine disclosures, flags unusual end-of-day moves, and places a useful person from a fictional network beside the event. A company lens gives a concise numerical readout and opens the original annual report and earnings call transcript. A direct network search answers who could help with a company or theme.

**Try it:** https://krishanu230.github.io/finn-investor-desk/  
**Repository:** https://github.com/Krishanu230/finn-investor-desk  
**AI build history:** `BUILD_HISTORY.md`; I can provide the full coding-session export with the submission.

The core choice was to make every screen answer two questions: what changed, and who can make it clearer. I used a saved snapshot so the demo remains reliable, with a local Python endpoint for live research on any NSE ticker with available Screener data. The hosted showcase contains eight research examples; the local endpoint is needed for arbitrary tickers. Yahoo supplies daily bars, NSE supplies filings, and Screener supplies consolidated numerical tables and links to original reports and transcripts. There is no runtime LLM: deterministic rules made this version cheaper and easier to audit. A later version would use models only for passage extraction and multi-document reasoning, always with source spans.

All contact profiles and links are synthetic. A real deployment would use consented imports, separate each investor's data, encrypt it, enforce access at the API, allow deletion, and retain only the role history needed for matching. The static demo stores no real personal data. I would schedule refresh jobs, keep documents in private object storage, and cache normalized company data behind an authenticated service.

I left out transcript-guidance tracking and phone notifications. Both need more source checking and operational work than a thin prototype should pretend to have. The natural next step is to compare four quarters of explicit management guidance against reported numbers, with links to the exact transcript and filing passages.

Best regards
