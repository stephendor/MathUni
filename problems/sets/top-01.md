# top-01 — Topological spaces and open sets

**Module:** Topology · **Unit:** top-01
**Sources:** Munkres, *Topology*, 2nd ed. — §12 "Topological Spaces"
(pp. 75–78): the definition of a topology (p. 76), Examples 1–4 (pp. 76–77),
and the definition of *finer* / *coarser* / *comparable* (p. 77).

Everything below is done from the three axioms and nothing else. Bases are §13
and are not available to you; the standard topology on $\mathbb{R}$ is not
available either, so no argument here may quote an open interval as an example
of an open set. Where a counterexample is wanted, build it inside one of
Munkres's four examples.

Two reading conventions of Munkres's that this set relies on. He writes
$\subset$ for "is a subset of", **not** for proper containment — so
$\mathcal{T}' \supset \mathcal{T}$ permits $\mathcal{T}' = \mathcal{T}$, and
"strictly finer" is the separate phrase he reserves for proper containment
(p. 77). And his Example 4 is stated with its verification left to the reader
("as you can check", p. 77); Problem 4 is that verification.

Submit your written solutions via `/grade top-01`.

---

## Problem 1 (easy — the three axioms, run as a checklist)

Let $X = \{a, b, c\}$. For each collection below, decide whether it is a
topology on $X$. When it is not, name the axiom that fails — (1), (2) or (3) in
Munkres's numbering — and give the specific sets that witness the failure.

$$\mathcal{A} = \{\varnothing,\; X,\; \{b\},\; \{a,b\},\; \{b,c\}\}$$
$$\mathcal{B} = \{\varnothing,\; X,\; \{a\},\; \{b\}\}$$
$$\mathcal{C} = \{\varnothing,\; X,\; \{a,b\},\; \{b,c\}\}$$
$$\mathcal{D} = \{X,\; \{a\},\; \{a,b\}\}$$

(a) Classify all four.
(b) For $\mathcal{A}$, which you should find is a topology, list every union and
every pairwise intersection you had to check, and say why that finite list
suffices — that is, why you did not have to check unions of three or more
members separately.
(c) Axiom (3) is stated for *finite* subcollections. Prove that a collection
containing $\varnothing$ and $X$ and closed under arbitrary unions is a
topology as soon as it is closed under the intersection of **two** members.
State the induction cleanly.
(d) Munkres's axiom (2) is about "any subcollection". What does it say when the
subcollection is empty, and is that consistent with axiom (1)?

*(Munkres §12, p. 76 for the definition. $\mathcal{A}$ is the topology Munkres
describes in prose on that page — "the topology in which the open sets are $X$,
$\varnothing$, $\{a,b\}$, $\{b\}$, and $\{b,c\}$" — reproduced from his sentence
rather than from the diagram. $\mathcal{B}$, $\mathcal{C}$ and $\mathcal{D}$ are
set here, not read off Figure 12.1 or 12.2, whose contents the text does not
describe; every collection above is stated in full so that nothing depends on
reading a picture.)*

<details><summary>Nudge</summary>
For $\mathcal{C}$, intersect the two three-element sets. For $\mathcal{D}$,
compare the collection against axiom (1) before doing any set arithmetic.
For (d), a union over no sets is not $X$.
</details>
<details><summary>Strategy</summary>
Run the axioms in the order (1), (3), (2) rather than (1), (2), (3): axiom (1)
is a glance, axiom (3) usually fails first because pairwise intersections are
few, and axiom (2) is the long check. For (c), the statement to induct on is
"every intersection of $n$ members lies in the collection", and the inductive
step splits $U_1 \cap \cdots \cap U_n$ as $(U_1 \cap \cdots \cap U_{n-1}) \cap U_n$.
</details>
<details><summary>Partial</summary>
$\mathcal{A}$ is a topology. $\mathcal{B}$ fails (2): $\{a\} \cup \{b\} = \{a,b\}$
is absent. $\mathcal{C}$ fails (3): $\{a,b\} \cap \{b,c\} = \{b\}$ is absent.
$\mathcal{D}$ fails (1). In (d), the union of the empty subcollection is
$\varnothing$, which axiom (1) supplies anyway — so the two axioms overlap
rather than conflict.
</details>
<details><summary>Worked start</summary>
(a) $\mathcal{C}$. Axiom (1) holds. Axiom (2): the only union that could escape
is $\{a,b\} \cup \{b,c\} = X$, which is present. Axiom (3): but
$\{a,b\} \cap \{b,c\} = \{b\}$, and $\{b\} \notin \mathcal{C}$. So $\mathcal{C}$
fails axiom (3), witnessed by the pair $\{a,b\}$, $\{b,c\}$.

