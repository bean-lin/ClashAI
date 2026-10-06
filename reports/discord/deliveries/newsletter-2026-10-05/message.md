# ClashAI daily update — October 5, 2026

**Where we stand**

No new model has earned a replacement deployment for R1e. Today produced some useful improvements in individual tests, but none met the full requirements. Live play is currently stopped; R1e remains selected. This first newsletter is being sent manually after the scheduled edition did not arrive.

**Training and game results**

We tested changes to training examples, spell aiming, tower representation, and reinforcement learning from game outcomes. Some gains were real: the model with added tower information matched 85 of 955 expert Rocket actions, compared with 73 for its immediate control and 54 for R1e on the same corrected observations. That still missed the required improvement over its control and slightly regressed on Furnace situations. Recorded-action agreement is not evidence of more game wins.

The completed matched gameplay comparison was less encouraging. Across the same 64 simulator scenarios, R1e won 45, the ordinary training control won 42, and the version with improved projectile targeting won 39. The uncertainty did not establish a significant improvement or harm, but the new version failed the predeclared win requirement.

Both subsequent reinforcement-learning experiments completed 256 training games each. The latest gave earlier decisions more direct credit for the final outcome. It matched 77 of 955 expert Rocket actions, tying its parent control; R1e matched 54. Its Rocket aim improved only slightly over the parent, while Barrel, Witch, Night Witch, Furnace and defense measures regressed. Both experiments were rejected. These are development results, not new gameplay victories.

**What the diagnoses taught us**

One apparent improvement was misleading when viewed only as a total: the first reinforcement-learning model gained 722 correct recorded actions because correct waits increased by 859 while correct plays fell by 137. Waiting can be the right decision, but that total does not demonstrate better defensive play. We are separating those measurements.

We also checked whether the value-learning part of training was overwhelming the action-learning signal. The sampled gradients did not support that explanation. Many training Rockets occurred well before the final result, which motivated the longer-credit experiment; its failure means changing that setting alone was insufficient, not that long-term credit is irrelevant.

**Better measurements before the next model**

The stationary spell-impact test passed its independent checks. In the tested simulator scenes, a Rocket aimed two tiles inward from a princess tower's center dealt the same damage as a center shot; three tiles inward missed. This demonstrates why coordinate agreement and actual damage need separate measurements. It does not change earlier model verdicts or prove real-client parity.

The first moving-target test failed its isolation check because a tower began firing before the observation window ended. Its failed records are preserved. A separate shorter-window test is now registered, with explicit accounting for the engine snapping taps to tile centers; it has not run yet. The goal is reliable damage measurement on moving and multiple targets before testing learned targeting changes.

We also verified an optional simulator adapter that stops requesting new decisions once play time ends while allowing the engine to finish its tiebreak. It preserves accepted commands and final outcomes in the tested cases. That is an engineering improvement, not a stronger-policy result.

**Data and live coverage**

We corrected an earlier coverage misunderstanding: the low Witch and zero Barrel counts described a reconstructed pro cohort, not overnight live play. A separate audit of 134 completed live logs found public observations in 105 logs, including Witch in 22, Goblin Barrel in 11, Night Witch in 2, and Furnace in 3. The other 29 logs remain unknown. Those encounters are useful diagnostics, not independent tactical opportunities or expert training labels.

Untouched evidence for final acceptance is still incomplete, especially for some important matchups. We are preserving the reserved confirmation data. This edition has no verified daily trophy total or clip links to include.

**Decision and next steps**

No replacement is accepted or deployed, and live play remains stopped. We are keeping the performance requirements intact. Next: finish the moving-target measurement checks, then register a small test of learning card choice and placement together. Persistent public match history and complete late-game training scenarios remain plausible, untested directions. Each needs a clear experiment rather than another blind parameter sweep.

Future updates will keep these sections readable, explain what results mean, and report failures as well as gains. The daily edition is scheduled for 9:30 PM Eastern, with a shared delivery record to prevent duplicates.
