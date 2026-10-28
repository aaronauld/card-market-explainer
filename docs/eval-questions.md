# Eval questions: labelled price moves

Each entry is a real price move with a known cause (or, for a few, a deliberately confirmed lack of one). Together they are the answer key for the eval harness:

- **Retrieval** is scored by recall@k: do the documents listed under **Event docs** appear in the top k results?
- **Answers** are scored by whether they contain the facts under **Answer must mention**.

Rule: at least 40% of entries must need two sources to explain fully. These test whether retrieval can find more than one relevant document.

Rule: every fact under **Answer must mention** has to be derivable from what the system is given (the weekly prices and the event documents). Facts that need outside knowledge, such as "it was a widely played staple" when no document says so, are not fair to score and were removed after the first answer run (2026-10-28).

Entries were found with `scripts/find_spikes.sql` (weekly median at least doubled, or 1.6x for some, and stayed there with enough sales), then checked in the daily prices and against sources. All prices are TCGplayer `good` condition, in US dollars.

**Status** values:
- `confirmed`: cause shown by a primary source (official page or Limitless decklists) and the timing fits the daily data.
- `likely`: good evidence, but part of it is inference (e.g. a deck plays the card, but the price is for a premium printing). The harness can score these separately.
- `no known cause`: the move is real but no tournament, release, rotation, ban, reprint or announcement explains it. The correct answer says so. These test whether the system makes up a cause.
- `false premise`: the question assumes a move that didn't happen (e.g. asks why a card spiked when it only drifted). The correct answer corrects the premise from the prices. These test whether the system goes along with a misleading question.

---

## Template

Keep every field on one line starting with `- **Field:**` so the harness can parse it. Indented lines under a field are extra notes for people and are ignored by the parser.

### Q-000: <card name> (<set>, <card number>)

- **Status:** confirmed / likely / no known cause
- **Checked by:** who checked the sources, and when
- **Question:** what the system is asked, in a user's words. Names the card, printing and month; does not give away the cause.
- **Card id:** `tcgdex-id`
- **Price series:** variant, condition
- **Date of move:** YYYY-MM-DD (first day of the sustained move)
- **Direction and size:** e.g. up ~3x over two weeks
- **Real cause:** one or two sentences
- **Answer must mention:** fact one; fact two (separated by semicolons)
- **How I know:** links that confirm the cause
- **Sources needed:** 1 or 2
- **Event docs:** `doc-id`, `doc-id` (file names in `data/events/` without `.md`; may not be written yet)

---

## Entries

### Q-001: Roaring Moon ex (Paradox Rift, 124)

- **Status:** confirmed
- **Checked by:** Aaron, 2026-10-25
- **Question:** Why did Roaring Moon ex from Paradox Rift jump in price in late August 2024?
- **Card id:** `sv04-124`
- **Price series:** holo, good
- **Date of move:** 2024-08-18
- **Direction and size:** up ~2x. ~$2-3 through 17 Aug; 19 sales on 18 Aug (final day, $3.50); $4.40-5.50 from 19 Aug. Weekly: $2.61 before, $5.24 after, 61 sales.
  Single-sale outliers on 13 Aug ($5.31) and 15 Aug ($11.92) are noise.
- **Real cause:** Seinosuke Shiokawa took a Roaring Moon ex deck to the Masters final of the 2024 World Championships in Honolulu (16-18 Aug 2024), losing 2-1 to Fernando Cifuentes (Iron Thorns ex). Motohiro Higuchi also finished 72nd with Roaring Moon ex.
  Shrouded Fable (released 2 Aug 2024) added cards to the deck, but the price did not move until the final.
