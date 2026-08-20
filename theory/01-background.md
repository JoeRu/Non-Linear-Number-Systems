# When 1 Is Greater Than 1

### A mathematical analysis of *"Number systems: when 1 is greater than 1"* (web-dreamer.de, 14 November 2009)

---

## 0. Summary

The 2009 article describes a home-made positional numeral system in which the place
values are the Fibonacci numbers `1, 1, 2, 3, 5, 8, …` and the digit permitted at each
place ranges from `0` up to the place value itself. The author observes three things:

1. the system represents every integer **more than once**;
2. consequently two different numerals — `10` and `1` — denote the same number, so that
   "1 > 1" in an apparent but not real sense;
3. everyday time-and-date notation is itself a non-uniform ("mixed") positional system.

All three observations are mathematically sound, and each one sits at the head of a
substantial research literature. Observation (2) in particular is not a paradox but a
precise instance of the distinction between **numerals** (syntax) and **numbers**
(semantics) — the same distinction that makes `0.999… = 1` true rather than absurd.

What the article invented independently is a **redundant numeration system with a
linear recurrent base sequence**. Such systems are the foundation of high-speed computer
arithmetic (carry-free addition), of the Zeckendorf/Ostrowski numeration used across
combinatorics on words, and of fault-tolerant "Fibonacci arithmetic" hardware. The
article's system is a maximally redundant member of that family, and its redundancy can
be computed exactly.

---

## 1. Formalising the construction

### 1.1 Definition

Let `F₁ = 1, F₂ = 1, F₃ = 2, F₄ = 3, F₅ = 5, …` be the Fibonacci numbers.

A **numeral** of length *n* is a tuple of digits

```
d = (d₁, d₂, …, dₙ)     with     0 ≤ d_k ≤ F_k
```

and its **value** is the evaluation map

```
val(d) = Σ_{k=1}^{n} d_k · F_k
```

This is exactly the article's rule: *"Sum over all places (placenumber × number)."*

Two conventions worth fixing, because the original table leaves them implicit:

- **Digit order.** The article writes places left-to-right as `1 1 2 3`, i.e.
  **least-significant digit first**. This is the reverse of ordinary decimal habit and is
  the direct cause of the "10 > 1" reading. (Numeral `10` = digits `d₁=1, d₂=0` → value 1;
  numeral `1` = digit `d₁=1` → value 1.)
- **Digit bound.** The bound `0 ≤ d_k ≤ F_k` (rather than `0 ≤ d_k ≤ 1`) is the article's
  own choice, and it is what makes the system *maximally* redundant. This is the
  single most consequential design decision in the piece.

### 1.2 Comparison with the standard framework

| | Standard base *b* | Article's system |
|---|---|---|
| Place values | `bᵏ` (geometric) | `F_k` (linear recurrence, dominant root φ) |
| Digit alphabet | `{0,…,b−1}` | `{0,…,F_k}`, alphabet grows with position |
| Digits per place | constant | position-dependent |
| Representations per integer | exactly 1 | many (see §4) |
| Lexicographic = numeric order? | yes | **no** |

The system is what the literature calls a **linear numeration system** in the sense of
Fraenkel (1985), with a non-canonical (over-complete) digit set.

---

## 2. Verification of the article's worked examples

Using places `(F₁,F₂,F₃,F₄) = (1,1,2,3)` with digit bounds `(1,1,2,3)`:

| Numeral (d₁ d₂ d₃ d₄) | Products `d_k·F_k` | Value |
|---|---|---|
| `1 0 2 0` | 1, 0, 4, 0 | **5** ✓ |
| `1 0 1 1` | 1, 0, 2, 3 | **6** ✓ |

Both of the article's examples are correct as written. (The original HTML table is
mangled by the 2009 blog export; the row labelled "Decimal 5 / 1 0 4 0" is the row of
**products**, not of digits, which is why it looks inconsistent at first reading.)

Exhaustive enumeration of this 4-place system gives:

| Value | Number of numerals | The numerals |
|---|---|---|
| 1 | 2 | `1000`, `0100` |
| 5 | 4 | `0011`, `0120`, `1020`, `1101` |
| 6 | 4 | `0002`, `0111`, `1011`, `1120` |

The pair `1000` / `0100` — read as strings, "1" and "10" — is precisely the article's
"1 > 1".

