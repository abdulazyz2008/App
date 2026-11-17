# Board: CrashEcho AI + RoadMemory

**Vote: 3 FUND IF, 0 FUND, 0 PASS. Average score 4.3 / 10** (Offers 4, Monopoly 4, Product 5).

The pain is real and the outcome is strong. Nobody would fund it as pitched. All three would fund a narrower version with proof behind it.

Memos: [offers](board/offers.md) · [monopoly](board/monopoly.md) · [product](board/product.md) · [brief](board/brief.md)

## Risks raised by more than one member (most dangerous first)

1. **No proof that detection works (all 3).** There are no crash-detection or false-alarm rates and no field data. The Offers lens calls the likelihood of success "zero" until this exists. The Product lens says a false SOS to the rider's family destroys trust after once or twice. The Monopoly lens says there's no sign the technology is 10x better than the crash detection already built into phones.
2. **RoadMemory has a cold start (all 3).** Warnings only work once enough riders have confirmed a hazard. In a new city the map is empty, so on day one the product is just a crash alert.
3. **No paying buyer yet (Offers and Monopoly; Product agrees).** The rider has the pain but there's no sign they have the money. All three reject rider freemium (a) as the lead model.
4. **Battery drain and phone limits on background apps (all 3).** Nothing in the deck covers them. Riders could uninstall, or the phone could quietly stop the app.
5. **Hand-offs the team doesn't control (Product; Monopoly on platforms).** The 108 ambulance call, "hospital matched to injury", and the gig platform itself are all outside the team's control. The Monopoly lens adds that the platform paying for it could also copy it.

## Where the board disagrees (kept on purpose)

- **What to do with RoadMemory.** The Product lens says park it and ship only crash-to-help. The Monopoly lens says RoadMemory is the *only* part that could become a moat (a network effect), so keep it and own the data. The Offers lens sits in between: keep the rider app free so riders build the map, which raises its value to buyers.
- **Cities and insurers.** The Monopoly lens wants to sell the pooled hazard map to cities (d) and insurers (c) once the team has enough data. The Offers lens adds insurers second but treats cities as a bonus. The Product lens warns that both turn this into a data business and put pressure on the privacy promise.
- **The platform as customer.** Offers and Product see one fleet deal as easy access to thousands of riders. The Monopoly lens sees the same platform as the most likely competitor.

## Suggested business model (the founders asked)

All three back **(b): a per-rider monthly fee paid by delivery fleets / gig platforms, with a free app for the rider.** The price is open: see `/founder-pricing` and `/founder-cfo`.

## Conditions checklist

Proof
- [ ] Field test on real two-wheeler rides reporting crash-detection rate and false-alarm rate (all 3)
- [ ] Compared head to head with the crash detection already built into phones (Monopoly)
- [ ] Battery cost measured over a ~10-hour delivery shift, and behaviour under Android/iOS limits on background apps (Monopoly, Product) → `/founder-consumer` for whether riders tolerate it
- [ ] Every hand-off mapped and tested: 108 call, hospital choice, family alert (Product)

Buyer and model
- [ ] Pick one metro (all 3)
- [ ] One fleet or platform signs a paid pilot or LOI at a stated per-rider price (all 3) → `/founder-pricing`, `/founder-cfo`
- [ ] Cost of one rider crash to a fleet measured, so the price is set by value (Offers) → `/founder-cfo`
- [ ] Offer written as a stack with a named guarantee tied to a fleet outcome (Offers) → `/founder-offer`
- [ ] Rider privacy terms in the contract: the fleet gets crash alerts, no tracking (Product)
- [ ] The startup keeps the rights to the anonymised hazard data and can pool it across fleets (Monopoly)

Scope and moat
- [ ] Decide the one thing to ship first: crash-to-help, or crash-to-help plus RoadMemory (Product vs Monopoly; resolve this)
- [ ] If RoadMemory stays: set a rider-density target for the pilot city and show the map getting more useful as riders are added (Monopoly) → `/founder-cfo`
- [ ] Answer "what do you know that phone makers and the platforms don't?" (Monopoly)
- [ ] Check what fleets already give riders for safety and insurance, and whether platforms are building this themselves (all 3) → `/founder-competitors`

## The strongest version the board can see

This is narrower than the pitch. **A rider-safety service sold to delivery fleets in one Indian city:** the fleet pays per rider per month, and every rider gets a free app. Its first job is crash-to-help, and it has to be measurably reliable: few false alarms, a tested path to 108 and to family, and acceptable battery use over a full shift. RoadMemory runs quietly underneath. Every fleet's riders feed one anonymised hazard map that the startup owns and pools across fleets. The map isn't sold until the density data shows it works; after that it becomes the moat and the source of later revenue from insurers and maybe cities. The pitch leads with the full seven-step chain for five audiences. The board would lead with one buyer, one city, one moment, and proof.
