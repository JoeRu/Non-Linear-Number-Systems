# Roadmap: Asymptotik von R_c(N)  
## Kapazitätsbeschränkte Fibonacci-Partitionen

**Status:** Forschungsinitiative  
**Aktuelle Version:** 2026-08-15  
**Zielgruppe:** Originale mathematische Publikation

---

## Kontextverankerung

Dieses Projekt untersucht die Asymptotik von $R_c(N)$ — der Anzahl der Darstellungen einer Zahl $N$ als
$$\sum_{k \ge 1} d_k F_k = N$$
mit Ziffernschranken $0 \le d_k \le F_k$ für alle Positionen $k$.

Das Problem sitzt exakt zwischen zwei klassischen, gelösten Fällen:

1. **Binäre Partitionen** (Mahler 1940, de Bruijn 1948):  
   Partitionen in Zweierpotenzen mit unbeschränkter Multiplizität. Asymptotik bekannt, inklusive oszillierende Korrektionen periodisch in $\log_2 N$.

2. **Fibonacci-Partitionen ohne Cap** (Coons–Kristensen–Laursen 2023, arXiv:2312.07404):  
   Partitionen in Fibonacci-Zahlen, nicht-distinkt, mit unbeschränkter Multiplizität. Zum ersten Mal wurde hier die volle Asymptotik
   $$\log p_F(n) \sim \frac{(\log n)^2}{2\log\varphi}$$
   mit Oszillationen und Fehleranalyse rigoros etabliert. Die Methode verbindet Harday–Ramanujan-Ideen, Mahler–de Bruijn-Techniken und analytische Fortsetzung der Fibonacci-Dirichletreihe $\zeta_F(z)=\sum_{k\ge1}F_k^{-z}$ (nach Navas).

**Die neue Herausforderung:** Die positionsabhängige Schranke $d_k \le F_k$ bricht beide Vereinfachungen. Sie ist weder so uniform wie bei Zweierpotenzen noch so simpel wie bei unbeschränkter Multiplizität. Dies macht das Problem zu einem idealen Testfall für verallgemeinerte asymptotische Methoden in der additiven Kombinatorik.

---

## Fortschritt

Stand: 2026-08-20. Jede erledigte Teilaufgabe mit dem Commit, der sie abdeckt.
Offene Punkte sind bewusst *nicht* abgehakt — auch dann nicht, wenn Infrastruktur
dafür schon existiert.

### Infrastruktur (querschnittlich, keine Roadmap-Phase)

- [x] Benchmark-Gerüst entfernt, Repo auf das Forschungsprogramm umgebaut — `6095170`
- [x] `capfib`-Paket: Platzwerte, Brute-Force-Orakel, zwei unabhängige schnelle Pfade — `425b503`, `0140c82`, `674058b`, `054f968`
- [x] Log-Raum-Auswertung der erzeugenden Funktion, Legendre-Transformation, Regression — `3aeffa6`, `78ccc80`, `de735dc`
- [x] Provenienz-Manifest für alle generierten Daten (Upsert statt Append) — `a688b99`, `9f3436d`
- [x] Claim-Ledger `theory/claims.yaml` + Validator `scripts/check_claims.py` — `625ce82`, `1b4dca0`, `9f3436d`
- [x] Projekt-Skills `rc-numerics`, `claim-ledger` — `0d377c1`, `7e83f82`
- [x] Lean-Entwicklung kompiliert erstmals (elan, Mathlib v4.14.0, `lake-manifest.json` versioniert) — `543c8b0`
- [x] Lean auf das *richtige* Objekt umgestellt: positionsabhängige Schranke statt konstanter Kapazität — `53f8030`

### Phase 0 — Präzisierung ✅

- [x] Fibonacci-Konvention festgelegt: $F_1=F_2=1$, $F_3=2$, $F_4=3$, $F_5=5$ — `425b503`, `860dd5b`
- [x] $R_c$, $R_u$, $b$ präzise definiert; $R_c$ über **alle** Stellen $F_k \le N$ — `625ce82`
- [x] Forschungsfragen (A), (B), (C) formuliert — `625ce82`
- [x] Deliverable `theory/00-definitions.md` — `625ce82`
- [x] Bekannt / Konjektur / offen im Ledger getrennt — `625ce82`

### Phase 0.5 — Konstanten-Gate ✅

- [x] `scripts/run_phase0_gate.py`, `data/phase0_5_gate.csv`, `figures/phase0_5_gate.png` — `1d218a6`
- [x] Messung: lokale Steigung **0.518710** bei $N = 10^{3200}$ gegen $1/(4\log\varphi) = 0.519522$ {claim:gate-local-slope} — `1d218a6`
- [x] Ergebnis korrekt als *obere* Schranke formuliert; $1/(8\log\varphi)$ nur unter Sattelpunkt-Straffheit ausgeschlossen — `1b4dca0`, `3c97822`
- [x] Deliverable `docs/phases/phase0_5_gate.md` — `1d218a6`, `1b4dca0`, `3c97822`
- [x] Roadmap an die revidierte Phasenfolge angepasst — `860dd5b`

### Phase 1 — Exakte Berechnung ✅

**Ergebnis:** [`docs/phase1.md`](phase1.md) — Zusammenfassung; Details in
[`docs/phases/phase1_report.md`](phases/phase1_report.md).

Erledigt:

- [x] DP-Rekurrenz (naive Ziffernschleife) — `674058b`
- [x] Unabhängige Zweitimplementierung über die geschlossene Produktform — `054f968`
- [x] Brute-Force-Orakel (bewusst langsam, dient als Spezifikation) — `0140c82`
- [x] **Korrektheits-Gate:** DP gegen Orakel für alle $N \le 200$, beide schnellen Pfade gegeneinander für alle $N \le 500$ — `054f968`
- [x] Tabelle aus `theory/01-background.md` §4 exakt reproduziert für $n = 1..10$ — `674058b`
- [x] Vollständigkeit numerisch bestätigt (keine Lücken in der Zählung) — `674058b`
- [x] Lauf bis $N = 10^6$ (exakt, nicht Log-Domain — der zurückgestellte Pfad wird nicht gebraucht) — `9ce15e9`
- [x] `phase1_data.csv` — `9ce15e9`
- [x] `phase1_plot.png` → geliefert als `phase1_growth.png` und `phase1_fluctuation.png` — `9ce15e9`
- [x] `phase1_report.md` — `8601426`
- [x] Deskriptive Statistik: Monotonie, lokale Fluktuation — `9ce15e9`
- [x] Extremale $N$ (offenes Problem 2) — `9ce15e9`
- [x] **Fluktuations-Befund:** `R_c(N)` ist stark fluktuierend (49.6% fallende
      Schritte, aus `data/phase1_summary.json`) {claim:rc-not-monotone}, damit
      ist die in Phase 0 offengelassene Frage entschieden: der Befund
      **schränkt Route B ein** (ist eine Randbedingung an sie, keine Auswahl
      gegen Route A) — er macht es ratsam, einen Tauber-Angriff über die
      summatorische Funktion `S_c(N)` zu führen statt direkt über `R_c(N)`;
      Route A bleibt die primäre Route für den strengen Asymptotik-Beweis
      (siehe Phase 5) — `8601426`

