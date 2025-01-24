## Page 1

# Aeration costs in stirred-tank and bubble column bioreactors  
  
## ABSTRACT  
  
To overcome knowledge gaps in the economics of large-scale aeration for production of commodity products, Aspen Plus is used to stimulate steady-state oxygen delivery in both stirred-tank and bubble column bioreactors, using published engineering correlations for oxygen mass transfer as a function of power input, coupled with new equipment cost estimates developed in Aspen Capital Cost Estimator and validated against vendor quotations. These simulations describe the cost efficiency of oxygen delivery as a function of oxygen uptake rate and vessel size, and show that capital and operating costs for oxygen delivery drop considerably moving from small-scale (200 m³) to world-class size (500 m³) reactors. This analysis suggests bubble-column reactor systems can reduce overall costs for oxygen delivery by 10-20% relative to stirred tanks at low to moderate oxygen transfer rates up to 150 mmol/L·h.  
  
## Keywords  
Aerobic fermentation  
Bioreactor design  
Capital cost  
Gas-liquid oxygen mass transfer

---

## Page 2



---

## Page 3

Biochemical Engineering Journal xxx (2017) xxx-xxx  
  
3  
  
determine the total system power demand for most of the users shown  
in Fig. 1, the compression, air cooler, chiller for FCR, circulation  
pump, and chiller (scaled by cooling duty). The cooling tower was not  
included because its power consumption is insignificant compared to  
the chiller.  
The independent variable determining total system power was  
taken to be the oxygen uptake rate (OUR), in an operating bioreactor,  
the submersed culture provides some OUR, which, at steady-state, is  
equal to an oxygen transfer rate (OTR); the product of a mass transfer  
coefficient, k  
a (m h−1), times the volumetric available surface area, a, and  
an oxygen concentration driving force, (C∗ − C).  
OUR = OTR = k  
a a (C∗ − C)  
  
(1)  
  
where k  
a is usually lumped together and C∗ and C are respectively the equilibrium and the actual dissolved oxygen concentrations  
(mol/L), the reactor design purposes, several literature sources [19] and  
STRs, the two-viscous mass transfer correlation of [13] is frequently  
used as a design equation. This correlation describes k  
a as a function  
of bioreactor vessel power input (P) per unit volume (V) and the gas  
superficial velocity (v  
g) in the reactor, i.e.  
k  
a(s−1) = 0.002 (P/V)(vm)0.5 (v  
g m/s)−0.2  
  
(2)  
  
where the pre-factor and exponents are adjustable for specific systems. This correlation is often relied on for its simplicity, as it does  
not depend on specific reactor geometry, or impeller speed, number,  
and type (details the accessible range of P/V is an implied function of  
these [14]). The review of [15] lists other, more complex, correlations  
for k  
a, but notes that the original [13] (Ref correlation (Eq. (2))) is  
the most frequently used for basic design in non-viscous systems. Reactor sizes > 100 m3 are out of the fit space for the original correlation,  
but [16] developed a zoned model where the correlation was applied  
independently to stirred and unstirred zones within a large reactor,  
and concluded that in the limit of good mixing (L/dk > 1000), the correlations could be simply applied to the entire volume. In many event,  
well proven correlations like Eq. (2) can be used to determine idealized steady-state bioreactor scenarios and make cost productions.  
For BCRs, [17] proposed a similar correlation, with k  
a as a primary  
function of the gas superficial velocity [13], which further described  
how this correlation can be corrected for temperature, T, and effective  
broth viscosity, m  
br, resulting in:  
k  
a(s−1) = 0.32 (m  
s m/s)0.1 (m  
br/μP)0.84 ∗ 1.025(T-20)  
  
(3)  
  
It should be noted that BCRs are not normally recommended for  
fermentations where the broth viscosity is higher than 2 cP. We therefore limit our comparisons to non-viscous (aqueous) systems in the  
scope of this study.  
In aerobic culture where molecular oxygen (O2) is the primary  
electron acceptor at the end of the electron transport chain, it can be  
shown that the heat of reaction is proportional to the oxygen uptake  
rate, regardless of the actual effective stoichiometry or products of  
the culture [18]. Approximately 100 kcal of heat is released per g-mol  
O2 consumed, which is equivalent to the heat of reaction for an O2

---

## Page 4



---

## Page 5

# Biochemical Engineering Journal xxx (2017) xxx-xxx  
  
Fig. 2. Capital costs (uninstalled, 2014$) of STRs in 316SS as a function of agitator power.  
  
Compression power is required for larger volumes of air. The power scales slightly more favorably with volume at higher O2R, with a 10% power reduction between 500 m^3 and 1000 m^3. In either case, for large reactors at a given O2R, the total bioreactor system power consumption scales approximately linearly with total liquid volume. This implies that any beneficial economies of scale realized at larger vessel sizes are more strongly a result of reduced capital costs for the vessels and agitators than reduced operating costs from differences in power demand or cost efficiency.  
  
To investigate the economies of scale possible for aeration, capital and operating costs were incorporated into the analysis. The bioreactor capital costs were taken from ACCE as discussed above. For STRs, these were obtained from Fig. 2 as a function of optimized agitator power. A fixed installation factor of 2.3 was used to obtain the direct cost for the bioreactors. Capital costs for compressors, pumps, and heat exchangers were also estimated using ACCE, though these were generally small compared to the reactor cost. The total capital cost was then converted to an annualized capital charge factor and $400 operating hours per year, consistent with NEL's cost flow calculation methodologies, e.g., as presented in [12] and [10]. Operating costs were calculated as the sum of electricity at $0.06/kW-h and maintenance at 6% of installed capital. The resulting aggregate OPEX plus annualized CAPEX costs were combined with the oxygen delivery rate calculated for each condition to determine the total cost per kilogram of oxygen delivered. This can be thought of as the total cost to deliver a kg of oxygen to a culture, for a single reactor and the associated equipment depicted in Fig. 1. Fig. 3b shows a specific total oxygen demand, for which capital and operating costs were normalized by reactor volume ($/m^3). Note that the costs of substantial aeration (high O2R) increase the total operating costs relative to OUR, and has been minimized here to focus on the economic trade-offs of scale.  
  
The economics of scale appear to show a fairly sizable advantage in favor of BCR technology. Beyond the physical limitations studied, BCR reactors are always less expensive to operate than STRs of the same size: with values ranging ~ 10-20% reduction in $/kg O2 by use of a BCR over a STR (Fig. 3c), suggesting the diminishing economies of scale are unlikely to justify discontinuing such a large unit.  
  
The above observation that O2 delivery is more cost-efficient at higher OUR has implications for the production of high-volume commodities like bulk chemicals and biofuels where extreme cost minimization is essential for techno-economic viability. For example, to make the most efficient use of fermentor capital equipment, it is important to be able to obtain and maintain a high volumetric productivity during the production phase of the target process.  
  
Fig. 3. (a) Specific total power demand, (b) specific aggregate capital and operating cost and (c) annual aggregate capital and operating cost to deliver oxygen in STR and BCR processes as a function of OUR.

---

## Page 6



---