$\mathcal{D}$. The set $\varnothing$ is not a member, so axiom (1) fails
immediately. Note that no amount of closure under unions or intersections would
repair this: $\mathcal{D}$ is closed under both operations as it stands
($\{a\} \cap \{a,b\} = \{a\}$, $\{a\} \cup \{a,b\} = \{a,b\}$, and everything
meets or joins $X$ harmlessly), which is exactly why axiom (1) has to be stated
separately rather than derived.

$\mathcal{A}$, $\mathcal{B}$: ⟨your step⟩

(c) ⟨your step: state the inductive hypothesis, then do the step⟩

(d) ⟨your step⟩
</details>

---

## Problem 2 (easy–medium — the two extreme topologies, and the order between them)

Munkres's Example 2 (p. 77) gives two topologies that exist on every set: the
**discrete topology**, the collection of *all* subsets of $X$; and the
**indiscrete** or **trivial topology**, the collection consisting of $X$ and
$\varnothing$ only.

(a) Verify all three axioms for each, for an arbitrary set $X$. Do not skip the
indiscrete case on the grounds that it is obvious — write down what axioms (2)
and (3) actually require of a two-element collection.
(b) Prove that the discrete topology is finer than every topology on $X$, and
the indiscrete topology is coarser than every topology on $X$, in Munkres's
sense (p. 77).
(c) For which sets $X$ do the discrete and indiscrete topologies coincide?
Give the complete answer, including the empty set, and check your answer
against (b).
(d) List every topology on a two-element set $X = \{a,b\}$, and draw the
finer/coarser relation between them. How many are there? Which pairs are
comparable?

*(Munkres §12, p. 77 for Example 2 and for the definition of finer and coarser.)*

<details><summary>Nudge</summary>
In (b), "finer" is a statement about containment of collections, so both parts
are one line each once you have said what the collections are. In (c), test
$|X| = 0$ and $|X| = 1$ separately before you generalise.
</details>
<details><summary>Strategy</summary>
For (a), the point of writing it out is that the indiscrete collection is
closed under unions and intersections for a reason worth naming: every union or
intersection of members of $\{\varnothing, X\}$ is again $\varnothing$ or $X$,
because $\varnothing$ absorbs intersections and $X$ absorbs unions. For (d),
work by the number of members: a topology on $\{a,b\}$ must contain
$\varnothing$ and $X$, so the only freedom is which of $\{a\}$, $\{b\}$ to
include.
</details>
<details><summary>Partial</summary>
(c) They coincide exactly when $X$ has at most one point — for $X = \varnothing$
both collections are $\{\varnothing\}$ (note $\varnothing$ and $X$ are the same
set here, so the collection has one member, not two), and for a one-point set
both are $\{\varnothing, X\}$. (d) There are four.
</details>
<details><summary>Worked start</summary>
(a) Indiscrete. Axiom (1) is the definition of the collection. Axiom (2): a
subcollection of $\{\varnothing, X\}$ is one of $\varnothing$ (the empty
subcollection), $\{\varnothing\}$, $\{X\}$, $\{\varnothing, X\}$, whose unions
are $\varnothing$, $\varnothing$, $X$, $X$ respectively — all members. Axiom (3):
the same four subcollections have intersections $X$ (the empty intersection,
taken within $X$), $\varnothing$, $X$, $\varnothing$ — all members.

Discrete: ⟨your step⟩

(b) Let $\mathcal{T}$ be any topology on $X$ and let $\mathcal{P}$ be the
discrete topology. Every member of $\mathcal{T}$ is a subset of $X$, hence a
member of $\mathcal{P}$; so $\mathcal{P} \supset \mathcal{T}$, which is what
"finer" means. ⟨your step: the indiscrete half⟩

