# Symnoesis Research Log

This log is append-only by convention. Every research action, literature lookup, and evidence decision is recorded here.

---

## 2026-10-11 — Prior-Art and Foundational Literature Baseline Search

- **Question:** What prior benchmarks, frameworks, and foundational studies measure human-AI reliance, cognitive offloading, sycophancy, or psychosocial outcomes over time, and how does SYMN-01 relate to them?
- **Method:** Academic literature search and repository review of arXiv preprints, PubMed/Frontiers records, and seminal human factors journals across cognitive psychology, automation reliance, and AI safety.
- **Sources:**
  1. `[humanai-impact-bench]` HumanAI-Impact-Bench (2026). PyPI: `human-ai-impact-bench`. Accessed 2026-10-11. Status: verified.
  2. `[arx-amplification]` Cognitive Amplification vs Cognitive Delegation in Human–AI Systems: A Metric Framework (2026). arXiv:2603.18677. Accessed 2026-10-11. Status: verified.
  3. `[arx-offloading]` Offloading Score: Measuring AI Reliance Through Counterfactual Workflows (2026). arXiv:2605.29392. Accessed 2026-10-11. Status: verified.
  4. `[truth-decay]` TRUTH DECAY: Quantifying Multi-Turn Sycophancy in Language Models (2025). arXiv:2503.11656. Accessed 2026-10-11. Status: verified.
  5. `[mit-openai-rct]` MIT Media Lab & OpenAI (2025). How AI and Human Behaviors Shape Psychosocial Effects of Chatbot Use: A Longitudinal Randomized Controlled Study. arXiv:2503.17473. Accessed 2026-10-11. Status: verified.
  6. `[ophir-2025]` Ophir, Y. et al. (2025). Critical reflections on chatbot psychosocial randomized trials. Front. Med., doi:10.3389/fmed.2025.1612838. Accessed 2026-10-11. Status: verified.
  7. `[frontiers-offloading-2026]` Not all cognitive offloading is equal: distinguishing dependent and autonomous offloading to generative AI (2026). Front. Psychol., doi:10.3389/fpsyg.2026.1878629. Accessed 2026-10-11. Status: verified.
  8. `[bainbridge-1983]` Bainbridge, L. (1983). Ironies of automation. Automatica, 19(6), 775-779. doi:10.1016/0005-1098(83)90046-8. Accessed 2026-10-11. Status: verified.
  9. `[parasuraman-1997]` Parasuraman, R. & Riley, V. (1997). Humans and Automation: Use, Misuse, Disuse, Abuse. Human Factors, 39(2), 230-253. doi:10.1518/001872097778543886. Accessed 2026-10-11. Status: verified.
  10. `[parasuraman-2010]` Parasuraman, R. & Manzey, D. H. (2010). Complacency and Bias in Human Use of Automation: An Attentional Integration. Human Factors, 52(3), 381-410. doi:10.1177/0018720810376055. Accessed 2026-10-11. Status: verified.
  11. `[skitka-1999]` Skitka, L. J., Mosier, K. L., & Burdick, M. (1999). Does automation bias decision-making? Int. J. Human-Computer Studies, 51(5), 991-1006. doi:10.1006/ijhc.1999.0252. Accessed 2026-10-11. Status: verified.
  12. `[sparrow-2011]` Sparrow, B., Liu, J., & Wegner, D. M. (2011). Google Effects on Memory: Cognitive Consequences of Having Information at Our Fingertips. Science, 333(6043), 776-778. doi:10.1126/science.1207745. Accessed 2026-10-11. Status: verified.
  13. `[risko-2016]` Risko, E. F. & Gilbert, S. J. (2016). Cognitive Offloading. Trends in Cognitive Sciences, 20(9), 676-688. doi:10.1016/j.tics.2016.07.002. Accessed 2026-10-11. Status: verified.
  14. `[mitchell-2019]` Mitchell, M. et al. (2019). Model Cards for Model Reporting. In Proceedings of FAT* '19, 220-229. doi:10.1145/3287560.3287596. Accessed 2026-10-11. Status: verified.
  15. `[gebru-2021]` Gebru, T. et al. (2021). Datasheets for Datasets. Communications of the ACM, 64(12), 86-92. doi:10.1145/3458723. Accessed 2026-10-11. Status: verified.
- **Findings:**
  - Existing open benchmarks (e.g. HumanAI-Impact-Bench) examine conversational-AI effects across up to 13 dimensions using cross-sectional human ratings, but lack a unified dyadic state space, Gray-code adjacency representations, or formal Minimal Failure Covers.
  - Recent literature establishes the critical distinction between autonomous offloading (which preserves human capability) and dependent offloading (which induces cognitive atrophy and reliance).
  - Parasuraman and Skitka provide the theoretical bedrock for automation complacency and bias, informing the appropriate-reliance indices in SYM-COG.
- **Confidence:** High. All citations point to verified publications, DOIs, or published repositories.
- **Decision impact:** Direct mapping to `research/prior-art.md`, SYM-COG/SYM-AFF operationalizations, and `spec/SPEC.md` §2.
- **Open issues:** Formal empirical validation of threshold cutoffs requires Phase 3 human cohorts.