---

## 3. Property A — Completeness (surjectivity)

**Claim.** With *n* places, the system represents every integer in `[0, F_n·F_{n+1}]`,
with no gaps.

**Why the range is what it is.** The maximum value is
`Σ_{k=1}^{n} F_k·F_k = Σ F_k²`, and a classical Fibonacci identity gives

```
Σ_{k=1}^{n} F_k²  =  F_n · F_{n+1}
```

For the article's four places: `1 + 1 + 4 + 9 = 15 = F₄·F₅ = 3·5`. ✓

**Why there are no gaps.** A digit system with place values `u₁ < u₂ < …` and digit
bounds `m₁, m₂, …` represents every integer up to `Σ m_k u_k` without gaps precisely when

```
u_k  ≤  1 + Σ_{j<k} m_j u_j        for every k
```

(the Kempner–Fraenkel completeness condition; the greedy algorithm then always
succeeds). Here `u_k = m_k = F_k`, so the condition reads `F_k ≤ 1 + F_{k−1}F_k`, which is
true for all *k* with enormous room to spare. That slack is exactly the redundancy.

**Impact.** Completeness is the property that makes this a genuine numeration system
rather than a curiosity. Note that the *ordinary* Fibonacci base (digits `{0,1}`) is
also complete — it is the failure of the reverse implication (uniqueness) that
distinguishes the two.

---

## 4. Property B — Redundancy, quantified

This is where the article's system becomes genuinely interesting, because the
redundancy is not mild.

Let `S(n) = ∏_{k=1}^{n} (F_k + 1)` be the number of numerals of length *n*, and
`V(n) = F_n·F_{n+1} + 1` the number of values they cover.

| Places *n* | Largest place `F_n` | Max value | Numerals `S(n)` | Values `V(n)` | Avg. representations | Max representations |
|---|---|---|---|---|---|---|
| 1 | 1 | 1 | 2 | 2 | 1.00 | 1 |
| 2 | 1 | 2 | 4 | 3 | 1.33 | 2 |
| 3 | 2 | 6 | 12 | 7 | 1.71 | 2 |
| 4 | 3 | 15 | 48 | 16 | 3.00 | 4 |
| 5 | 5 | 40 | 288 | 41 | 7.02 | 10 |
| 6 | 8 | 104 | 2 592 | 105 | 24.69 | 37 |
| 7 | 13 | 273 | 36 288 | 274 | 132.44 | 202 |
| 8 | 21 | 714 | 798 336 | 715 | 1 116.55 | 1 746 |
| 9 | 34 | 1 870 | 27 941 760 | 1 871 | 14 934.13 | 23 638 |
| 10 | 55 | 4 895 | 1 564 738 560 | 4 896 | 319 595.29 | 510 384 |

**Asymptotics.** Since `log_φ F_k ≈ k`, we get

```
log_φ S(n)  =  n²/2 + O(n)          (super-exponential in n)
log_φ V(n)  =  2n  + O(1)           (exponential in n)
```

so the average number of numerals per value satisfies

```
S(n)/V(n)  =  φ^{ n²/2 + O(n) }
```

Expressed in terms of the represented integer `N ≈ φ^{2n}`, the average multiplicity is

```
N^{ Θ(log N) }
```

— **quasi-polynomial**: it grows faster than any fixed power of *N*, but slower than any
exponential. That is a very precise sense in which the article's system "creates every
decimal number more than once": it does so overwhelmingly.

**Information-theoretic reading.** The numerals carry `Θ(n²)` bits of syntax to encode
`Θ(n)` bits of number. The system is roughly `n/4`-fold wasteful. This is not automatically
a defect — see §9, where exactly this kind of slack is bought deliberately.

**The counting function.** Define `R(N)` = the number of numerals evaluating to *N*.
Its generating function is

```
Σ_N R(N) xᴺ  =  ∏_{k≥1} ( 1 + x^{F_k} + x^{2F_k} + … + x^{F_k·F_k} )
             =  ∏_{k≥1} ( x^{F_k(F_k+1)} − 1 ) / ( x^{F_k} − 1 )
```