(c) ⟨your step⟩ (d) ⟨your step⟩
</details>

---

## Problem 3 (medium — the finite complement topology, and why "finite" is in axiom (3))

Munkres's Example 3 (p. 77): for a set $X$, let $\mathcal{T}_f$ be the
collection of all subsets $U$ of $X$ such that $X - U$ either is finite or is
all of $X$. He proves this is a topology using the two identities

$$X - \bigcup U_\alpha = \bigcap (X - U_\alpha),
\qquad X - \bigcap_{i=1}^{n} U_i = \bigcup_{i=1}^{n} (X - U_i).$$

(a) Reproduce both halves of his argument in full, and say for each identity
which finiteness fact about sets is doing the work. One of the two arguments
would collapse if the index set were allowed to be infinite — say which, and
where exactly.
(b) Munkres states both halves for **nonempty** elements of $\mathcal{T}_f$.
Explain why the restriction is needed — what goes wrong with the phrase "each
set $X - U_\alpha$ is finite" if some $U_\alpha$ is empty — and then dispose of
the empty cases separately, so that the proof is complete without the
restriction.
(c) Identify $\mathcal{T}_f$ when $X$ is finite. Prove your identification, and
say which of Munkres's other examples it coincides with.
(d) Show that axiom (3) genuinely needs its finiteness hypothesis: exhibit a
countably infinite family of members of $\mathcal{T}_f$ on $X = \mathbb{Z}$
whose intersection is not a member. State the intersection explicitly and check
it against the definition of $\mathcal{T}_f$.

*(Munkres §12, p. 77, Example 3, including both displayed identities.)*

<details><summary>Nudge</summary>
For (d) the members to intersect are complements of single points. For (b), ask
what $X - \varnothing$ is.
</details>
<details><summary>Strategy</summary>
(a) The union half needs "a subset of a finite set is finite" (an intersection
of finite sets is finite as soon as *one* of them is). The intersection half
needs "a finite union of finite sets is finite" — and it is that one that fails
for infinite index sets, since an infinite union of finite sets can be infinite.
(d) Take $U_n = \mathbb{Z} - \{n\}$ and intersect over $n \geq 1$; the
complement of the intersection is $\{1, 2, 3, \dots\}$.
</details>
<details><summary>Partial</summary>
(b) $X - \varnothing = X$, which is not finite when $X$ is infinite, so the
sentence "each set $X - U_\alpha$ is finite" is false as soon as one $U_\alpha$
is empty. The repair: dropping empty members changes neither the union nor the
value of the intersection unless *some* member is empty, in which case the
intersection is $\varnothing$, which is in $\mathcal{T}_f$ by the "or is all of
$X$" clause.
(c) $\mathcal{T}_f$ is the discrete topology when $X$ is finite.
</details>
<details><summary>Worked start</summary>
(a) Union half. Let $\{U_\alpha\}_{\alpha \in J}$ be nonempty members of
$\mathcal{T}_f$, so each $X - U_\alpha$ is finite. Then
$X - \bigcup U_\alpha = \bigcap (X - U_\alpha)$, and this is a subset of any
one of the finite sets $X - U_{\alpha_0}$, hence finite. So
$\bigcup U_\alpha \in \mathcal{T}_f$. The finiteness fact used is that a subset
of a finite set is finite; note that this argument places **no** restriction on
the size of $J$, which is exactly why axiom (2) may be stated for arbitrary
subcollections.

Intersection half. ⟨your step: run the second identity, and name the finiteness
fact — then say precisely which sentence of your argument fails if $n$ is
replaced by an infinite index set⟩

(b) ⟨your step⟩ (c) ⟨your step⟩

(d) Put $U_n = \mathbb{Z} - \{n\}$ for $n \geq 1$. Each $U_n \in \mathcal{T}_f$,
since $\mathbb{Z} - U_n = \{n\}$ is finite. ⟨your step: compute
$\bigcap_{n \geq 1} U_n$, compute its complement, and check both clauses of the
definition of $\mathcal{T}_f$ against it⟩
</details>

---

