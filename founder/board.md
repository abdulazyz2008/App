# Board summary: Self-Recharging Washing Machine

## The vote
**3 PASS, 0 fund if, 0 fund** · average score **1.3 / 10** (Offers 1, Monopoly 1, Product 2)

## Risks every member raised (these come first)
1. **The two-battery loop cannot create energy.** Energy is conserved, and every step (motor, generator, charging) turns some of it into heat. With realistic efficiencies a round trip returns about **69–77%** of what left Battery A, and that is *before* any washing. Washing is energy that leaves the loop for good (friction, warm water and clothes). Each swap delivers less than the last: 100% → ~75% → ~56% → ~42%. The generator also brakes the drum, so the machine washes **less** than it would with the generator removed.
2. **The batteries are small for the job.** 15,000 mAh is a charge, not an energy figure, so the voltage matters. At 3.7 V that is about 55 Wh per battery. At 12 V it is about 180 Wh. Heating one load of water (15 L from 15 °C to 40 °C) takes about 440 Wh, and the drum takes roughly another 100–300 Wh. One battery covers only about 9–28% of a heated load.
3. **Once the loop is removed, nothing is left to defend.** What remains is an ordinary washer with a battery in it. It has no proprietary edge, no proof and no guarantee anyone could keep.

## Where the members disagreed
- **Product (2)** scored slightly higher than the other two. Its reason was that the customer moment is clear in one sentence ("start a load, never think about the socket"). Offers and Monopoly scored only the mechanism, and the mechanism fails.
- **Offers** said the washer market itself is fine, with buyers who have money and are easy to reach. **Monopoly** said that even a working battery washer has no route to a monopoly unless it starts in a narrow niche.

## Conditions to come back (merged checklist)
The board would only look at a **different** business. Each item is a requirement for that pitch:
- [ ] Drop the self-recharging claim completely. All energy must come from outside the machine: grid, solar or off-peak power.
- [ ] Give the battery voltage and measure the Wh per cycle on a meter, with and without hot water.
- [ ] Name the first small market, for example homes with an unreliable or no grid connection. → `/founder-consumer`
- [ ] Find out who already sells battery, solar or manual washers to those buyers. → `/founder-competitors`
- [ ] State a price and the cost per load. → `/founder-pricing`, `/founder-cfo`
- [ ] Explain how the first 100 customers arrive.
- [ ] Offer a guarantee you could actually honour.

## The strongest version the board can see
This is **not what was pitched.** The board sees a **battery-buffered washer for homes with unreliable or no power**. It charges from a small solar panel or from off-peak grid power, washes in cold water to keep the energy budget small, and finishes a load during a blackout. The honest claim is "it runs when the power doesn't" and never "it powers itself". That version is buildable and testable. Whether anyone would pay for it is still an open question for `/founder-consumer` and `/founder-competitors`.