### Phase 2 — Elementare Schranken 🟡 Aussagen formuliert, Beweise offen

- [x] $\sum_{k \le n} F_k^2 = F_n F_{n+1}$ **in Lean bewiesen** (nicht in Mathlib vorhanden) — `53f8030`
- [x] $R_c(N) \le R_u(N)$ als Lean-Aussage formuliert (`countReps_le_uncapped`, mit Beweisskizze) — `53f8030`
- [x] Vollständigkeit als Lean-Aussage formuliert (`exists_numeral_of_le`, mit Beweisskizze) — `53f8030`
- [x] Zusatz: „1 > 1“ formal bewiesen — zwei verschiedene Numerale mit gleichem Wert (`exists_two_numerals_same_value`) — `53f8030`
- [ ] Obere Schranke aus Coons–Kristensen–Laursen zitierfähig ausformuliert
- [ ] Untere Schranke: konstruktiver Beweis (Kern der Phase)
- [ ] `phase2_bounds.md` mit beiden Sätzen und Fehlertermen
- [ ] Zusammenführung: welcher Wert von $C'$ ergibt sich?

### Phase 3 — Sattelpunkt-Heuristik ⬜ offen

- [ ] Drei-Regime-Zerlegung sauber ausgearbeitet
- [ ] Legendre-Transformation zur Konstante hergeleitet
- [ ] `phase3_heuristic.md` mit expliziter Heuristik-Warnung
- [ ] Sekundärterm-Entwicklung ($C_1$, $C_2$)

Hinweis: Die Konstante ist durch Phase 0.5 bereits *gemessen*. Phase 3 muss sie
nun *erklären*, nicht vorhersagen.

### Phase 4 — Numerische Konfrontation ⬜ offen

- [x] Direkte Produktauswertung $\log F_c(e^{-s})$ (Werkzeug vorhanden, gegen die exakte Reihe auf $10^{-16}$ verifiziert) — `3aeffa6`
- [x] Vier-Term-Regression als Werkzeug vorhanden — `de735dc`
- [ ] Fit an Phase-1-Daten (benötigt Phase 1)
- [ ] Oszillationsdetektion: Residuen gegen $\{\log_\varphi N\}$, Fourieranalyse
- [ ] `capfib/oscillation.py` (bewusst noch nicht angelegt — kein Testmaterial ohne Phase 1)
- [ ] `phase4_numerical_report.md`

### Phase 5 — Rigorisierung ⬜ offen

- [ ] Route A: Mellin-Transformation und $\zeta_F^{(F+1)}$
- [ ] Route B: Taubersätze für $S_c(N)$
- [ ] Route C: Funktionalgleichung (explorativ)
- [ ] **Sattelpunkt-Straffheit** beweisen — erst dann schließt die Phase-0.5-Messung auch $1/(8\log\varphi)$ aus (siehe `theory/claims.yaml`, `saddle-tightness`)

### Phase 6 — Oszillationen ⬜ offen

- [ ] Pol-Spektrum aus Phase 5
- [ ] Fourierkoeffizienten von $\Psi(\log_\varphi N)$
- [ ] Explizite Fehlerschranken
- [ ] `phase6_oscillations.md`

### Phase 7 — Verallgemeinerung und Writeup ⬜ offen

- [x] `paper/main.tex` und `paper/refs.bib` angelegt, damit Zitate ab Tag 1 in BibTeX auflaufen — `6095170`
- [ ] Verallgemeinerung auf $d_k \le c F_k^\alpha$
- [ ] Allgemeine lineare Rekurrenzen (Pisot-Basis)
- [ ] Paper
- [ ] arXiv-Preprint

---

## Phase 0 — Präzisierung

**Zeithorizont:** 1–2 Tage  
**Kritikalität:** ESSENTIELL — alle späteren Phasen ruhen darauf

### Ziele

- Alle Notationskonventionen fixieren  
- Die zentralen Forschungsfragen in präzise mathematische Aussagen umwandeln  
- Abgrenzung: Welche Fragen sind gestellt, welche sind offen?

### Substanz

1. **Fibonacci-Konvention:**  
   Festlegen: $F_1, F_2, F_3, \ldots$ mit expliziten Werten.  
   **Festgelegt:** $F_1=1, F_2=1, F_3=2, F_4=3, F_5=5, \ldots$ — siehe `theory/00-definitions.md`.
   Die doppelte 1-Stelle ist beabsichtigt: sie ist der Ursprung des "1 > 1"-Phänomens
   (Numerale `1000` und `0100` haben beide den Wert 1), und nur unter dieser Konvention
   gilt $\sum_{k\le n} F_k^2 = F_n F_{n+1}$, das die Vollständigkeitsschranke fixiert.
   **Konsequenz:** $d_1, d_2 \in \{0,1\}$.

2. **Definitionen schärfen:**  
   - $R_c(N):=$ Anzahl der Folgen $(d_k)_{k\ge1}$ mit $0\le d_k\le F_k$ und $\sum_k d_k F_k=N$.  
   - $R_u(N):=$ wie oben, aber $d_k$ unbeschränkt.  
   - $b(N):=$ binäre Partitionsfunktion (Partitionen in Zweierpotenzen, unbeschränkt).

3. **Asymptotics-Zieldefinition:**  
   Welche der folgenden drei Fragen sind für diese Roadmap zentral?
   - **(A) Existenz der führenden Asymptotik:**  
     Existiert $C_c$ so, dass $\log R_c(N) \sim C_c (\log N)^2$?
   - **(B) Verfeinerte Entwicklung:**  
     $\log R_c(N) = C_c(\log N)^2 + c_1 \log N \log\log N + c_2 \log N + (\text{Oszillation}) + o(1)$?
   - **(C) Oszillationsstruktur:**  
     Falls Oszillationen existieren: periodisch in $\log_\varphi N$? Welche Periode(n)?

   **Fokus dieser Roadmap:** Primär (A) und (B); (C) nachgelagert in Phase 6.

4. **Fluktuations-Vorüberlegung:**  
   Die klassische Partitionsfunktion $p(n)$ ist monoton wachsend.  
   $R_c(N)$ könnte lokal stark fluktuieren (analog zur distinkten Fibonacci-Partitionsfunktion A000119).  
   Entscheidung: 
   - Falls $R_c(N)$ sehr fluktuiert → verwende summatorische Funktion $S_c(N):=\sum_{n\le N}R_c(n)$ für Taubersätze (Phase 5B).
   - Falls $R_c(N)$ glatt ist → direkter Attack auf $R_c(N)$ selbst.  
   Diese Klärung wird in Phase 1 durch Daten entschieden.

### Deliverable

**Dokument:** `00-Definitionen.md` (1 Seite)  
Enthält:
- Fibonacci-Konvention mit expliziten Werten bis $F_{10}$  
- Präzise Definition von $R_c, R_u, b$ je in 2–3 Zeilen  
- Zentrale Forschungsfragen (A), (B), (C) in mathform  
- Zeichen: Welche Asymptotiken sind *bekannt* (mit Referenz), welche sind *Konjekturen*, welche sind *offen*?

