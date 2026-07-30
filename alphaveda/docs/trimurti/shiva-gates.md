# Shiva Gate — Review, Challenge and Transformation

Source: PDF pp.7-8, 22-23. Applies before any AlphaVeda feature is marked shipped/complete —
this is the gate the Financial Council Consultation Rule (COUNCIL_RULES.md Rule E) operationalizes.

## Shiva objectives (source p.7, adopted as-is)
- Challenge product assumptions
- Identify dark patterns and decision bias
- Test recommendation stability
- Detect excessive churn
- Remove confusing or unused interactions
- Verify accessibility
- Review model and data failure
- Test whether users understand uncertainty
- Evaluate realised outcomes
- Decide whether the feature should be retained, revised or retired

## Shiva outputs (source pp.7-8)
1. UX review findings
2. Behavioural-bias audit
3. Accessibility review
4. Recommendation-risk review
5. Data-quality review
6. Usability-test results
7. Adversarial test results
8. Drift report
9. Remediation backlog
10. Release or rollback decision

## Shiva review scorecard (source pp.22-23)

| Review dimension | Question |
|---|---|
| Bias | Does the experience push the user toward action? |
| Harm | Could the recommendation create excessive churn? |
| Data failure | Does the design fail safely? |
| Model failure | Are unstable or weak recommendations blocked? |
| Transformation | What should be removed, corrected or rebuilt? |

## Gate rule (source p.22-23, the load-bearing rule)

> "A release should not proceed solely because the total combined score is high. A critical
> failure in any one dimension — such as misleading tax information — should block release."

This is the single most important rule in the whole Trimurti model for AlphaVeda: unanimous
high scores elsewhere never override one critical Shiva finding. Matches this system's own
False-Consensus Detection rule (`chief-of-staff/SKILL.md` Domain F) — a unanimous zero-modification
pattern across seats is itself a signal to look harder, not a green light.
