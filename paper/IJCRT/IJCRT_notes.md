# IJCRT reformatting notes (BEED V2 and Pan-Cancer)

Prepared 21 Oct 2026. Target: International Journal of Creative Research Thoughts (IJCRT), ISSN 2320-2882, https://ijcrt.org. Nothing has been submitted or registered, and nobody has been contacted.

## 1. Template check
- The attached template is **byte-identical** to IJCRT's official "Paper_Format.docx" from https://ijcrt.org/download.php (sha256 b3fcd893…72f12, last modified on the server 12 Oct 2026). **There are no differences between them**, so the official template was used as the base file.
- **Conflict on the IJCRT site.** The download page and the "How to publish" page say *double-spaced, Times New Roman 12 pt, headings 12 pt bold*. The template itself, and the "Structure Details" box inside it, say *single line spacing, 0 pt before and after*, with 10 pt body text. **I followed the template.** If the editor asks for double spacing, it is a one-line change in the build script, so tell me.

## 2. Template specs applied
- A4. Margins as in the template file: left and right 0.51", top about 0.83", bottom 0.75". Header 0.25", footer 0.
- Single column, justified text, Times New Roman throughout. **Single spacing is kept, as the official template specifies**; the website's "double-spaced" line is not applied.
- The IJCRT header (logo, "© 20XX IJCRT | Volume X, Issue X…") and footer (paper ID, page number) are kept exactly as supplied. The template says these are "set by the journal", so the page numbering also keeps the template's start value of 25.
- **Title:** 24 pt, centred, 8 pt before and 16 pt after, in title case.
- **Author block:** the template's Author and Affiliation styles, with **empty placeholders**: [Author name(s)], [Designation], [Department], [Organisation, City, Country], [Email].
- **Docx metadata:** the author and last-modified-by fields are blank.
- **Abstract and keywords:** bold-italic "Abstract:" and "Index Terms -" run-in labels, 10 pt, with a horizontal rule above and below as in the template.
- **Headings:**
  - Main sections use the template's Heading 1, with automatic Roman numbering in small caps (I. INTRODUCTION … VII. LIMITATIONS AND FUTURE WORK).
  - Back-matter headings (Data Availability, Ethics, declarations, References) are unnumbered.
  - Subsections are bold run-in headings (2.1, 4.7 …) as in the template sample, so the in-text cross-references (§4.7, Section 3.3) still match.
- **Body text:** 10 pt, first-line indent 0.2", single spacing, 0 spacing.
- **Figures and tables:**
  - Figure captions are 10 pt, centred, below the figure.
  - Table titles are 10 pt, centred, above the table, in sentence case (not upper case).
  - Tables are 9 pt and centred. Header rows repeat on later pages, rows do not split, and short tables are kept on one page.
- **References:** changed to **IEEE style** ([n] A. B. Surname, "Title," *Venue*, vol., no., pp., year, doi), because IJCRT asks for IEEE numbered references. The numbering and order are unchanged.
- **Removed NIELIT items:** the double spacing, the "Track 2/5" lines, the corresponding-author and ORCID lines, and the names and affiliation.
  - In the Author Contributions statement, your name is now "[Author 1]".
- **Scientific content is unchanged.** A script checked that every body paragraph, every table cell and every image of the camera-ready papers and supplements is present in the new files.

## 3. Files (each paper has DOCX + matching PDF)
| File | Pages |
|---|---|
| BEED/BEED_IJCRT.docx / .pdf | 11 |
| BEED/BEED_IJCRT_supplementary.docx / .pdf | 32 |
| PanCancer/PanCancer_IJCRT.docx / .pdf | 10 |
| PanCancer/PanCancer_IJCRT_supplementary.docx / .pdf | 10 |

The supplements are kept as separate files. IJCRT asks for one Word manuscript and does not mention supplementary files, so ask the editor whether a separate supplement is accepted. If it is not, the supplement can be appended to the paper, which would add 10 or 32 pages.

## 4. IJCRT guideline findings (ijcrt.org, read 21 Oct 2026)
- **File type:** Word (.doc/.docx) only. *PDF is not accepted at submission*; the PDFs here are for checking. After acceptance, the formatted manuscript must be named with your Registration ID.
- **Page limit:** none stated.
- **Abstract:** at most 250 words, with 4–6 keywords.
  - **BEED:** 245 words and **6 keywords**. Compliant.
  - **Pan-Cancer:** trimmed from 296 to **247 words**, with **6 keywords**. Compliant (updated 21 Oct). Every number and claim is unchanged: a script confirmed the multiset of numbers is identical. Only the phrasing was tightened, and the framing sentence "We asked how much these practices matter here and what the accuracies can support" was dropped. The trimmed abstract appears only in the IJCRT file; the NIELIT camera-ready still has the 296-word version. Please read it once to approve the wording.
- **References:** IEEE numbered style, cited in order of appearance. This is done.
- **Other formatting rules:**
  - Number pages, sections, figures, tables and equations.
  - Define abbreviations at first use.
  - Submit a clean file with no tracked changes or comments.
  - Figures at 300 dpi or more, with axes labelled with units.
- **Similarity:** Turnitin or iThenticate screening, which must be **below 15%**. Self-plagiarism also counts.
  - Both papers draw on your own earlier NIELIT drafts and on public preprints that may be similar. If any version is already public (arXiv, ResearchGate), cite it.