## Problem 4 (medium–hard — Example 4, which Munkres leaves to you)

Munkres's Example 4 (p. 77) defines $\mathcal{T}_c$ to be the collection of all
subsets $U$ of $X$ such that $X - U$ either is countable or is all of $X$, and
says only "Then $\mathcal{T}_c$ is a topology on $X$, as you can check." This
problem is that check, and then the comparison Munkres does not make.

(a) Prove that $\mathcal{T}_c$ is a topology on any set $X$, following the shape
of Example 3. Say explicitly which fact about countable sets replaces "a finite
union of finite sets is finite", and confirm that it is true.
(b) Prove that $\mathcal{T}_f \subset \mathcal{T}_c$ for every $X$.
(c) Determine exactly when the containment in (b) is **strict**. The natural
first guess is "when $X$ is uncountable"; decide whether that is right, and
prove the correct statement. Give the witnessing set.
(d) Identify $\mathcal{T}_c$ when $X$ is countable, and prove it. Then say
whether $\mathcal{T}_f$ and $\mathcal{T}_c$ are comparable on
$X = \mathbb{Z}$, and if so which way round.

*(Munkres §12, p. 77, Example 4 — stated there, with the verification left to
the reader. Parts (b)–(d) go beyond what §12 states; they are built from the
definitions of $\mathcal{T}_f$, $\mathcal{T}_c$ and "finer" on the same page.)*

<details><summary>Nudge</summary>
In (c), before assuming uncountability is needed, try $X = \mathbb{Z}$ and the
set of even integers.
</details>
<details><summary>Strategy</summary>
(a) The replacement fact is that a finite union of countable sets is countable,
and that a subset of a countable set is countable. Both halves of Example 3's
argument then transcribe word for word.
(c) The guess is wrong. What (b) needs to be strict is a subset $D \subset X$
that is countable, infinite, and not all of $X$; such a $D$ exists whenever $X$
is infinite, not merely when it is uncountable. Then $U = X - D$ lies in
$\mathcal{T}_c$ and not in $\mathcal{T}_f$.
</details>
<details><summary>Partial</summary>
(b) If $X - U$ is finite it is countable, and the "all of $X$" clause is common
to both definitions; so every member of $\mathcal{T}_f$ is a member of
$\mathcal{T}_c$.
(c) The containment is strict exactly when $X$ is infinite; the two collections
are equal exactly when $X$ is finite, where both are discrete.
(d) $\mathcal{T}_c$ is the discrete topology whenever $X$ is countable.
</details>
<details><summary>Worked start</summary>
(b) Let $U \in \mathcal{T}_f$. Then $X - U$ is finite or is all of $X$. In the
first case $X - U$ is finite, hence countable, so $U \in \mathcal{T}_c$; in the
second case $U \in \mathcal{T}_c$ by the second clause of that definition
directly. Hence $\mathcal{T}_f \subset \mathcal{T}_c$, i.e. $\mathcal{T}_c$ is
finer than $\mathcal{T}_f$.

(c) Suppose $X$ is infinite. Choose a countably infinite subset
$D \subset X$ with $D \neq X$ — when $X$ is countably infinite take, for
instance, $X = \mathbb{Z}$ and $D$ the even integers; when $X$ is uncountable
any countably infinite subset will do, since it cannot exhaust $X$. Put
$U = X - D$. Then $X - U = D$ is countable, so $U \in \mathcal{T}_c$; but $D$
is infinite and $D \neq X$, so $U \notin \mathcal{T}_f$.
⟨your step: now prove the converse — that if $X$ is finite the two collections
are equal — and conclude the exact condition for strictness⟩

(a) ⟨your step⟩ (d) ⟨your step⟩
</details>

---

## Problem 5 (hard — the comparison relation, and the limits of Munkres's metaphor)

Munkres defines $\mathcal{T}'$ to be **finer** than $\mathcal{T}$ when
$\mathcal{T}' \supset \mathcal{T}$, **strictly finer** when the containment is
proper, and calls the two topologies **comparable** when one contains the other
(p. 77). He then remarks that "Two topologies on $X$ need not be comparable."

