Risk-Aware Payment Delegation: From Intent to Executable Decisions

October 13, 2026 narrative revision. Main text: 8 pages; complete PDF: 23 pages;
199-word abstract; 46 cited references. The title, decision policy, experimental
results, numerical table sources, and all figure assets are unchanged.

Build: latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex
Offline reconstruction: python reproduce.py --pdf
Native availability witnesses: python ../scripts/availability_20261013/verify.py --native-witnesses

The manuscript now follows one argument: bounded authorization makes delegated
purchasing different from optimizing a shopping objective; SET makes the
purchase-or-refusal decision explicit; workflow gains do not certify every
generated permission; frozen availability tests expose the gap. The introduction
uses the official AP2 announcement only to motivate pre-authorized purchasing,
not as a claim about an AP2 vulnerability or payment-system deployment.

Section 4 connects current correctness directly to authorization-domain
soundness and availability exposure. The state-omission derivation is retained
in Appendix A.5, with its unchanged assumptions and formula. Equation numbers
are updated automatically. Figure 4 and the full reasoning/language panels are
in Appendix E; the availability study is the final main-text empirical result.
The 4/59 case explains behavior and cause in Section 5.4, with event terms,
monetary values, and original-expression checks in Appendix F.3.

Figure 3 keeps 800 planned trials per model, 2,400 pooled, and its original
removal-budget curves. Exposure covers 48 requests, 15 templates, and four
families while viable authorized alternatives remain; eight exposed outputs
begin with exact decisions. Complete distributions and controls remain in
Appendix F. Acquisition records are in ../docs/availability_20261013.md.
Historical studies remain separately archived in ../docs/diagnostic_archive/.

Table 7 remains one table with main-study settings and the retained inventory
of 12 requested models and 49 model-effort combinations, on page 16. The former
component Table 2 is absent from the PDF; no family-summary table replaces it.
The official ACL style, anonymity, and uppercase SET labels are preserved.

Figure layout: the panel captions in Figures 1 and 4 are centered below their
respective panels, with axis labels kept separate. Plot data are unchanged.