- **Fees:** none at submission. After acceptance the fee is **₹1501 for up to 5 authors**, plus ₹500 for each extra author.
  - Optional extras: Crossref DOI ₹300, hard copy of the certificate ₹500, journal hard copy + certificate + DOI ₹1100, transparent peer-review report ₹700.
- **At submission you need:**
  - the main manuscript (Word);
  - high-resolution figures and tables;
  - the details of every author, with affiliations and ORCID iDs;
  - declarations covering conflicts of interest, ethics and AI use.
- **After acceptance, send in one email to editor@ijcrt.org** (Registration ID in the subject):
  - the hand-signed, scanned **Undertaking (copyright) form**: https://ijcrt.org/Doc/Undertaking%20by%20Authors%20form.pdf
  - the formatted .doc named with the Registration ID;
  - an identity proof of the corresponding author;
  - the payment proof.
- **Licence:** papers are published open access under CC BY 4.0.
- **Review:** IJCRT advertises a 1–2 day decision.
- **Current call:** Vol. 14, Issue 10 (October 2026); online submission is open until **31 Oct 2026**.

## 5. What you must do yourself
1. Fill in the authors, designations, department, organisation and email in the author block of both papers. The placeholders are now standardised: [Author 1] is you, and in BEED [Author 2] and [Author 3] replace the old [Co-author Name] and [Supervisor Name]. Fill them in or delete them.
2. Complete the **[To confirm]** placeholders:
   - Author Contributions ("[Author 1]");
   - Funding;
   - Conflict of interest;
   - the AI-use declaration;
   - Data/Code availability, including where the code zip is deposited and its licence.
3. Done: the abstract is trimmed and both keyword lists are cut to 6 (§6). Just check the new Pan-Cancer abstract wording.
4. Ask IJCRT whether the supplement can be a separate file, and whether there is a place for the code zip (the papers cite "Supplementary File S1").
5. Register on the portal, submit the .docx, and get a similarity report if you want one before review.
6. After acceptance: the undertaking form, ID proof, the fee, and the file renamed to the Registration ID.
7. Decide whether you want a DOI (₹300). It is **not** included by default.
8. Note that the old NIELIT cover letters and checklists do not apply to IJCRT.

## 6. Keyword sets (applied)
- **BEED (6):** electroencephalography, epileptic seizure classification, data leakage, dataset provenance, blocked cross-validation, shortcut learning
- **Pan-Cancer (6):** pan-cancer classification, RNA-Seq, data leakage, equivalence testing, conformal prediction, learning curves

## 7. Rebuilding
The build scripts are on the bot's box at /workspace/ijcrt/build/. `build_all.sh` converts the camera-ready papers into the IJCRT template, and `ieee.py` converts the references to IEEE style. If the source papers change, just ask for a rebuild.

## 8. Final round (21 Oct 2026, evening): Kristina's review fixes and Tanya's English edits
**This was the last run of `build_all.sh`.** From now on, edit the docx files directly. Re-running the build would overwrite any manual edits.

- **References:** now in full IEEE style.
  - Venue names are in *italics* and abbreviated in IEEE style (e.g. *Comput. Biol. Med.*, *J. Mach. Learn. Res.*).
  - Conference papers read "in *Proc. …*, year, pp. …", and the book (Vovk et al.) has an italic title.
  - Numbering, order and content are unchanged (36 and 46 entries, citations identical).
- **Figure files:** separate files are in `figures/Fig1.png`–`Fig3.png` in each paper folder.
  - These are the original image files, embedded at 300 dpi.
  - At printed size they are 472–793 dpi (BEED) and 338 dpi (Pan-Cancer).
- **Cover letters:** `BEED_IJCRT_cover_letter` and `PanCancer_IJCRT_cover_letter` (docx + pdf, 1 page each), with author, contact, date and signature placeholders.
  - They include a "not under consideration elsewhere" declaration. That statement must be true when you sign, so see the policy point below.
- **Template leftovers removed:**
  - the docx Company field ("www.ijrti.org") and the "IJRTI" title entry;
  - the sample paper ID "IJCRT1601009" in the footer.
  - Page numbering now starts at 1, not 25; the journal sets the final numbers.
- **Pan-Cancer abstract:**
  - "in few" is now "in a few", as both Kristina and Tanya asked.
  - "confirming, on real RNA-Seq data, earlier simulations" was reordered so that "real data" refers to this study.
  - "abstaining otherwise" is now "abstaining on the rest".
  - It is now **250 words**. BEED's abstract is 246 words.
- **English edits (Tanya):** applied in the build sources, with a per-item log in the report.
  - No number, claim, citation or piece of Bonn wording was changed (checked by script).
  - Items that would push the Pan-Cancer abstract over 250 words were left out.
  - Bold run-in labels ("Research questions.", "Contributions.", "Answers to the research questions.") were kept, as Tanya's alternative allows.

### Policy: originality (IJCRT requirement)
IJCRT requires that the paper is "not being considered for publication elsewhere".
- Do **not** have the same paper under review at NIELIT Bio-AI Conclave 2026 and IJCRT at the same time. Submit each paper to only one venue, and withdraw from one before submitting to the other.
- Cite any public preprint of the work, since similarity must stay below 15%.

### Structured abstract
IJCRT's pubguide asks for a structured abstract (background, methods, results, conclusion). Both abstracts already roughly follow that order: problem and data, protocol, results, and conclusion and scope. Explicit sub-headings were not added; ask the editor if they are required.