This is a **restricted partition function with Fibonacci parts and Fibonacci-bounded
multiplicities**, and as far as I know its asymptotics have not been worked out
specifically. The `{0,1}`-digit analogue is well studied — it is OEIS **A000119**, the
number of representations of *N* as a sum of distinct Fibonacci numbers, the "Fibonacci
representation function", studied by Carlitz (1968), Stockmeyer, Robbins, Edson, and
others, and closely analogous to Stern's diatomic sequence. **This is a concrete open
avenue arising directly from the article** (see §14).

---

## 5. Property C — "1 > 1": order, and the syntax/semantics gap

### 5.1 What actually happens

The evaluation map `val : Numerals → ℕ` is **surjective but not injective**. Therefore:

- `val` induces an equivalence relation `s ~ t ⟺ val(s) = val(t)` on numerals;
- ordering numerals *by value* yields a **total preorder**, not a partial order —
  antisymmetry fails, because `1000 ≼ 0100` and `0100 ≼ 1000` yet `1000 ≠ 0100`;
- the lexicographic (or shortlex) order on strings **does not descend** to the quotient ℕ.

The statement "1 > 1" is therefore a category error of a productive kind: it compares
*numerals* using string order while reading them as *numbers*. Nothing about the
ordering of ℕ is violated; trichotomy is perfectly intact. What fails is a property we
tacitly rely on in base 10 and never name.

### 5.2 The property that quietly breaks

In standard base *b* with fixed width and digits `< b`:

```
lexicographic order on digit strings  =  numeric order
```

This is why radix sort works, why string-comparing zero-padded numbers works, why
ISO 8601 dates (`2009-11-14`) sort correctly as text, and why version numbers with
unbounded components (`1.10` vs `1.9`) famously *don't*. The article's system destroys
this coincidence, and version-number sorting is the everyday analogue of its "1 > 1".

### 5.3 Algorithmic consequence

Comparison ceases to be a single left-to-right digit scan. To compare two numerals you
must first **normalise** them to a canonical form. This turns an `O(n)` primitive into a
rewriting problem — which is precisely the subject of §10, and which turns out to have
a beautiful answer.

---

## 6. A terminological correction: numeral systems are not fields

The article links to the Wikipedia page on *Field (mathematics)* as the justification
for "you can go for another number system". This conflates two different things, and
disentangling them sharpens the whole piece:

| | What it is | Does the article change it? |
|---|---|---|
| **Field / ring** | Algebraic structure: the set, `+`, `×`, and their laws | **No** |
| **Numeration system** | Syntax: how elements are written down | **Yes** |