(a) Let $\operatorname{Top}(X)$ be the set of all topologies on $X$. Prove that
"is finer than" is a partial order on $\operatorname{Top}(X)$ — reflexive,
antisymmetric, transitive — and say in one sentence why all three come for free.
Then exhibit two topologies on $\{a,b,c\}$ that are not comparable, so that the
order is not total.
(b) Prove that the intersection $\bigcap_{i \in I} \mathcal{T}_i$ of any
non-empty family of topologies on $X$ is again a topology on $X$. Where does
your argument use that each $\mathcal{T}_i$ satisfies axiom (2) for *arbitrary*
subcollections?
(c) Show that the union of two topologies need not be a topology, using your
incomparable pair from (a). Which axiom fails, and with which sets?
(d) Munkres offers an image: a topological space is "something like a truckload
full of gravel — the pebbles and all unions of collections of pebbles being the
open sets", and smashing the pebbles smaller makes the topology finer. Assess
it. Name one thing the image gets exactly right, and two things it gets wrong —
one about the shape of the open sets it suggests, and one about the structure
of $\operatorname{Top}(X)$ that your answers to (a) and (b) contradict. Support
each with a specific example from this problem set.

*(Munkres §12, p. 77 for the definition of finer/coarser/comparable, for the
gravel passage, and for the remark that two topologies need not be comparable.
Parts (a)–(c) are derived from that definition; §12 states none of them.)*

<details><summary>Nudge</summary>
For (a), remember that "finer" *is* the containment relation on collections, so
you are being asked about $\supseteq$ on a set of sets. For (d), the gravel
image makes the open sets look like unions of a fixed disjoint pile; look at
$\mathcal{A}$ from Problem 1.
</details>
<details><summary>Strategy</summary>
(b) Take $U_\alpha \in \bigcap_i \mathcal{T}_i$ for all $\alpha$; then for each
fixed $i$ the whole family lies in $\mathcal{T}_i$, so the union lies in
$\mathcal{T}_i$; as $i$ was arbitrary, the union lies in the intersection. The
"arbitrary subcollections" clause matters because the family $\{U_\alpha\}$ you
are handed may be of any size, and you must feed it whole to each
$\mathcal{T}_i$.
(d) The image is right that a topology is determined by a generating collection
together with its unions — which is exactly §13's notion of a basis, and is why
the metaphor is placed here. It is wrong that the generators can be taken
pairwise disjoint, and wrong that any two topologies can be compared by
"which was smashed finer".
</details>
<details><summary>Partial</summary>
(a) Reflexivity, antisymmetry and transitivity are inherited from $\subseteq$ on
sets, since "finer" is literally containment; the only content is that
$\operatorname{Top}(X)$ is a set of collections. An incomparable pair:
$\mathcal{T}_1 = \{\varnothing, X, \{a\}\}$ and
$\mathcal{T}_2 = \{\varnothing, X, \{b\}\}$.
(c) The union $\{\varnothing, X, \{a\}, \{b\}\}$ fails axiom (2), since
$\{a\} \cup \{b\} = \{a,b\}$ is absent — this is $\mathcal{B}$ from Problem 1.
</details>
<details><summary>Worked start</summary>
(a) Both $\mathcal{T}_1 = \{\varnothing, X, \{a\}\}$ and
$\mathcal{T}_2 = \{\varnothing, X, \{b\}\}$ are topologies on $X = \{a,b,c\}$:
each contains $\varnothing$ and $X$, and every union or intersection of members
of a collection of the form $\{\varnothing, X, S\}$ is again $\varnothing$, $S$
or $X$. Neither contains the other, since $\{a\} \notin \mathcal{T}_2$ and
$\{b\} \notin \mathcal{T}_1$. So they are not comparable, and the order is not
total.
⟨your step: the three order axioms, and the one sentence saying why they are
free⟩

(b) Write $\mathcal{T} = \bigcap_{i \in I} \mathcal{T}_i$. Axiom (1):
$\varnothing$ and $X$ lie in every $\mathcal{T}_i$, hence in $\mathcal{T}$.
⟨your step: axioms (2) and (3), and the sentence identifying where "arbitrary
subcollections" is used⟩

(c) ⟨your step⟩ (d) ⟨your step⟩
</details>