---

## Phase 0.5 — Konstanten-Gate

**Zeithorizont:** 1 Tag
**Kritikalität:** HOCH — Entscheidungspunkt vor jeder monatelangen Investition

### Ziel

Die führende Konstante $C_c$ *messen*, bevor die Heuristik sie *herleitet*.

### Substanz

Direkte Auswertung von $\log F_c(e^{-s})$ im Log-Raum plus numerische
Legendre-Transformation $\log R_c(N) \le \min_s [sN + \log F_c(e^{-s})]$.
Schätzer ist die lokale Steigung $d(\log R)/d((\log N)^2)$, die weit schneller
konvergiert als das Verhältnis $\log R/(\log N)^2$.

Kandidaten: $1/(2\log\varphi)=1.039$, $1/(4\log\varphi)=0.520$, $1/(8\log\varphi)=0.260$.

### Deliverables

`scripts/run_phase0_gate.py`, `data/phase0_5_gate.csv`, `figures/phase0_5_gate.png`,
`docs/phases/phase0_5_gate.md`.

### Konsequenz

Phase 3 erklärt danach eine *gemessene* Zahl statt eine unbekannte vorherzusagen.

---

## Phase 1 — Exakte Berechnung und Sanity Checks

> **✅ Abgeschlossen.** Ergebnis: [`docs/phase1.md`](phase1.md). Exakte Werte für
> alle `N ≤ 10^6`, abgesichert durch einen punktweisen Abgleich zwischen zwei
> unabhängigen Algorithmen über den gesamten Bereich. Zentraler Befund:
> `R_c(N)` fluktuiert stark (49,6 % der Schritte fallen), was `S_c(N)` als
> Zielobjekt eines Tauber-Arguments nahelegt. Der folgende Abschnitt ist die
> ursprüngliche Planung und wird als solche beibehalten.

**Zeithorizont:** 1–2 Wochen  
**Kritikalität:** HOCH — Benchmark für alle theoretischen Ansprüche

### Ziele

- Zuverlässige numerische Daten für $R_c(N)$ bis zu praktischem Limit (ca. $N \le 10^6$–$10^7$)  
- Verifikation der erzeugenden Funktion gegen Brute-Force  
- Erste deskriptive Statistik: Monotonie, lokale Fluktuation, Symmetrien

### Substanz

1. **Algorithmus: Dynamische Programmierung**  
   ```
   Rekurrenz: P_0(x) = 1
              P_k(x) = P_{k-1}(x) · G_k(x),
   wobei G_k(x) = 1 + x^{F_k} + x^{2F_k} + ... + x^{F_k^2}
                = (x^{F_k(F_k+1)} - 1) / (x^{F_k} - 1)  [geschlossene Form]
   
   Koeffizient [x^N]P_k(x) = R_c^{(k)}(N)  [mit nur 1..k verfügbar]
   ```
   
   **Umsetzung:**  
   - Für exakte Koeffizienten: Array-Faltung mit ganzzahligen Potenzen (Speicher ~GiB für $N_{\max}\sim 10^7$).  
   - Für $\log R_c(N)$ (ausreichend für Asymptotik): Logistic-Faltung via Floating-Point, dann Umrechnung. Oder Bigint mit periodischem Logarithmieren.  
   - **Checksum:** Code gegen kleine Fälle $(N \le 200)$ via Brute-Force verifizieren (explizites Aufzählen aller $(d_k)$-Folgen).

2. **Erzeugungsfunktion-Test**  
   Produktform: $\prod_{k=1}^{K} \frac{1-x^{F_k(F_k+1)}}{1-x^{F_k}}$ für trunkiertes Produkt.  
   Abgleich gegen DP-Rekurrenz bis $N=500$: Sollten identisch sein.

3. **Deskriptive Statistik**  
   - Tabelle: $N$, $R_c(N)$, $\log R_c(N)$, $(\log N)^2$, $\frac{\log R_c(N)}{(\log N)^2}$ für $N\in\{100,500,1000,5000,10000,\ldots\}$.
   - Monotonie: Ist $R_c(N)$ wachsend? Oder gibt es Einbrüche (z.B. bei $N=F_m-1$)?  
   - Lokale Fluktuation: Ratio $R_c(N+1)/R_c(N)$; gibt es Spitzen oder systematische Muster?
   - **Vollständigkeit (erledigt):** Es gibt *keine* Lücken. Die Kempner–Fraenkel-Bedingung
     $F_k \le 1 + F_{k-1}F_k$ ist mit großem Spielraum erfüllt, also ist jedes $N \in [0, \sum_k F_k^2]$
     darstellbar (`theory/01-background.md` §3, numerisch bestätigt in `tests/test_dp.py`)
     {claim:completeness-no-gaps}.
     Aufgabe ist daher der *Beweis* der Vollständigkeit (Phase 2, Lean-Ziel), nicht die Suche nach Lücken.

### Deliverables

1. **Code:** `phase1_DP.py` (oder Sprache der Wahl)  
   - Eingabe: $N_{\max}$  
   - Ausgabe: Array $[R_c(1), R_c(2), \ldots, R_c(N_{\max})]$ oder $[\log R_c(1), \ldots]$  
   - Eingebaute Checks gegen $N=\text{small}$ via Brute-Force

2. **Daten:** `phase1_data.csv`  
   Spalten: `N, R_c(N), log(R_c(N)), (log N)^2, ratio_to_quad, log(R_c(N))/(log N)^2`  
   Mindestens für $N \in \{10^i \cdot 10^j : i=2,\ldots,7; j=0,\ldots,9\}$.

3. **Grafik:** `phase1_plot.png`  
   - Oben: $\log R_c(N)$ vs. $(\log N)^2$ (sollten proportional aussehen)  
   - Unten: Residuen nach Abzug des $(\log N)^2$-Terms (oszillatorische Struktur visualisieren)  
   - Kennzeichnung verdächtiger Stellen (lokale Minima etc.)

4. **Report:** `phase1_report.md` (2–3 Seiten)  
   - Zusammenfassung der Dataquality  
   - Beobachtete Muster mit Hypothesen  
   - Offene numerische Rätsel  

### Risiken

- **Speicher/Rechenzeit:** $10^7$ Koeffizienten brauchen effiziente Arithmetik. Falls zu langsam: auf $10^6$ reduzieren, oder nur $\log R_c$ approximieren.  
- **Numerische Stabilität bei $\log$:** Vorsicht mit underflow; BigInt-Logarithmieren via Mantisse+Exponent.

---

## Phase 2 — Elementare Schranken: Das Sandwich

**Zeithorizont:** 2–3 Wochen  
**Kritikalität:** MITTEL — Erstes bewiesenes Theorem, gibt Orientierung

### Ziele

- Obere und untere Schranken $c_1(\log N)^2 \le \log R_c(N) \le c_2(\log N)^2$ rigorös beweisen  
- Die Konstanten $c_1, c_2$ mit Referenzen angeben  
- Damit die *Größenordnung* schlüssig etablieren, ohne volle Asymptotik zu behaupten

