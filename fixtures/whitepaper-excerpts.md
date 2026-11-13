# Whitepaper excerpts — Post Fiat: A Buy-Side Internet of Value

Source: https://postfiat.org/whitepaper/ (live page crawled 2026-11-13 02:30 UTC)
and the raw text copy in postfiatl1v2 `docs/assets/raw/whitepaper.md.txt` (same commit
pin as above). Excerpts are verbatim; ellipses mark omissions.

## 1. Chain category (Part 1, §1)

> "The chain inherits the XRP category—known validators, deterministic finality,
> a fixed-supply native asset, fee burn, no validator subsidy—and changes three
> things. Validator-trust changes become protocol state ratified by Cobalt.
> Accounts and validators sign with ML-DSA from genesis, while the shielded
> stack itself remains classical."

## 2. Current fleet administration (Part 1, §1.8)

> "Admission therefore carries control-group and dependency checks, and the
> current fleet—six Foundation-administered validators with separate keys—
> establishes no independent control."

Note: this describes the controlled devnet fleet. The live testnet measured in
this pack has 25 UNL validators on 25 distinct community/operator domains
(see derived/vhs.json); whether those seats are independently operated is not
established by the public record — see finding F-08.

## 3. Consensus v2 committee arithmetic (Part 1, §1.8)

> "For a block committee of n validators, f = floor((n-1)/3), q = floor(2n/3)+1,
> 2q-n > f for every n … Consensus v2 is an explicit prepare/precommit
> protocol: q prepare votes form the durable lock, q precommit votes for the
> same non-nil block form the only commit certificate, and a proposal at view
> v+1 must carry a verified timeout certificate for view v with its highest
> prepare-QC reference."

## 4. Cobalt trust views (Part 1, §1.8)

> "Cobalt governs a different object: agreement over declared validator trust.
> A trust view lists essential subsets; a subset with size n_S, fault budget
> t_S, and threshold q_S must satisfy t_S < 2q_S - n_S, 2t_S < q_S … The
> devnet's graph is one six-validator subset with t_S=1, q_S=5: five-of-six
> ratifies, four-of-six fails."

## 5. August 2026 campaign (Part 1, §1.8)

> "The August 2026 campaign exercised the full path: Admission evidence packet
> → Deterministic selector → Cobalt RBC → ABBA → MVBA → DABC decision under the
> current trust graph → Distinct ML-DSA-65 authorizations from the current
> registry, one per support vote, at least q → Consensus v2 orders the update
> at its activation height → Execution verifies bindings and applies the
> registry change … At height 924, the legitimate rotation of validator 5
> carried authorizations from validators 0–4 and committed."

## 6. Evidence basis (Part 1, §1, and Part 3)

> "The evidence behind this paper consists of a limited-availability
> primary-market route on Ethereum mainnet (A666), a controlled private
> currency swap on a six-validator devnet, byte-exact replay of model-scored
> index inputs, and an adversarial governance campaign—all project-authored
> and pinned to immutable commits. Several requirements remain proposals: a
> shielded batch matcher, an on-ledger index registry, an emergency redemption
> path, and independently operated validators."