Base 10, base 2, Roman numerals, Zeckendorf and the article's Fibonacci system all
denote the *same* structure ℕ ⊂ ℤ ⊂ ℚ. Changing the base changes notation, not
arithmetic. (ℕ isn't a field anyway; ℤ is a ring, ℚ is the field.)

Genuinely *different* number systems — where the algebra itself changes — would be
things like finite fields `𝔽_p`, `p`-adic numbers `ℚ_p`, quaternions, or the surreal
numbers. Interestingly, **`p`-adics are the object the article was reaching toward
without knowing it**: there, the "places" run infinitely to the *left*, and the notion
of size is genuinely redefined. If the 2009 motivation was prime numbers (§12), `ℚ_p` is
the direction that actually pays.

This correction costs the article nothing. Its content is about *representation*, and
representation theory of the integers is a real and deep subject in its own right.

---

## 7. The canonical relative: Zeckendorf representation

The article rediscovered the Fibonacci base. The standard version constrains the digits
much harder, and buys uniqueness:

> **Zeckendorf's theorem** (Lekkerkerker 1952; Zeckendorf 1972).
> Every positive integer has a **unique** representation as a sum of non-consecutive
> Fibonacci numbers `F₂, F₃, F₄, …`.

| System | Digit alphabet | Extra constraint | Representations per *N* |
|---|---|---|---|
| Article's | `{0,…,F_k}` | none | `N^{Θ(log N)}` |
| Fibonacci `{0,1}` | `{0,1}` | none | A000119, grows slowly |
| **Zeckendorf** | `{0,1}` | no two adjacent 1s | **exactly 1** |
| "Lazy" Fibonacci | `{0,1}` | greedy-from-below | exactly 1 |

Examples: `10 = 8 + 2 = 1 0 0 1 0`, `19 = 13 + 5 + 1 = 1 0 1 0 0 1`.

Three consequences worth knowing:

- **The valid numerals form a regular language** — binary strings avoiding `11`.
  Its adjacency matrix has spectral radius φ, so the number of valid *n*-digit strings is
  Fibonacci-many and the entropy is `log φ`. In symbolic dynamics this is the
  **golden mean shift**, one of the standard first examples of a subshift of finite type.
- **Fibonacci coding.** Reversing a Zeckendorf numeral and appending a `1` gives a
  self-delimiting prefix-free code for the integers (the terminating `11` can occur
  nowhere else). It is a universal code, robust against single-bit errors in a way
  Elias codes are not, and used in practice in compression.
- **Fibonacci nim / Wythoff's game.** The winning strategy in Fibonacci nim is stated
  directly in terms of the Zeckendorf decomposition of the heap size (Whinihan 1963).
  Wythoff's game is governed by `⌊nφ⌋`. Numeration systems show up as *game theory*.

---

## 8. "1 > 1" is a recognised phenomenon, not an anomaly

The article worried that people found the non-uniqueness hard to accept. It is worth
knowing how much company it keeps.

**Familiar cases**

- `0.999… = 1` in base 10 — the single most argued-about fact in elementary mathematics,
  and structurally identical: two numerals, one number.
- **Roman numerals**: `IIII` and `IV` both denote 4; clock faces still use `IIII`.
- **Babylonian sexagesimal**: genuinely ambiguous. With no zero and no separator, the
  same cuneiform string could denote `1`, `60`, or `1/60`; disambiguation was contextual.
  A 4000-year-old, empire-scale deployment of "1 > 1".

**The golden-ratio base (base φ, "phinary"; Bergman 1957)**

Take place values `φᵏ` with digits `{0,1}`. Because `φ² = φ + 1`, the rewriting rule

```
100  ⟷  011
```

holds identically. So `1 = 0.11_φ`, and `100_φ = 011_φ`. The article's exact phenomenon,
in the system that is arguably the "real" Fibonacci base over ℝ. Every positive integer
has a terminating base-φ expansion (its "golden ratio base" form), and the
standard-form rule is again "no `11`".

**β-expansions (Rényi 1957; Parry 1960)**

The general theory: expansions in a non-integer base `β > 1`. For `1 < β < 2` almost
every number has **uncountably many** expansions (Erdős–Joó–Komornik). The bases in
which `1` has a *unique* expansion are the **univoque numbers**; the smallest of these is
the **Komornik–Loreti constant** `≈ 1.78723…`, whose digit sequence is the Thue–Morse
sequence, and which is transcendental. The article's "how can one apple be bigger than
one apple" is, in this language, the question of when a base is univoque — an active
research area.

---

## 9. Redundancy as an engineering feature

The single largest practical impact of the article's central property is that
**redundancy buys carry-free addition** — and this is not a footnote in computer
arithmetic, it is a foundation.

### 9.1 The mechanism

In base 10, adding `d + e` at one place can force a carry that propagates the entire
width of the operands: `999999 + 1`. Worst-case addition depth is `O(n)`, or `O(log n)`
with a carry-lookahead tree. If instead the digit set is *larger than necessary*, sums
can be absorbed locally: a carry travels at most a bounded number of places and dies.
Addition becomes **`O(1)` depth, independent of word length**.

- **Avizienis (1961), signed-digit representations**: digits `{−a,…,a}` with
  `b/2 < a < b`. Carry-free addition. The founding paper of the field.
- **Carry-save adders**: keep a number as an unevaluated (sum, carry) pair — a redundant
  representation — and normalise only once, at the end. Standard in every hardware
  multiplier ever shipped.
- **Booth encoding / non-adjacent form (NAF)**: the redundant signed-binary form with
  minimal Hamming weight; the reason scalar multiplication in elliptic-curve
  cryptography is fast. Note the NAF's defining constraint is *no two adjacent nonzeros* —
  literally the Zeckendorf condition transplanted to base 2.
- **Montgomery / lazy reduction** in modular arithmetic: keep values in a redundant
  range, reduce lazily.

The article's system has *far* more redundancy than any of these need — the digit bound
`F_k` grows exponentially where `2b` would do — but the qualitative insight ("more digits
than places require") is exactly the right one.

### 9.2 Redundancy as error detection

Because not every string is canonical, the set of canonical strings is a proper subset —
i.e. **a code with slack**. A hardware unit can check canonicity and detect faults.
Stakhov's programme of **"Fibonacci computers"** (Soviet work from the 1970s onward,
including patented Fibonacci-processor designs) built self-checking arithmetic on
precisely this observation, using Fibonacci *p*-codes. The article independently
reasoned its way to the representational half of that idea.

---

## 10. Normalisation, automata, and why the golden ratio makes it work

Section 5.3 left an algorithmic problem: to compare or canonicalise, you must
normalise. In the Fibonacci system this is done by rewriting with the recurrence
`F_k + F_{k+1} = F_{k+2}`:

```
011 → 100          (F_k + F_{k+1} = F_{k+2})
0200 → 1001        (and further carry rules for digits ≥ 2)
```

The key theorem is due to **Christiane Frougny**:

> **Frougny (1992), "Representations of numbers and finite automata".**
> In a linear numeration system whose characteristic polynomial has a **Pisot number**
> as dominant root, normalisation is computable by a **finite transducer**, hence in
> **linear time**, and addition is recognisable by a finite automaton.

The golden ratio φ *is* a Pisot number (its conjugate `−1/φ ≈ −0.618` has modulus < 1).
That is the structural reason the Fibonacci numeration system behaves as well as it
does, and why the article's redundant variant is tractable rather than chaotic: an
`O(n)` normaliser exists and can be written down explicitly.

### 10.1 The modern payoff: automatic theorem proving

This connection has become a live research tool. A sequence is **Fibonacci-automatic**
if a finite automaton reading Zeckendorf representations computes it. Because addition
is automaton-recognisable (Frougny), first-order statements about such sequences are
**decidable** — a Büchi-style decision procedure.

<cite index="2-1">This has been implemented in the free software **Walnut**, which supports base-*k*, Fibonacci (Zeckendorf), Tribonacci and user-defined numeration systems, and which produces a minimal DFA accepting the values making a given first-order formula true.</cite> <cite index="2-1">It has been used in over a hundred research papers and books, confirming old results, correcting errors in the literature, and proving new theorems.</cite>

<cite index="8-1">The numeration system is usually attributed to Zeckendorf, although Ostrowski had published a much more general system already in 1922.</cite> Concrete recent examples of the machinery in action: <cite index="6-1">the repetition threshold for the class of binary Fibonacci-automatic sequences has been determined to be 7/3</cite>, and <cite index="3-1">the Ziv–Lempel factorisation of the infinite Fibonacci word has been expressed and verified as a first-order formula in Walnut</cite>.

**For a reader of the 2009 article, this is the punchline**: the notational curiosity is
now infrastructure for machine-checked proofs in combinatorics on words.

---

## 11. Mixed radix — the time/date observation was exactly right

The closing remark about seconds/minutes/hours/days/years is, if anything,
under-claimed. **Mixed-radix numeration** is a fully developed subject.

A mixed-radix system has place values `u₀ = 1`, `u_k = b₁b₂⋯b_k` for a sequence of radices
`(b_k)`, with digits `0 ≤ d_k < b_{k+1}`. Time is `(…, 60, 60, 24, 7, …)`.[^1]

**The factorial number system (factoradic)** takes `b_k = k`, place values `k!`, digits
`0 ≤ d_k ≤ k`:

```
463 = 3·5! + 4·4! + 1·3! + 0·2! + 1·1!  =  "341010"
```

Because `Σ_{k=1}^{n} k·k! = (n+1)! − 1`, it is complete and unique — the same identity role
that `Σ F_k² = F_n F_{n+1}` plays in §3. Its use is not decorative: the factoradic gives the
**Lehmer code**, a bijection between `{0,…,n!−1}` and permutations of *n* elements, which
is the standard way to rank/unrank permutations, to generate a uniformly random
permutation, and to index into a permutation space without storing it. Cantor's mixed
radix expansions generalise the idea to arbitrary radix sequences.

**Ostrowski numeration** generalises the other way: given an irrational α, use the
denominators of its continued-fraction convergents as place values. Fibonacci numeration
is exactly the Ostrowski system for `α = φ = [1;1,1,1,…]` — the "simplest" irrational
producing the "simplest" recurrence. This links the article's construction to
Diophantine approximation, three-distance theorems, Sturmian words, and quasicrystals.

[^1]: The article writes `356,25` for the days in a year; `365.25` is intended.

---

## 12. The prime question

The article closes: *"Not a step closer to my prime problem."* That instinct was
correct in the short term and wrong in the long term — the interaction between digit
representations and primes has since become one of the striking success stories of
analytic number theory.

- **Gelfond's problem (1968), solved by Mauduit & Rivat (2010).**
  <cite index="17-1">The sum of the base-*q* digits of prime numbers is equidistributed in arithmetic progressions, for every *q* > 2</cite> — <cite index="16-1">in particular, the sum of the decimal digits of a prime is equally likely to be odd or even</cite>.
- **Bourgain (2015).** <cite index="17-1">There are the expected number of primes with *k* binary digits when a positive proportion of those digits are preassigned</cite>.
- **Maynard (2016/2019), primes with restricted digits.**
  <cite index="20-1">For any digit `a₀ ∈ {0,…,9}` there are infinitely many primes whose decimal expansion omits `a₀` entirely.</cite> <cite index="20-1">The proof combines the circle method, Harman's sieve, bilinear sums, the large sieve, the geometry of numbers and a comparison with a Markov process, exploiting the Fourier structure of the digit-restricted set.</cite> <cite index="11-1">The result was later extended to polynomial values in sufficiently large bases.</cite>

**Why representation nevertheless resists primality.** Positional systems are *additive*
(`val` is a sum), while primality is *multiplicative*. No positional system makes
primality locally readable, and there is a structural reason: by **Cobham's theorem**, a
set automatic in two multiplicatively independent bases is eventually periodic — and the
primes are not. So the primes cannot be automatic in any base, Fibonacci included. The
2009 intuition that the construction was "not a step closer" is, in this sense,
provably right.

**Where representation *does* pay for primes.** The `p`-adic numbers `ℚ_p` (§6) — where
the whole notion of magnitude is rebuilt prime by prime — are the genuine article. That
is where "another number system" changes the arithmetic rather than the notation, and
it is the route from the 2009 question to Hensel lifting, local–global principles, and
modular forms.

---

## 13. Research-topic map

Ordered from closest to the article outward.

### Tier 1 — directly what the article built
| Topic | Key names / entry points |
|---|---|
| Zeckendorf's theorem, Fibonacci base | Lekkerkerker 1952; Zeckendorf 1972 |
| Linear / non-standard numeration systems | Fraenkel, *Systems of Numeration*, Amer. Math. Monthly 92 (1985) |
| Redundant numeration, digit sets | Avizienis 1961; Matula |
| Counting Fibonacci representations | OEIS A000119; Carlitz 1968; Stockmeyer; Edson |
| Mixed radix, factorial base, Lehmer code | Knuth, *TAOCP* vol. 4A §7.2.1.2 |

### Tier 2 — the theory that explains it
| Topic | Key names / entry points |
|---|---|
| Normalisation by finite automata; Pisot condition | Frougny 1992; Frougny & Sakarovitch |
| β-expansions, non-integer bases | Rényi 1957; Parry 1960 |
| Golden-ratio base | Bergman 1957 |
| Univoque bases; Komornik–Loreti constant | Erdős–Joó–Komornik 1990; Komornik–Loreti 1998 |
| Ostrowski numeration; continued fractions | Ostrowski 1922; Berthé |
| Golden mean shift; subshifts of finite type | Lind & Marcus, *Symbolic Dynamics and Coding* |

### Tier 3 — where it is used now
| Topic | Key names / entry points |
|---|---|
| Automatic sequences; Fibonacci-automatic words | Allouche & Shallit 2003; Mousavi–Schaeffer–Shallit 2016 |
| Machine-checked combinatorics on words | Shallit, *The Logical Approach to Automatic Sequences* (CUP 2022); **Walnut** |
| Cobham's theorem and its generalisations | Cobham 1969; Durand |
| Carry-free computer arithmetic | Parhami, *Computer Arithmetic*; carry-save, Booth, NAF |
| Fault-tolerant Fibonacci arithmetic | Stakhov, Fibonacci *p*-codes |
| Fibonacci coding / universal codes | Apostolico & Fraenkel 1987 |
| Fibonacci nim, Wythoff's game | Whinihan 1963; Wythoff 1907 |
| Digits of primes | Mauduit–Rivat 2010; Bourgain 2015; Maynard 2019 |
| `p`-adic numbers | Gouvêa, *p-adic Numbers: An Introduction* |

---

## 14. Open problems arising directly from the article

These are genuine, and as far as I can determine, at least (1) and (2) are unstudied in
this exact form.

1. **Asymptotics of `R(N)`**, the number of representations of *N* in the article's
   system (digits `0 ≤ d_k ≤ F_k`). The `{0,1}` case is A000119 and well understood;
   the maximal-digit case has the generating function of §4 and appears untreated.
   Conjecture worth testing numerically: `log R(N) ~ c·(log N)²` with an explicit *c*,
   with bounded oscillation in the fractional part of `log_φ N`.

2. **Extremal numerals.** Which integers have the most / fewest representations at each
   length? (From the table: for *n* = 10 the maximum is 510 384 against an average of
   319 595 — the distribution is not sharply concentrated. Which *N* achieves it?)

3. **Normalisation cost.** Give an explicit finite transducer converting an
   article-system numeral to its Zeckendorf form, and determine its state complexity as
   a function of the digit bound. Frougny's theorem guarantees existence; the concrete
   automaton is a finite, doable project.

4. **Order recovery.** Characterise the largest sub-language of article-numerals on
   which lexicographic order *does* agree with numeric order. (Zeckendorf strings are
   one such; is it maximal?)

5. **Interpolating the digit bound.** Set `d_k ≤ g(k)` for `g` between `1` and `F_k` and
   trace the redundancy as a function of *g* — a one-parameter family joining Zeckendorf
   (`g ≡ 1`) to the article's system (`g = F_k`). Where is the phase transition in
   `log R(N)` growth?

---

## 15. Reading list, in order

1. Fraenkel, **"Systems of Numeration"**, *Amer. Math. Monthly* **92** (1985), 105–114.
   *The single best entry point; covers exactly the general framework the article
   improvised.*
2. Knuth, *TAOCP* vol. 2 §4.1 (positional systems) and vol. 4A §7.1.3 / §7.2.1.2
   (Zeckendorf, factorial base, Lehmer codes).
3. Allouche & Shallit, **Automatic Sequences: Theory, Applications, Generalizations**,
   CUP 2003 — chapters on numeration systems and Cobham's theorem.
4. Frougny, **"Representations of numbers and finite automata"**, *Math. Systems Theory*
   **25** (1992) — the Pisot/normalisation theorem.
5. Shallit, **The Logical Approach to Automatic Sequences**, CUP 2022 — and the
   **Walnut** software, to actually run experiments.
6. Parhami, **Computer Arithmetic: Algorithms and Hardware Designs** — redundant number
   systems as engineering.
7. Gouvêa, **p-adic Numbers: An Introduction** — for the prime motivation of §12.

---

## Appendix — reproducible code

```python
def fibs(n):
    F = [1, 1]
    while len(F) < n:
        F.append(F[-1] + F[-2])
    return F[:n]

def representation_counts(n_places):
    """Number of numerals evaluating to each value, digits 0..F_k at place F_k."""
    F = fibs(n_places)
    maxval = sum(f * f for f in F)          # == F_n * F_{n+1}
    counts = [0] * (maxval + 1)
    counts[0] = 1
    for f in F:                              # knapsack DP over places
        nxt = [0] * (maxval + 1)
        for v, c in enumerate(counts):
            if c:
                for d in range(f + 1):
                    if v + d * f <= maxval:
                        nxt[v + d * f] += c
        counts = nxt
    return F, maxval, counts

for n in range(1, 11):
    F, maxval, counts = representation_counts(n)
    strings = 1
    for f in F:
        strings *= f + 1
    print(n, F[-1], maxval, strings, maxval + 1,
          round(strings / (maxval + 1), 2), max(counts),
          "gaps:", counts.count(0))
```

Running this reproduces the table in §4, and confirms `counts.count(0) == 0` at every
length — the completeness claim of §3, verified empirically.

---

*Analysis of "Number systems: when 1 is greater than 1" (web-dreamer.de, 14 Nov 2009).
The article's two worked examples (5 and 6) verify exactly as written.*