### Substanz

1. **Obere Schranke:**  
   Trivial: $R_c(N) \le R_u(N)$ (Caps schwächen nur ein).  
   Aus Coons–Kristensen–Laursen (arXiv:2312.07404):
   $$\log R_u(N) \sim \frac{(\log N)^2}{2\log\varphi}, \quad \log\varphi = \frac{\log(1+\sqrt{5})}{2} \approx 0.481.$$
   
   Daher: **Theorem (Obere Schranke):**  
   $$\log R_c(N) \le (1+o(1)) \cdot \frac{(\log N)^2}{2\log\varphi}.$$
   
   Dies ist sofort zitierbar und benötigt keinen Beweis.

2. **Untere Schranke — konstruktive Methode:**  
   Partitioniere die Positionen $k$ in zwei Klassen:
   - **Bindet-Klasse $\mathcal{B}$:** $F_k \le N^{1/4}$ (hier kann der Cap die Verfügbarkeit ernsthaft einschränken).  
   - **Nichts-Klasse $\mathcal{N}$:** $F_k > N^{1/4}$ (hier ist jede Position einzeln viel zu groß, Cap ist irrelevant).  
   
   In Klasse $\mathcal{N}$ können wir höchstens eine Position verwenden, und zwar eine mit $F_k \le N < F_{k+1}$.  
   Jede Darstellung von $N$ muss also ein Präfix aus $\mathcal{B}$ und einen einzelnen Summand aus $\mathcal{N}$ (oder aus $\mathcal{B}$ selbst) haben.
   
   Untere Schranke aus expliziter Injektion:  
   Für beliebiges $M \in \mathcal{B}$ zähle alle $(d_k)_{k\in\mathcal{B}}$ mit $\sum_{k\in\mathcal{B}}d_k F_k = N - M$.  
   Dies gibt mindestens $R_u(N-M)$ Möglichkeiten, und wir können $M$ modulo $|\mathcal{B}|$ variieren, um Injektivität zu sichern.  
   
   Feinere Analyse: Nutze spezielle Struktur von $\mathcal{N}$ (geometrisches Wachstum der Fibonacci), um zu zeigen:
   $$\log R_c(N) \ge \frac{(\log N)^2}{4\log\varphi}(1-o(1)) + O(\log N).$$
   
   **Detaillierter Beweis erforderlich**, aber konzeptionell machbar mit Standard-Bijektionen.