- **Answer must mention:** 2024 World Championships (Aug 2024); a Roaring Moon ex deck finished runner-up
- **How I know:** [Limitless: Worlds 2024](https://limitlesstcg.com/tournaments/420), [Pokémon.com: Worlds 2024 TCG Masters](https://www.pokemon.com/us/play-pokemon/worlds/2024/tcg-masters). Secondary: [SNKRDUNK](https://snkrdunk.com/en/magazine/2024/08/19/pokemon-tcg-fernando-cifuentes-beats-seinosuke-shiokawa-to-win-the-2024-pokemon-tcg-world-championships).
- **Sources needed:** 1
- **Event docs:** `2024-08-18-worlds-2024-masters-results`

### Q-002: Avery (Chilling Reign, 187)

- **Status:** confirmed
- **Checked by:** Claude from decklists, spot-checked by Aaron, 2026-10-25
- **Question:** What made Avery from Chilling Reign (187) shoot up in price in November 2023?
- **Card id:** `swsh6-187`
- **Price series:** holo, good
- **Date of move:** 2023-11-15
- **Direction and size:** up ~3x. ~$5.50-7 through 11 Nov; $9.10 on 15 Nov; $10.47 on 17 Nov; $20.47 on 20 Nov; ~$16-22 to end of Nov. Weekly: 2.4x, 26 sales.
- **Real cause:** Gardevoir ex decks started playing Avery at the Latin America International Championships (São Paulo, 17-19 Nov 2023): most of the ~30 Gardevoir lists ran 1-3, including 3rd, 6th and 8th. None of the 20 Gardevoir lists at Regional Toronto (28 Oct 2023) played it.
  The price started rising two days before LAIC, possibly as lists spread during preparation.
- **Answer must mention:** Latin America International Championships (Nov 2023); Gardevoir ex decks started playing Avery
- **How I know:** [Limitless: LAIC 2023-24](https://limitlesstcg.com/tournaments/404), [Limitless: Regional Toronto 2023](https://limitlesstcg.com/tournaments/389)
- **Sources needed:** 1
- **Event docs:** `2023-11-19-laic-2023-results`

### Q-003: Regidrago VSTAR (Silver Tempest, 136)

- **Status:** confirmed
- **Checked by:** Claude from standings, spot-checked by Aaron, 2026-10-25
- **Question:** Why did Regidrago VSTAR (Silver Tempest) go up in mid-June 2024?
- **Card id:** `swsh12-136`
- **Price series:** holo, good
- **Date of move:** 2024-06-11
- **Direction and size:** up ~2-3x. ~$2-3 through 10 Jun; $4.03 on 11 Jun; $6.02 on 12 Jun; ~$9 on 18-20 Jun; ~$5-6 to end of June. Weekly: 2.2x, 80 sales.
- **Real cause:** A Regidrago deck finished 14th (Jacob Eye) at the North America International Championships (New Orleans, 7-9 Jun 2024), with another in 43rd (Ryan Miller); both lists played 3 Regidrago VSTAR. Andrew Hedrick won with Lost Zone Box.
  Twilight Masquerade (24 May 2024) added support cards for the deck, but the price did not move at that release.
- **Answer must mention:** North America International Championships (Jun 2024); a Regidrago deck placed 14th
- **How I know:** [Limitless: NAIC 2024](https://limitlesstcg.com/tournaments/406). Secondary: [TCGplayer price report, 16 Jul 2024](https://seller.tcgplayer.com/blog/articles/price-trends-pokémon-cards-climbing-in-price-71624).
- **Sources needed:** 1
- **Event docs:** `2024-06-09-naic-2024-results`

### Q-004: Dark Patch (Lost Origin, 216)

- **Status:** confirmed
- **Checked by:** Claude from decklists, spot-checked by Aaron, 2026-10-25
- **Question:** Why did Dark Patch from Lost Origin (216) spike in late October and early November 2023?
- **Card id:** `swsh11-216`
- **Price series:** holo, good
- **Date of move:** 2023-10-19
- **Direction and size:** up ~3-5x. ~$5 in early Oct; $7-9 from 19-24 Oct; $14 on 26 Oct; peak $25.76 on 3 Nov; ~$14-15 by late Nov. Weekly: 2.7x, 50 sales.
- **Real cause:** Paradox Rift (released 3 Nov 2023) introduced Roaring Moon ex, and Roaring Moon ex decks are built around Dark Patch: all 6 Roaring Moon ex lists at LAIC 2023 (17-19 Nov) played 4.
  The rise starts about two weeks before the English release, so card reveals or the Japanese release (around 27 Oct) likely started it. Not yet checked.
- **Answer must mention:** Paradox Rift release (3 Nov 2023) with Roaring Moon ex; Roaring Moon ex decks play 4 Dark Patch
- **How I know:** [Pokémon.com: Paradox Rift](https://www.pokemon.com/us/pokemon-tcg/scarlet-violet-paradox-rift), [Limitless: LAIC 2023-24](https://limitlesstcg.com/tournaments/404)
- **Sources needed:** 2
- **Event docs:** `2023-11-03-paradox-rift-release`, `2023-11-19-laic-2023-results`

### Q-005: Energy Switch (Silver Tempest, 212)

- **Status:** confirmed
- **Checked by:** Claude from decklists, spot-checked by Aaron, 2026-10-25
- **Question:** What caused Energy Switch from Silver Tempest (212) to rise in November 2023?
- **Card id:** `swsh12-212`
- **Price series:** holo, good
- **Date of move:** 2023-11-03
- **Direction and size:** up ~3x. ~$2.50 through 2 Nov; 23 sales on 3 Nov; $4.48 on 8 Nov; $8.64 on 15 Nov; ~$6-8 to end of Nov. Weekly: 2.2x, 32 sales.
- **Real cause:** Same as Q-004: Roaring Moon ex decks also use Energy Switch to move energy onto Roaring Moon ex. All 6 Roaring Moon ex lists at LAIC 2023 played 3-4. The rise starts on Paradox Rift's release day.
  Energy Switch from Roaring Skies (`xy6-109`) rose in the same weeks, but it is not Standard-legal, so it is left out.
- **Answer must mention:** Paradox Rift release (3 Nov 2023) with Roaring Moon ex; Roaring Moon ex decks play Energy Switch
- **How I know:** Same as Q-004.
- **Sources needed:** 2
- **Event docs:** `2023-11-03-paradox-rift-release`, `2023-11-19-laic-2023-results`

### Q-006: Regieleki VMAX (Silver Tempest, 198)

- **Status:** confirmed
- **Checked by:** Claude (research agent, decklists), 2026-10-25. TODO (Aaron): spot-check
- **Question:** Why did Regieleki VMAX from Silver Tempest (198) jump in early April 2023?
- **Card id:** `swsh12-198`
- **Price series:** holo, good
- **Date of move:** 2023-04-02
- **Direction and size:** up ~1.6-2.5x. ~$11.50-13 from 13-29 Mar; $28-33 on 2-3 Apr; steady $20-22 from 6-23 Apr. Thin daily sales (1-10). Weekly: 1.6x, 57 sales.
- **Real cause:** Scarlet & Violet (released 31 Mar 2023) brought Miraidon ex, the engine of the Miraidon/Regieleki deck. On 1 Apr 2023 Shin Inageta won Champions League Miyagi (2,488 players) with that deck, playing 3 Regieleki VMAX. No Miraidon deck was in the previous Champions League (Aichi, 25 Feb) top 16.
- **Answer must mention:** Miraidon ex released in Scarlet & Violet (31 Mar 2023); Miraidon/Regieleki won Champions League Miyagi (1 Apr 2023); Regieleki VMAX is a core card in that deck
- **How I know:** [Limitless: CL Miyagi 2023](https://limitlesstcg.com/tournaments/364) (1st, list has 3 Regieleki VMAX), [Limitless: CL Aichi 2023](https://limitlesstcg.com/tournaments/361). Release date: secondary ([Bulbapedia: Scarlet & Violet](https://bulbapedia.bulbagarden.net/wiki/Scarlet_%26_Violet_(TCG))).
- **Sources needed:** 2
- **Event docs:** `2023-03-31-scarlet-violet-release`, `2023-04-01-cl-miyagi-2023-results`

### Q-007: Exp. Share (Battle Styles, 180)

- **Status:** likely
- **Checked by:** Claude (research agent, decklists), 2026-10-25. TODO (Aaron): spot-check
- **Question:** What made Exp. Share from Battle Styles (180) double in April 2023?
- **Card id:** `swsh5-180`
- **Price series:** holo, good
- **Date of move:** 2023-04-03
- **Direction and size:** up ~2x. $5.00-5.50 in March; $8.42 on 3 Apr (12 sales); $10.70-12.70 through April. Most days 1-4 sales. Weekly: 2.1x, 25 sales.
- **Real cause:** Same trigger as Q-006: the Miraidon/Regieleki deck that won Champions League Miyagi (1 Apr 2023) ran 2 Exp. Share, and Miraidon ex arrived in English on 31 Mar 2023.
  Likely, not confirmed: few sales, and Scarlet & Violet also reprinted Exp. Share (SVI 174), yet this printing still rose.
- **Answer must mention:** Miraidon/Regieleki decks play Exp. Share; the deck won Champions League Miyagi (1 Apr 2023); Miraidon ex released 31 Mar 2023
- **How I know:** [Limitless: CL Miyagi 2023](https://limitlesstcg.com/tournaments/364) (winning list has 2 Exp. Share), [Limitless: EUIC 2023](https://limitlesstcg.com/tournaments/351) (two Miraidon lists played it)
- **Sources needed:** 2
- **Event docs:** `2023-03-31-scarlet-violet-release`, `2023-04-01-cl-miyagi-2023-results`

### Q-008: Worker (Silver Tempest, 195)

- **Status:** likely
- **Checked by:** Claude (research agent, decklists), 2026-10-25. TODO (Aaron): spot-check
- **Question:** Why did Worker from Silver Tempest (195) climb in late March 2023?
- **Card id:** `swsh12-195`
- **Price series:** holo, good
- **Date of move:** 2023-03-28
- **Direction and size:** up ~1.6-2x. $5.20-6.70 from 13-27 Mar; $7.83 on 28 Mar; $10.60 on 1 Apr; $12.34 on 2 Apr (11-20 sales a day); $10-13 through April. Weekly: 1.6x, 91 sales.
- **Real cause:** Worker is a 1-copy staple in Gardevoir ex decks, which had already done well in Japan (2nd and 7th at Champions League Aichi, 25 Feb 2023), and Gardevoir ex arrived in English with Scarlet & Violet on 31 Mar 2023.
  Likely, not confirmed: the rise starts 3 days before the English release (anticipation), and the price is for a premium printing.
- **Answer must mention:** Worker is played in Gardevoir ex decks; Gardevoir ex released in English 31 Mar 2023; the deck had already placed well in Japan
- **How I know:** [Limitless: CL Aichi 2023](https://limitlesstcg.com/tournaments/361) (2nd and 7th, Gardevoir, 1 Worker each), [Limitless: EUIC 2023](https://limitlesstcg.com/tournaments/351) (Tord Reklev 2nd, Gardevoir, 1 Worker)
- **Sources needed:** 2
- **Event docs:** `2023-03-31-scarlet-violet-release`, `2023-02-25-cl-aichi-2023-results`

### Q-009: Gardevoir (Chilling Reign, 61)

- **Status:** likely
- **Checked by:** Claude (research agent, decklists), 2026-10-25. TODO (Aaron): spot-check
- **Question:** Why did Gardevoir from Chilling Reign (61) briefly spike at the start of April 2023?
- **Card id:** `swsh6-61`
- **Price series:** holo, good
- **Date of move:** 2023-04-01
- **Direction and size:** up ~2.5x, briefly. $3.30-4.40 in March; $9.21, $9.75, $10.83 on 1-3 Apr (26, 32 and 15 sales); back to $4.40-5.20 from 5 Apr. The reverse holo did the same. Weekly: 1.7x, 205 sales.
- **Real cause:** This Gardevoir is the second attacker in Gardevoir ex decks (2-3 copies in the Japanese lists at Champions League Aichi, 25 Feb 2023), and the spike lands on the English release of Gardevoir ex in Scarlet & Violet (31 Mar 2023).
- **Answer must mention:** Gardevoir ex released 31 Mar 2023; Chilling Reign Gardevoir is played alongside Gardevoir ex; the price peaked around the release and eased in the following weeks
- **How I know:** [Limitless: CL Aichi 2023](https://limitlesstcg.com/tournaments/361), [Limitless: CL Miyagi 2023](https://limitlesstcg.com/tournaments/364), [Limitless: EUIC 2023](https://limitlesstcg.com/tournaments/351)
- **Sources needed:** 2
- **Event docs:** `2023-03-31-scarlet-violet-release`, `2023-02-25-cl-aichi-2023-results`

### Q-010: Scoop Up Net (Rebel Clash, 165)

- **Status:** confirmed
- **Checked by:** Claude (research agent + weekly data), 2026-10-25. TODO (Aaron): spot-check
- **Question:** Why did Scoop Up Net from Rebel Clash drop in price in March 2023?
- **Card id:** `swsh2-165`
- **Price series:** normal, good
- **Date of move:** 2023-03-13
- **Direction and size:** down ~2.5x. Weekly median ~$2.80-3.70 from mid-Feb to early March; $1.99 in the week of 13 Mar (250 sales); $1.42 by 27 Mar; ~$1.10-1.40 through April.
- **Real cause:** Scoop Up Net has the D regulation mark, so the 2023 Standard rotation (announced 12 Dec 2022) removed it from Standard. Rotation took effect on 30 Mar 2023 on Pokémon TCG Live and 14 Apr 2023 at in-person events. The price stepped down in mid-March, ahead of both dates, then kept sliding.
- **Answer must mention:** 2023 Standard rotation removed D regulation mark cards; rotation dates (TCG Live 30 Mar, in-person 14 Apr 2023)
- **How I know:** [Pokémon.com: 2023 rotation announcement](https://www.pokemon.com/us/pokemon-news/2023-pokemon-tcg-standard-format-rotation-and-pokemon-tool-errata), [Pokémon.com: rotation strategy article](https://www.pokemon.com/us/strategy/2023-pokemon-tcg-standard-format-rotation-strategy) (names Scoop Up Net as a big loss). Secondary: [PokeGuardian, 12 Dec 2022](https://www.pokeguardian.com/1117731_pokemon-tcg-standard-format-rotation-announced-for-april-14-2023-pokemon-tool-card-errata).
- **Sources needed:** 1
- **Event docs:** `2022-12-12-2023-standard-rotation-announced`

### Q-011: Aurora Energy (Sword & Shield, 186)

- **Status:** confirmed
- **Checked by:** Claude (research agent), 2026-10-25. TODO (Aaron): spot-check
- **Question:** What made Aurora Energy from Sword & Shield fall in March 2023?
- **Card id:** `swsh1-186`
- **Price series:** normal, good
- **Date of move:** 2023-03-13
- **Direction and size:** down ~2x then further. ~$2.00-2.15 from Dec to early March; $1.37 in the week of 13 Mar (129 sales); ~$1.10 in April; ~$0.30-0.40 by June.
- **Real cause:** D regulation mark card removed by the 2023 Standard rotation (see Q-010). The pokemon.com strategy article names it as a format-defining staple leaving Standard.
- **Answer must mention:** 2023 Standard rotation removed D regulation mark cards; rotation dates (30 Mar / 14 Apr 2023)
- **How I know:** Same pokemon.com pages as Q-010.
- **Sources needed:** 1
- **Event docs:** `2022-12-12-2023-standard-rotation-announced`

### Q-012: Capture Energy (Rebel Clash, 171)

- **Status:** confirmed
- **Checked by:** Claude (research agent), 2026-10-25. TODO (Aaron): spot-check
- **Question:** Why did Capture Energy from Rebel Clash lose most of its value in spring 2023?
- **Card id:** `swsh2-171`
- **Price series:** normal, good
- **Date of move:** 2023-03-13
- **Direction and size:** down ~4-6x over two months. ~$1.40-1.70 in Dec-Jan; ~$1.25 in Feb; $0.72 in the week of 13 Mar (268 sales); $0.38 by mid-April; ~$0.25 by late May.
- **Real cause:** D regulation mark card removed by the 2023 Standard rotation (see Q-010). The pokemon.com strategy article names it alongside Aurora Energy as a format-defining staple leaving Standard.
- **Answer must mention:** 2023 Standard rotation removed D regulation mark cards; rotation dates (30 Mar / 14 Apr 2023)
- **How I know:** Same pokemon.com pages as Q-010.
- **Sources needed:** 1
- **Event docs:** `2022-12-12-2023-standard-rotation-announced`

### Q-013: Twin Energy (Rebel Clash, 174)

- **Status:** likely
- **Checked by:** Claude (research agent), 2026-10-25. TODO (Aaron): confirm it was widely played (Limitless lists from early 2023)
- **Question:** Why did Twin Energy from Rebel Clash get cheaper in March 2023?
- **Card id:** `swsh2-174`
- **Price series:** normal, good
- **Date of move:** 2023-03-13
- **Direction and size:** down ~2x. ~$2.60-2.90 from Dec to early March; $1.35 in the week of 13 Mar (95 sales); ~$0.90-1.00 in April; ~$0.60 in June.
- **Real cause:** D regulation mark card removed by the 2023 Standard rotation (see Q-010). Not named in the strategy article; its D mark comes from TCGdex card data.
- **Answer must mention:** 2023 Standard rotation removed D regulation mark cards; rotation dates (30 Mar / 14 Apr 2023)
- **How I know:** [Pokémon.com: 2023 rotation announcement](https://www.pokemon.com/us/pokemon-news/2023-pokemon-tcg-standard-format-rotation-and-pokemon-tool-errata)
- **Sources needed:** 1
- **Event docs:** `2022-12-12-2023-standard-rotation-announced`

### Q-014: Training Court (Rebel Clash, 169)

- **Status:** likely
- **Checked by:** Claude (research agent), 2026-10-25. TODO (Aaron): confirm it was widely played
- **Question:** Why did Training Court from Rebel Clash lose value in spring 2023?
- **Card id:** `swsh2-169`
- **Price series:** normal, good
- **Date of move:** 2023-03-13
- **Direction and size:** down ~2-3x. ~$2.70-2.85 in Dec, drifting to ~$2.05-2.30 in late Feb; $1.15 in the week of 13 Mar (111 sales); ~$0.60-0.80 in April-May.
- **Real cause:** D regulation mark card removed by the 2023 Standard rotation (see Q-010). Part of the decline started in February.
- **Answer must mention:** 2023 Standard rotation removed D regulation mark cards; rotation dates (30 Mar / 14 Apr 2023)
- **How I know:** [Pokémon.com: 2023 rotation announcement](https://www.pokemon.com/us/pokemon-news/2023-pokemon-tcg-standard-format-rotation-and-pokemon-tool-errata)
- **Sources needed:** 1
- **Event docs:** `2022-12-12-2023-standard-rotation-announced`

### Q-015: Aerodactyl (Fossil, 16)

- **Status:** no known cause
- **Checked by:** Claude (research agent), 2026-10-25
- **Question:** Why did Aerodactyl from Fossil jump in mid-April 2023?
- **Card id:** `base3-16`
- **Price series:** normal, good
- **Date of move:** 2023-04-10
- **Direction and size:** up ~2x, briefly. Weekly median $2.45 before; $5.59 and $5.99 in the next two weeks (29 sales); back to $2.73 after. On 12 Apr (16 sales) and 17 Apr (15 sales) the daily average was ~$15.
- **Real cause:** None found. No tournament, reprint, ban or announcement explains it. The Japanese Pokémon Card 151 reveal (around 1 Apr 2023) did not lift vintage Gen 1 cards in general (an index of ~500 vintage cards did not move).
- **Answer must mention:** no event specifically explains it; the price fell back to its earlier level within weeks
- **How I know:** Searched tournaments, announcements and TCGplayer price reports; checked a vintage-card index in the data.
- **Sources needed:** 1
- **Event docs:** none. Retrieval should return nothing relevant; the harness checks the answer, not recall.

### Q-016: Inteleon VMAX (Fusion Strike, 79)

- **Status:** confirmed
- **Checked by:** Claude (decklist + weekly data), 2026-10-25. TODO (Aaron): spot-check
- **Question:** Why did Inteleon VMAX from Fusion Strike nearly triple in early July 2023?
- **Card id:** `swsh8-79`
- **Price series:** holo, good
- **Date of move:** 2023-07-03
- **Direction and size:** up ~3x. Weekly median $2.75-3.16 through June (63 sales in the week of 26 Jun); $8.29 in the week of 3 Jul; $9.42 in the week of 17 Jul. No data for 2-6 Jul, so the exact first day isn't visible.
- **Real cause:** Cyrus Davis won the Masters division of the North America International Championships (Columbus, 30 Jun - 2 Jul 2023) with Inteleon VMAX / Rapid Strike Urshifu VMAX, a rarely played deck. The winning list ran 3 Inteleon VMAX (Fusion Strike 79).
  Rapid Strike Urshifu VMAX, already widely played, did not move.
- **Answer must mention:** North America International Championships 2023 (Jul 2023); Cyrus Davis won with an Inteleon VMAX / Rapid Strike Urshifu deck
- **How I know:** [Limitless: NAIC 2023](https://limitlesstcg.com/tournaments/360) (1st, Inteleon Urshifu; list has 3 Inteleon VMAX FST 79). Secondary: [Wargamer](https://www.wargamer.com/pokemon-trading-card-game/north-american-international-championships-final).
- **Sources needed:** 1
- **Event docs:** `2023-07-02-naic-2023-results`

### Q-017: Inteleon V (Fusion Strike, 78)

- **Status:** confirmed
- **Checked by:** Claude (decklist + weekly data), 2026-10-25. TODO (Aaron): spot-check
- **Question:** What pushed up the price of Inteleon V from Fusion Strike in July 2023?
- **Card id:** `swsh8-78`
- **Price series:** holo, good
- **Date of move:** 2023-07-03
- **Direction and size:** up ~2-2.5x. Weekly median $1.76 in the week of 26 Jun (50 sales); $3.09 in the week of 3 Jul; $4.29 in the week of 17 Jul.
- **Real cause:** Same as Q-016: the NAIC 2023 winning list ran 3 Inteleon V alongside 3 Inteleon VMAX.
- **Answer must mention:** North America International Championships 2023 (Jul 2023); an Inteleon VMAX deck won the event
- **How I know:** Same as Q-016.
- **Sources needed:** 1
- **Event docs:** `2023-07-02-naic-2023-results`

### Q-018: Yveltal (Paradox Rift, 205)

- **Status:** no known cause
- **Checked by:** Claude (research agent), 2026-10-25
- **Question:** Why did the Yveltal illustration rare from Paradox Rift go up in mid-June 2024?
- **Card id:** `sv04-205`
- **Price series:** holo, good (also visible in nearmint, which has more sales)
- **Date of move:** 2024-06-17
- **Direction and size:** up ~1.7x. Near Mint: $8.00-9.10 on 1-8 Jun (5-38 sales a day); $14.10-15.90 on 17-20 Jun; ~$12-15 into July. The typical Paradox Rift card did not move in the same weeks.
- **Real cause:** None found. The card has no competitive play (no Limitless decklists), and no announcement, product or event explains it. Probably collector demand.
- **Answer must mention:** no tournament, reprint, ban or announcement explains it; no document mentions Yveltal or a deck using it
- **How I know:** Searched Limitless, announcements and news; compared with the rest of Paradox Rift in the data.
- **Sources needed:** 1
- **Event docs:** none. Retrieval should return nothing relevant; the harness checks the answer, not recall.

### Q-019: Dark Patch (Astral Radiance, 139)

- **Status:** confirmed
- **Checked by:** Claude (weekly data), 2026-10-25. TODO (Aaron): spot-check
- **Question:** Why did the regular Dark Patch from Astral Radiance get more expensive in late October 2023?
- **Card id:** `swsh10-139`
- **Price series:** normal, good
- **Date of move:** 2023-10-16
- **Direction and size:** up ~3-4x on high volume. Weekly median $0.26-0.53 from late Sep to mid Oct (75-263 sales a week); $0.81-0.92 in the weeks of 16-23 Oct; $1.07-1.16 through November (164-660 sales a week).
- **Real cause:** Same as Q-004: Roaring Moon ex (Paradox Rift, released 3 Nov 2023) decks play 4 Dark Patch. This is the common printing most players buy.
- **Answer must mention:** Paradox Rift release (3 Nov 2023) with Roaring Moon ex; Roaring Moon ex decks play 4 Dark Patch
- **How I know:** Same as Q-004.
- **Sources needed:** 2
- **Event docs:** `2023-11-03-paradox-rift-release`, `2023-11-19-laic-2023-results`

### Q-020: Dark Patch (Lost Origin, 216), August 2024

- **Status:** confirmed
- **Checked by:** Claude (decklists + daily data), 2026-10-29. TODO (Aaron): spot-check
- **Question:** Why did Dark Patch from Lost Origin (216) go up again in late August 2024?
- **Card id:** `swsh11-216`
- **Price series:** holo, good
- **Date of move:** 2024-08-18
- **Direction and size:** up ~1.4-1.5x. Weekly median ~$5.65-6.60 from mid-July to the week of 12 Aug; $7.85 in the week of 19 Aug (13 sales); $8.63 in the week of 26 Aug. Near Mint shows the same: ~$6-6.70 through 17 Aug, 27 sales on 18 Aug and 30 on 19 Aug, then $8.50-9.
- **Real cause:** A Roaring Moon ex deck finished runner-up at the 2024 World Championships (16-18 Aug 2024). Both Roaring Moon ex lists there (Seinosuke Shiokawa 2nd, Motohiro Higuchi 72nd) played 4 Dark Patch.
  This needs two documents: the Worlds 2024 document names Roaring Moon ex as runner-up but never mentions Dark Patch, and the LAIC 2023 document says Roaring Moon ex decks play 4 Dark Patch. Same trigger as Q-001.
- **Answer must mention:** 2024 World Championships (Aug 2024); a Roaring Moon ex deck finished runner-up; Roaring Moon ex decks play Dark Patch
- **How I know:** [Limitless: Worlds 2024](https://limitlesstcg.com/tournaments/420) (both Roaring Moon lists have 4 Dark Patch), [Limitless: LAIC 2023-24](https://limitlesstcg.com/tournaments/404).
- **Sources needed:** 2
- **Event docs:** `2024-08-18-worlds-2024-masters-results`, `2023-11-19-laic-2023-results`

### Q-021: Earthen Vessel (Paradox Rift, 163)

- **Status:** false premise
- **Checked by:** Claude (decklists + weekly data), 2026-10-29
- **Question:** Why did Earthen Vessel from Paradox Rift spike after the 2024 World Championships?
- **Card id:** `sv04-163`
- **Price series:** normal, good
- **Date of move:** 2024-08-18
- **Direction and size:** no spike. Weekly median $4.06-4.25 through July, $4.54-4.60 in early August, $4.90 in the week of 19 Aug, $4.81-5.23 into September (about 100-160 sales a week): a gradual drift of about 20% over two months, with no jump after Worlds.
- **Real cause:** None needed: the premise is wrong. Both Roaring Moon ex lists at Worlds 2024 played 4 Earthen Vessel, so a spike would look plausible, but the price didn't react the way Roaring Moon ex (Q-001) and Dark Patch (Q-020) did. Earthen Vessel is played in many decks, which may be why one result didn't move it.
- **Answer must mention:** the price did not spike after Worlds 2024; it rose gradually, from about $4.10 in July to about $4.90 in late August
- **How I know:** Weekly prices from the data; [Limitless: Worlds 2024](https://limitlesstcg.com/tournaments/420) for the decklists.
- **Sources needed:** 1
- **Event docs:** none. The answer comes from the prices; a cited Worlds document is fine only if the answer doesn't claim it caused a spike.

---

## Candidates (not yet confirmed)

Real moves without a confirmed cause yet. Move one up to **Entries** (with the next Q number) once it is confirmed.

- **Regidrago VSTAR** (`swsh12-136`), Jul-Aug 2024: weekly median ~$6.70 in early July, $11.90-14.95 from 29 Jul to 19 Aug, then down to ~$7 by mid-September. Regidrago took 4th, 5th, 7th and 8th at Worlds 2024 ([Limitless](https://limitlesstcg.com/tournaments/420)), but the climb started three weeks before Worlds. TODO: find what drove late July (other events, Japanese results), or phrase the question around the fall after Worlds.
- **Origin Forme Dialga VSTAR** (`swsh10-114`), Apr 2023: ~$3.50 to $11.68 by 14 Apr. Not in EUIC 2023 lists. TODO: check Japanese results and Scarlet & Violet-era decks.
- **Inteleon VMAX** (`swsh8-79`), Apr 2023: ~$3 to ~$9-10 (a separate move from Q-016 in July). Only two EUIC 2023 lists. TODO: same as Dialga.
- **Hisuian Electrode V** (`swsh11-172`), Nov 2023: ~$2-2.40 to ~$7.70-8.10 by 17-20 Nov. Every early list with it is a Klawf deck (Klawf, Paradox Rift 105, released 3 Nov 2023), but the price rose from 8 Nov, before the first recorded list (LAIC, 17 Nov). TODO: find earlier results or a dated deck write-up.
- **Raikou** (`swsh4-50`), Dec 2022: ~$3.30-4 to ~$8.40-11.20 from 24 Dec. A 1-copy card in Lugia VSTAR decks, which won Regional Arlington (17-18 Dec 2022), but its share of Lugia lists didn't change and Lugia itself didn't move. No clear cause.
- **Dragonite V** (`swshp-SWSH154`), Apr 2023: ~$6-7 to ~$11-12.60 from 11 Apr. A 1-copy Lost Zone Box card already played before the rise. No cause found.
- **Battle VIP Pass** (`swsh8-225`), Apr 2023: rose with Gardevoir ex decks (4 copies), but was already a staple in Lost Zone Box and Mew. Too ambiguous.
- **Raichu** (`base3-14`), May 2023: possible extra `no known cause` entry, but only 13 sales.

## Checked and left out

Weekly spikes that turned out to be noise in the daily data, so they are not used:
- Mid-2024 drops in Crown Zenith Trainers (Rare Candy, Energy Switch, Trekking Shoes, Switch, Rescue Carrier, Energy Retrieval), 151 Trainers (Leftovers, Giovanni's Charisma), Professor's Research (Scarlet & Violet) and Klara: single-sale outliers in `good`; Near Mint was flat.
- Shining Fates holos (Cramorant V, Dhelmise V) and Volcanion in spring 2023: low-sales spikes that reverted.
- Most vintage spikes (Jungle Snorlax, Gym Heroes, Gym Challenge, Fossil and Team Rocket cards): 2x weeks are routine for these cards (5-7 a year).
