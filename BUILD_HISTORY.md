# AI build history


1. I inspected the PDF and checked for the companion glossary. It was not present in the directory.
2. I checked the live source shapes before coding. Yahoo daily chart data, NSE announcements and Screener company tables all responded. The first 18-stock refresh exposed one inactive ticker (`TATAMOTORS.NS`, HTTP 404); I replaced it with `EICHERMOT` and reran the fetch.
3. I chose a narrow flow: the filing, the reason it matters, then a person who could add context. The app highlights material filings and collapses routine updates.
4. I kept contact data synthetic and made source links visible. I avoided model-generated claims about management guidance because I had not verified transcript passages.
5. I ran syntax checks, refreshed all sources, and ran a local HTTP smoke test covering the page and live company lookup.
6. I opened the original TCS October 2026 transcript PDF and added a short, page-linked note. The call explicitly said the company does not give numerical revenue or earnings guidance, so I did not invent a promised-versus-delivered score.