3. **Konvergenz der Schranken:**  
   Falls obere und untere Schranke auf denselben Hauptterm hindeuten, hast du:
   $$C_c = \frac{(\log N)^2}{C'\log\varphi} \quad \text{für explizites } C' \in [2,4].$$
   Falls $C'=2$: Cap hat keinen Effekt auf die Führungsordnung (überraschend!).  
   Falls $C'=4$: Cap halbiert die Konstante (vermutete Heuristik aus Phase 3).  
   Falls $C'\in(2,4)$: Subtilere Effekt-Messung erforderlich.

### Deliverables

1. **Satz: Sandwich-Bounds**  
   Präzise Formulierung, Beweis von Ober- und Untergrenzen, mit Fehlerterme.

2. **Technical Note:** `phase2_bounds.md` (4–5 Seiten)  
   - Theorem + Beweis Obere Schranke (trivial, aber explizit).  
   - Theorem + Beweis Untere Schranke (Kern der Phase).  
   - Visualisierung: Numerische Daten aus Phase 1 gegen beide Grenzen plotten.  
   - Konklusion: Welchen Wert von $C'$ deuten die Daten an?

### Risiken

- Der Untergrenzen-Beweis könnte technisch knifflig werden (genaue Regimeeinteilung, Überlappungen).  
- Fallstricke beim Übersprechen von endlichen Produkten (bis zu welcher Position summieren?) zu Grenzwerten.

---

## Phase 3 — Die Sattelpunkt-Heuristik (Herzstück)

**Zeithorizont:** 3–4 Wochen  
**Kritikalität:** SEHR HOCH — Liefert die Konjektur und Intuition für Phase 5

### Ziele

- Die vermutete Konstante $C_c$ aus einer **expliziten, sauberen Heuristik** ableiten  
- Das Phänomen der "Drei Regime" offenlegen und erklären, warum der Cap die Asymptotik *halbiert*  
- Alles als **Konjektur und Heuristik klar markieren** (nicht als Theorem)

### Substanz

Die Kernidee: Analysiere die Produktseite der erzeugenden Funktion
$$F_c(x) := \prod_{k\ge1}\frac{1-x^{F_k(F_k+1)}}{1-x^{F_k}}$$
durch die Transformation $x=e^{-s}$, $s\to0^+$. Dann
$$\log F_c(e^{-s}) = \sum_{k\ge1}\left[\log(1-e^{-sF_k(F_k+1)})-\log(1-e^{-sF_k})\right].$$

1. **Drei-Regime-Zerlegung:**  
   
   Für jeden Summanden, parametriert durch $z=sF_k$:
   - Wenn $z\gg 1$: $\log(1-e^{-z})\approx -e^{-z}\approx 0$ (exponentiell kleine Beiträge).  
   - Wenn $z\approx 1$: kritischer Bereich (Übergänge).  
   - Wenn $z\ll 1$: $\log(1-e^{-z})\approx \log z$ (linear in $\log z$).  
   
   Da $F_k\approx \varphi^k/\sqrt{5}$ geometrisch wächst, gibt es für festes $s$ eine *eindeutige* Schwelle $k^*(s)$ mit $F_{k^*} \approx 1/s$.  
   
   Dies induziert drei Regime:

   | Regime | Bedingung | $k$ liegt in | Beitrag pro Term |
   |---|---|---|---|
   | **A (Cap bindet)** | $s F_k \gg F_k(F_k+1) \cdot s$ (unmöglich, Widerspruch — Revision notwendig) | — | — |
   
   **Korrekte Regimeeinteilung** (nach Überdenken):  
   
   Nutze den Fakt, dass jeder Term $k$ den Beitrag
   $$a_k(s):=\log\left(\frac{1-e^{-sF_k(F_k+1)}}{1-e^{-sF_k}}\right)$$
   liefert. Für $F_k \gg 1/s$: Zähler und Nenner sind beide $\approx 1$, also $a_k\approx 0$.  
   Für $F_k \ll 1/s$: 
   $$a_k \approx \log\left(\frac{sF_k(F_k+1)}{sF_k}\right) = \log(F_k+1)\approx\log F_k.$$
   
   Die **Drei Regime** sind genauer:

   | Regime | Bedingung auf $k$ | Beitrag zu Summe | Anzahl Positionen |
   |---|---|---|---|
   | **A** | $F_k \ll (sF_k)^{-1/2}$, d.h. $F_k^2 s\ll 1$ | $\approx \log F_k$ pro Term | $\approx \frac{1}{2}\frac{\log(1/s)}{\log\varphi}$ |
   | **B** | $(sF_k)^{-1/2} \ll F_k \ll s^{-1}$ | $\log F_k$-artig (linear in Summe) | $\approx \frac{1}{2}\frac{\log(1/s)}{\log\varphi}$ |
   | **C** | $F_k \gg s^{-1}$ | exponentiell klein | $\lesssim \text{const}$ |
   
   *(Diese Einteilung bedarf sorgfältiger Ausarbeitung; erste Skizze hier.)*

2. **Asymptotische Auswertung der Summe:**  
   
   Regime A + B gemeinsam liefern:
   $$\sum_{k \in A \cup B} \log F_k \approx \int_{k_{\min}}^{k_{\max}} \log(\varphi^k/\sqrt{5})\,dk$$
   wobei Grenzen durch $F_k^2 s \sim 1$ und $F_k s\sim 1$ gegeben sind.
   
   Dies ergibt:
   $$\int \log(\varphi^k)\,dk = \sum k \log\varphi = O((\log(1/s))^2 / \log\varphi).$$
   
   (Die genaue Konstante hängt von Regime-Grenzen ab; Legendre-Trafo unten liefert Hauptbeitrag.)

3. **Legendre-Transformation zum asymptotischen Verhalten von $R_c(N)$:**  
   
   Die Beziehung $N \leftrightarrow s$ über Sattelpunkt:
   $$\frac{d}{ds}\log F_c(e^{-s}) \Big|_{s=s^*} = N.$$
   
   Dies ist ein implicit-function-Theorem-Argument: Finde $s^*(N)$ so, dass die Ableitung der log-Erzeugungsfkt. gleich $N$ ist.
   
   Im binären Fall (de Bruijn) bekannt: $\frac{d}{ds}\log b(e^{-s})\approx \frac{\log(1/s)}{s}$, was auf $s^* \sim \frac{1}{\log N}$ und somit auf $\log b(N) \sim \frac{(\log N)^2}{2\log 2}$ führt.
   
   Im Fibonacci-Cap-Fall sollte die Struktur ähnlich sein, aber **eine weitere Halbierung tritt auf** wegen der Symmetrie der Cap-Regel: nur *Hälfte* der Positionen trägt zum Hauptterm bei (die, deren Cap *bindet*). Dies führt zur Konjektur:
   $$\log R_c(N) \sim \frac{(\log N)^2}{4\log\varphi}.$$

4. **Graphische Visualisierung:**  
   - Plot von $\log F_c(e^{-s})$ für $s$ von $0.1$ bis $0.001$.  
   - Überlagert: die Vorhersage $\frac{(\log(1/s))^2}{4\log\varphi}$ (sollte als Kurve sichtbar sein).  
   - Residuum: Abweichung vom asymptotischen Ansatz (offenbart Übergangszonen, Sekundärtermstrukturen).

### Deliverables

1. **Heuristik-Kapitel:** `phase3_heuristic.md` (8–10 Seiten)  
   - Sorgfältige Erklärung des Sattelpunkt-Ansatzes.  
   - Drei-Regime-Zerlegung mit Skizzen und Begründung.  
   - Legendre-Transformation zur Konstante.  
   - Grafiken (s.o.).  
   - **Riesengroße Warnung:** "Das Folgende ist eine Heuristik. Rigorose Beweise folgen in Phase 5."

2. **Konjektur-Statement:**  
   $$\boxed{\ \log R_c(N) \sim \frac{(\log N)^2}{4\log\varphi} \quad \text{(KONJEKTUR)}\ }$$
   Mit explizitem Numerant: $\frac{1}{4\log\varphi} = \frac{1}{4 \cdot 0.481\ldots} \approx 0.520$.

   > **Numerische Stütze (Phase 0.5):** Die lokale Steigung der Legendre-Transformierten misst
   > 0.518710 bei $N = 10^{3200}$ und steigt monoton gegen $1/(4\log\varphi) = 0.519522$
   > {claim:gate-local-slope}.
   > Da es sich um eine *obere* Schranke handelt, schließt dies $1/(2\log\varphi)$ unmittelbar aus;
   > der Ausschluss von $1/(8\log\varphi)$ setzt zusätzlich voraus, dass die Sattelpunkt-Korrektur
   > von niedrigerer Ordnung ist — erwartet, aber in Phase 0.5 nicht bewiesen.
   > Siehe `docs/phases/phase0_5_gate.md`. Das bleibt eine Konjektur — Phase 5 hat sie noch zu beweisen.

3. **Sekundär-Entwicklung (optional, aber wertvoll):**  
   Falls die Heuristik auch Logarithmische Terme anderer Ordnung andeutet, z.B.
   $$\log R_c(N) = \frac{(\log N)^2}{4\log\varphi} + C_1 \frac{\log N \log\log N}{\log\varphi} + C_2 \frac{\log N}{\log\varphi} + \text{Oszillation} + o(1),$$
   dann die Konstanten $C_1, C_2$ aus der Heuristik herauspräparieren.

### Risiken

- Die Übergangszonen zwischen Regimen sind mathematisch heiklig — kleine Fehler in der Asymptotics-Analyse können zu falschen Konstanten führen.  
- Die Legendre-Trafo setzt partielle Analytizität des Sattelpunkts voraus; dies muss plausibel gemacht werden (oder ist es der Punkt, an dem Phase 5A Rigorisierung braucht?).

---

## Phase 4 — Numerische Konfrontation (parallel zu Phase 3)

**Zeithorizont:** 2–3 Wochen  
**Kritikalität:** HOCH — Quantitatives Feedback auf die Konjektur

### Ziele

- Die Konjektur $\log R_c(N)\sim\frac{(\log N)^2}{4\log\varphi}$ numerisch gegen Phase-1-Daten testen  
- Oszillationen erkennen und quantifizieren  
- Größenordnung und evtl. Sekundärtermstruktur klären

### Substanz

1. **Direkte Produktauswertung (schnellster Test):**  
   
   Berechne $\log F_c(e^{-s})$ direkt aus dem Produkt für kleine $s$ (z.B. $s=0.01, 0.003, 0.001$):
   $$\log F_c(e^{-s}) = \sum_{k=1}^{K} \log\left(\frac{1-e^{-sF_k(F_k+1)}}{1-e^{-sF_k}}\right),$$
   wobei $K$ so groß gewählt wird, dass weitere Terme exponentiell klein sind.
   
   Vergleiche gegen $\frac{(\log(1/s))^2}{4\log\varphi}$:
   
   | $s$ | $\log F_c(e^{-s})$ (numerisch) | $\frac{(\log(1/s))^2}{4\log\varphi}$ | Ratio |
   |---|---|---|---|
   | $0.01$ | ? | $\approx 1.35$ | ? |
   | $0.001$ | ? | $\approx 5.40$ | ? |
   | $0.0001$ | ? | $\approx 12.1$ | ? |
   
   Falls Ratio gegen 1 konvergiert: ✓ Konjektur konsistent.  
   Falls nicht: Konjektur needs revision oder zusätzliche Terme (Sekundärterme dominieren noch).

2. **Fitting an Phase-1-Daten:**  
   
   Die Konvergenz in $(log N)^2$-Regressionen ist infamously langsam (Fehler wie $O(1/\log N)$). Stattdessen parametrischer Fit:
   $$\log R_c(N) = a(\log N)^2 + b\log N \log\log N + c\log N + d + o(1).$$
   
   Nutze Multiple-Regression mit Daten aus Phase 1 (mindestens 20–30 Datenpunkte) und extrahiere $a, b, c, d$ sowie Fehlerbalken.
   
   Erwartet: $a \approx \frac{1}{4\log\varphi} \approx 0.520$.  
   Test der Konjektur: Ist $a$ konsistent mit $0.520$ innerhalb der Unsicherheit?

3. **Oszillationsdetektion:**  
   
   Berechne Residuen:
   $$R(N) := \log R_c(N) - a(\log N)^2 - b\log N\log\log N - c\log N - d.$$
   
   Plotte $R(N)$ gegen $\{\log_\varphi N\}$ (Nachkommateil von $\log_\varphi N$), also die "*Fraktionale Phase*".
   
   Falls es periodische Muster gibt: Fourieranalyse der Periode(n). Erwartet aus der Theorie: Hauptperiode 1 (da Pole der Dirichletreihen bei $z=\frac{2\pi i k}{\log\varphi}$ liegen).

4. **Verlässlichkeitsprüfung:**  
   
   Teile die Daten in zwei Hälften: Fit mit Hälfte A, teste Koeffiziente gegen Hälfte B. Abweichung sollte klein sein.

### Deliverables

1. **Numerik-Skript:** `phase4_numerical.py`  
   - Funktion `evaluate_product_FC(s, K_max)`: Berechnet $\log F_c(e^{-s})$ direkt.  
   - Funktion `fit_logRC(data_file)`: Multiple Regression an Phase-1-Daten.  
   - Visualisierungen: Plots (Produkt vs. Hypothese; Residuen vs. Phase; etc.).

2. **Numerik-Report:** `phase4_numerical_report.md` (5–7 Seiten)  
   - Tabellen mit den Produktauswertungen.  
   - Fitting-Ergebnisse mit Konfidenzintervalle.  
   - Oszillations-Plots.  
   - **Fazit:** Wie gut stimmt die Konjektur? Welche Korrektionen sind sichtbar?

3. **Updated Konjektur-Statement (falls notwendig):**  
   Falls die numerischen Daten systematische Abweichungen zeigen (z.B. Sekundärtermkoeffizienten), diese in die Konjektur einarbeiten.

### Risiken

- **Langsame Konvergenz:** Mit $N$ nur bis $10^7$ könnten Sekundärtermeffekte noch dominieren; echte $(log N)^2$-Asymptotik zeigt sich erst bei $10^{10}$ o.ä.  
- **Numerische Genauigkeit:** Floating-Point bei Summationen über $\sim 30$ Fibonacci-Terme kann Rundungsfehler aufbauen. Mit Double-Precision arbeiten und später Check mit Extended-Precision.

---

## Phase 5 — Rigorisierung: Drei Angriffsrouten

**Zeithorizont:** Monate (3–6, je nach Route)  
**Kritikalität:** KRITISCH — Unterschied zwischen Konjektur und Theorem

Diese Phase teilt sich in drei mögliche, teilweise parallele Routes:

### Route A — Mellin-Transformation und Dirichletreihen (Favorit)

**Zeithorizont:** 4–6 Monate  
**Analoge zu:** Coons–Kristensen–Laursen, Navas auf $\zeta_F$.

**Strategie:**

1. **Setup der Mellin-Transformation:**  
   Schreibe
   $$\log F_c(e^{-s}) = \int_1^\infty \left(\log F_c(e^{-x/t})\right) \frac{dx}{x} \quad (\text{partielle Integration/Mellin-Pair}).$$
   
   Dies transformiert das Produkt in eine Summe über Pole und Residuen einer meromorphen Funktion.

2. **Dirichlereihen-Ansatz:**  
   Definiere
   $$\zeta_F^{(C)}(z) := \sum_{k\ge1} F_k^{-z}, \quad \zeta_F^{(F+1)}(z):=\sum_{k\ge1} (F_k(F_k+1))^{-z}.$$
   
   Dann ist
   $$\prod_k (1-x^{F_k}) = x^{\zeta_F^{(C)}(0)} \cdot (\text{Regge-Struktur in } z)$$
   und ähnlich für den Zähler. Die Quotientenerzeugungsfunktion wird zu einer Differenz oder Ratio dieser Dirichletreihen.
   
   **Kritisches Neuland:** $\zeta_F^{(F+1)}(z)$ ist neu in der Literatur (nicht reduzibel auf frühere Arbeiten). Die analytische Fortsetzung dieser Reihe ist das Kernproblem.
   
   **Erwartetes Resultat:** $\zeta_F^{(F+1)}(z)$ hat poles und Residuen ähnlich wie $\zeta_F(z)$ (Navas), aber möglicherweise mit geänderten Residuen-Strukturen (z.B. Doppelpole bei $z=0$? Neue imaginäre Pole?). Eine vorsichtige Analyse mittels Borel-Summation oder Mellin-asymptotik könnte die Konstante $\frac{1}{4\log\varphi}$ rigoros etablieren.

3. **Mellin-Inversion:**  
   Mit den analytischen Eigenschaften von $\zeta_F$ und $\zeta_F^{(F+1)}$ zurück zur Asymptotik von $R_c(N)$ über inverse Mellin-Transformation und Taubersätze.

**Chancen:** Diese Route parallisiert historisch bewährte Techniken mit neuer Dirichletreihe — hohes Erfolgspotential bei moderatem technischen Aufwand (falls $\zeta_F^{(F+1)}$ sich ähnlich wie bekannte Fälle verhält).

**Fallstricke:** Die neue Reihe könnte pathologisch behaglichere Konvergenzeigenschaften haben (z.B. kleinerer Konvergenz-Radius); dann helfen Navas' Techniken vielleicht nicht direkt.

**Hauptlieferable:** Theorem (mit vollen Beweis oder Detail-Skizze):
$$\log R_c(N) = \frac{(\log N)^2}{4\log\varphi} + O\left(\frac{\log N \log\log N}{\log\varphi}\right).$$

---

### Route B — Taubersätze (für summatorische Funktion)

**Zeithorizont:** 2–3 Monate  
**Analoge zu:** Ingham 1941 (binäre Partitionen); Hardy–Littlewood-Tauberian-Klassiker.

**Strategie:**

1. Falls $R_c(N)$ zu fluktuierig ist (aus Phase 1 bekannt), arbeite mit der Summatorischen:
   $$S_c(N) := \sum_{n\le N} R_c(n).$$
   
   Diese ist monoton wachsend und glatter.

2. **Tauberian Theorem (Ingham-Typ):** Wenn
   $$\sum_{n\ge1} S_c(n) x^n \sim (1-x)^{-\alpha} L(1/(1-x)) \quad (x\to 1^-)$$
   für bestimmtes $\alpha$ und (ggf. iteriertes) Logarithmus $L$, dann folgt
   $$S_c(N) \sim \frac{N^{\alpha+1}}{(\alpha+1)!} \exp(\sqrt{\beta \log N})$$
   oder ähnliche Form, je nach Struktur.

3. **Von $S_c$ zurück zu $R_c$:**  
   Differenzen $R_c(N) = S_c(N) - S_c(N-1)$ sind nicht direkt asymptotisch, es sei denn, $S_c$ ist sehr glatt. Dies ist die Gretchenfrage: falls $S_c(N)\sim A N^{\alpha} \exp(B(\log N)^\beta)$, dann ist $R_c(N)$ nur dann asymptotisch, wenn $\beta\ne 1$ oder weitere Glattheit vorhanden ist.

**Chancen:** Wenn $S_c$ sich wie $\exp(c(\log N)^2/\log\varphi)$ verhält, sind moderne Taubersätze (z.B. Delange, Karamata, etc.) wahrscheinlich anwendbar.

**Fallstricke:** Der Rückgang von $S_c$ zu $R_c$ ist oft subtil und erfordert zusätzliche Regularitätsannahmen.

**Hauptlieferable:** Theorem für $S_c(N)$ mit Asymptotik; Korollar für $R_c(N)$ unter Regularität-Bedingungen.

---

### Route C — Funktionalgleichung (explorativer Strang)

**Zeithorizont:** 1–2 Monate (explorativ; hohes Risiko)  
**Analoge zu:** de Bruijn's funktionale Gleichung für binäre Partitionen; Mahler-Operatoren.

**Strategie:**

1. **Gibt es eine funktionale Gleichung?**  
   Im binären Fall: $b(x) = b(x^2)/(1-x)$ (unter Berücksichtigung von Doublons und Zeckendorf-artigen Symmetrien).  
   
   Ähnliche Struktur für $R_c$? Vermutlich *nicht exakt*, aber möglicherweise approximativ unter der Zeckendorf-Substitution $x\to x^{\varphi^k}$ für bestimmte Sequenzen?
   
   Dies ist sehr spekulativ und bedarf Exploration.

2. **Selbstähnlichkeit nutzen:** Falls (teilweise) Selbstähnlichkeit vorhanden, Rekursionsgleichungen für asymptotische Konstanten aufstellen und lösen.

**Chancen:** Könnte zu unerwartet eleganten Argumenten führen, die dem Problembestand zu Grunde liegen.

**Fallstricke:** Sehr hochrisiko; könnte viel Zeit kostet ohne Resultat.

**Hauptlieferable (bei Erfolg):** Funktionale Gleichung (oder asymptotische Version); daraus Asymptotik-Theorem.

---

### Wahl und Priorisierung

**Empfehlung:** 
- **Primär:** Route A (Mellin + Dirichletreihen), da es Coons–Kristensen–Laursen parallisiert.  
- **Sekundär:** Route B (Taubersätze) als Fallback oder Verifizierung.  
- **Tertiary:** Route C (Funktionalgleichung) nur, falls Zeit/Energie vorhanden und explorative Ideen entstehen.

**Klarstellung nach Phase 1:** Route A und Route B stehen nicht zur Wahl
zwischen zwei Alternativen für dasselbe Ziel — sie beantworten verschiedene
Fragen. Route A bleibt die primäre Route für das rigorose
Asymptotik-Theorem über $\log R_c(N)$. Der Fluktuations-Befund aus Phase 1
(`docs/phases/phase1_report.md`) zeigt aber, dass $R_c(N)$ selbst über
$N \le 10^6$ so unregelmäßig ist (49.6% fallende Schritte) {claim:rc-not-monotone},
dass ein direkter
Taubersatz-Angriff auf $R_c(N)$ dadurch erschwert wird — die summatorische
Funktion $S_c(N)$ ist daher das numerisch sicherere Ziel für einen
Tauberian-Angriff (Route B), sobald sie verfolgt wird, statt $R_c(N)$ selbst.
Das ist keine Abschwächung von Route A, sondern eine Randbedingung an Route B,
sobald sie verfolgt wird.

---

## Phase 6 — Oszillationen und Fehlerterme

**Zeithorizont:** 6–8 Wochen (nach Phase 5 begonnen)  
**Kritikalität:** MITTEL — Verfeinert Theorem aus Phase 5

### Ziele

- Oszillatorische Korrektionen zu $\log R_c(N)$ explizit identifizieren und charakterisieren  
- Periodizität in $\log_\varphi N$ nachweisen/widersprechen  
- Fehlerschranken erhalten, die bei berechenbaren $N$ greifen

### Substanz

1. **Pole der Dirichletreihen (folgt aus Phase 5A):**  
   Die imaginären Pole von $\zeta_F$ liegen bei $z=\frac{2\pi i k}{\log\varphi}$, $k\in\mathbb{Z}\setminus\{0\}$.  
   
   Diese erzeugen Oszillationen periodisch in $\log_\varphi N$ mit Periode 1.  
   
   In $\zeta_F^{(F+1)}$ könnten *zusätzliche* Pole auftreten (oder alte verschwinden), was zu reicherer Spektrum führen könnte.

2. **Fourieranalyse der Residuen:**  
   Residuum bei Pol $z=z_j$ trägt einen Term wie $N^{\text{Re}(z_j)} \exp(2\pi i (\text{Im}(z_j)/\log\varphi) \log N)$ zur asymptotischen Entwicklung bei.
   
   Sammle Terme nach *imaginären* Teilen (Frequenzen) und schreibe
   $$\log R_c(N) = \frac{(\log N)^2}{4\log\varphi} + \text{(Hauptsekundärtermе)} + \Psi(\log_\varphi N),$$
   wobei $\Psi$ eine (meist kleine) periodische Funktion ist.

3. **Explizite Fourierkoeffizienten:**  
   Falls $\Psi(\phi) = \sum_{k\ne 0} a_k e^{2\pi i k \phi}$, extrahiere Koeffizienten $|a_k|$ aus theoretischen Residuen-Berechnungen und vergleiche gegen numerische Daten aus Phase 4.

4. **Fehlerschranken:**  
   Mit voller asymptotischer Entwicklung (bis zu Grad $d$ in Logarithmischen Termen) bekannt, verschaffe dir explizite, numerische Fehlerschranken der Form
   $$\left|\log R_c(N) - \left(\frac{(\log N)^2}{4\log\varphi}+\text{(Korrektionen)}\right)\right| \le C\frac{(\log N)^d}{(\log\varphi)^d}$$
   für effektive Konstante $C$ und Exponent $d < 2$ (besser als die Hauptordnung).

### Deliverables

1. **Theorem: Asymptotische Entwicklung mit Oszillationen**  
   Präzise Formulierung mit Fourierkoeffizienten.

2. **Technical Note:** `phase6_oscillations.md` (6–8 Seiten)  
   - Pole-Spektrum aus Phase 5.  
   - Fourieranalyse.  
   - Residuen-Berechnungen.  
   - Fehlerschranken.

3. **Grafiken:** Vergleich numerischer Residuen (Phase 4) gegen theoretische Vorhersage der Oszillationen.

---

## Phase 7 — Verallgemeinerung und Writeup

**Zeithorizont:** 2–3 Monate  
**Kritikalität:** MITTEL — Kontext und Publikation

### Ziele

- Die Ergebnisse auf allgemeine Caps und lineare Rekurrenzen verallgemeinern  
- Verbindung zu den anderen vier offenen Problemen in Ihrem System herstellen  
- Publikation schreiben

### Substanz

1. **Verallgemeinerung: Beliebige Caps $d_k \le c F_k^\alpha$**  
   
   Die Heuristik aus Phase 3 suggeriert, dass die Konstante $C_c(\alpha)$ interpoliert zwischen:
   - $\alpha=0$: $d_k\le c$ (alle Positionen gleich gecappt) → andere Asymptotik?  
   - $\alpha=1$: $d_k\le c F_k$ (unserer Fall) → $\frac{1}{4\log\varphi}$ (Konjektur)  
   - $\alpha\to\infty$: $d_k\le c F_k^\infty$ (praktisch unkappot) → $\frac{1}{2\log\varphi}$ (Coons–Kristensen–Laursen).
   
   Formuliere ein *parametrisches Theorem* mit $C_c(\alpha)$ als Funktion von $\alpha$ und verifiziere/beweise es für Grenzfälle.

2. **Allgemeine lineare Rekurrenzen (Pisot-Basis)**  
   
   Coons–Kristensen–Laursen zeigen, dass der uncapped-Fall für beliebige linear-rekurrente Sequenzen (unter Pisot-Bedingung) funktioniert.  
   
   Extend dies zu Caps: Wie muss man $d_k$ auf Basis-$\alpha$ (statt Fibonacci) anpassen? Welche analogue Konstante $C_c(\text{Basis})$ ergibt sich?

3. **Papierstruktur**  
   - **Introduktion:** Ihr Zahlensystem; Motivation (Repräsentations-Zählung); Platzierung im Literatur-Kontext (Mahler, de Bruijn, CKL, Navas).  
   - **Bekannte Anker:** Definieren, Satzbericht bestätigen für Fibonacci-uncapped und binär.  
   - **Hauptresultat:** Sandwich-Theorem (Phase 2); Heuristik (Phase 3); Haupttheorem mit Beweis (Phase 5).  
   - **Numerik:** Phase 4 Experimente.  
   - **Oszillationen:** Phase 6 verfeinert Theorem.  
   - **Verallgemeinerung:** $\alpha$-Interpolation; allgemeine Rekurrenzen (skizziert).  
   - **Offene Probleme:** Die fünf Probleme aus ihrem System; welche sind jetzt teilweise gelöst? Welche bleiben offen?  
   - **Anhang:** Vollständige Beweise schwieriger Lemmata; numerische Prozeduren.

4. **Verbindung zu anderen offenen Problemen in Ihrem System**  
   
   (Basierend auf Ihrer bisherigen Forschung — bitte präzisieren Sie die vier anderen Probleme; dann kann diese Sektion konkretisiert werden.)

### Deliverables

1. **Research Paper:** `CappedFibonacciPartitions.pdf`  
   - Typisch 25–40 Seiten für ein gutes Mathematik-Journal (z.B. J. Number Theory, Ramanujan J., etc.).  
   - Alle Theoreme rigoros; alle Numerik offengelegt.

2. **Preprint auf arXiv:** Vorbereitung und Submission.

3. **Präsentation (optional):** Kurz-Zusammenfassung (1–2 Seiten) für ggf. Diskussion mit Co-Autoren oder Mentoren.

---

## Kritischer Pfad und Priorisierung

```
Phase 0 (1–2 Tage)
    ↓
Phase 0.5 (1 Tag)
    ↓
Phase 1 (1–2 Wochen) ← Parallels mit Phase 3
    ↓
Phase 2 (2–3 Wochen) — schnelles Theorem
    ↓
Phase 3 (3–4 Wochen) ← kritisches Herzstück
Phase 4 (2–3 Wochen) — Numerik-Feedback
    ↓
**Entscheidungspunkt:** Konjektur robust genug für Phase 5?
    ↓ Ja
Phase 5A (4–6 Monate) — Mellin + Dirichletreihen
    ↓
Phase 6 (6–8 Wochen) — Oszillationen
    ↓
Phase 7 (2–3 Monate) — Writeup und Verallgemeinerung
```

**Zusammenfassung Zeithorizont:**  
- **Kurzfristig (4–6 Wochen):** Phase 0–2 liefern Sandwich-Theorem + Beweis für Größenordnung.  
- **Mittelfristig (3–4 Monate zusätzlich):** Phase 3–4 etablieren robuste numerische Konjektur.  
- **Langfristig (6–12 Monate):** Phase 5–7 erzielen vollständigen Beweis und publikationsfähiges Papier.

---

## Literatur-Anker (Referenzen für alle Phasen)

1. **Mahler, K.** (1940). "An application of Jensen's formula to polynomials." *Mathematica*, 7(2).  
   → Ursprung der Idee für binary partitions.

2. **de Bruijn, N. G.** (1948). "On the number of uncancelled elements in the sieve of Eratosthenes." *Proc. Ned. Akad.*  
   → Oszillations-Theorie für binary partitions.

3. **Coons, M., Kristensen, S., Laursen, M. L.** (2023). "Asymptotics for partitions over the Fibonacci numbers and related sequences." arXiv:2312.07404.  
   → *Zentral für unser Projekt:* uncapped Fibonacci partitions, Mellin/Dirichletreihen-Methode, Navas' $\zeta_F$.

4. **Navas, L.** (20XX). "Analytic continuation of the Fibonacci zeta function." [Referenz nachschlagen; in Coons–Kristensen–Laursen zitiert].  
   → $\zeta_F(z)$ analytische Fortsetzung; Pole und Residuen.

5. **Hardy, G. H., Ramanujan, S.** (1918). "Asymptotic formulae in combinatory analysis." *Proc. London Math. Soc.*  
   → Klassische partitions asymptotic; Ausgangspunkt für alle modernen Methoden.

6. **Meinardus, G.** (1954). "Asymptotische Formeln für Partitionsfunktionen." *Mathematische Annalen*.  
   → Generalisiert Hardy–Ramanujan auf Partitionen mit Restringierten Summanden; scheitert bei lacunaren Sequenzen (wie Fibonacci!).

7. **Stockmeyer, P., Chow, S., Slattery, T.** (2019–2020). "On the Fibonacci partition function" (OEIS A000119 und erwandte Arbeiten).  
   → Distinct Fibonacci partitions; Automatenliteratur.

---

## Anhang: Offene Fragen zur Erkundung

1. **Beyond $\alpha=1$:** Wie veränd sich $C_c(\alpha)$ für $\alpha \ne 1$?  
2. **Oszillationen:** Welche Frequenzen entstehen in $\Psi(\log_\varphi N)$?  
3. **Allgemeine Rekurrenzen:** Welche Pisot-Sequenzen verhalten sich ähnlich?  
4. **Zeckendorf-Konnex:** Wie verfeinert sich Ihre Zeckendorf-Darstellung unter dem Cap?  
5. **Generische Frage:** Ist die Halbierung durch den Cap ein universelles Phänomen in gefilterten Partition-Problemen?

---

**Version 1.0 — August 2026**  
Bereit für Feedback, Iterationen und konkrete Umsetzung.
