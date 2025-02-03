## Page 1

# Aeration costs in stirred-tank and bubble column bioreactors  
  
**D. Humbird<sup>a</sup>, R. Davis<sup>b,*</sup>, J.D. McMillan<sup>b</sup>**  
  
<sup>a</sup>DWH Process Consulting LLC, Centennial, CO, United States  
<sup>b</sup>National Renewable Energy Laboratory, National Bioenergy Center, Golden, CO, United States  
  
  
**ARTICLE INFO**  
  
**Article history:**  
  
Received 21 February 2017  
Received in revised form 24 July 2017  
Accepted 6 August 2017  
Available online xxx  
  
**Keywords:**  
  
Aerobic fermentation  
Bioreactor design  
Capital cost  
Gas-liquid oxygen mass transfer  
  
**1. Introduction**  
  
Since the development of penicillin production by submerged aerobic cultivation of *Penicillium chrysogenum*, aerobic biological production ("aerobic fermentation") has been used to produce an increasing variety of chemical products [1]. The range of products being produced or considered for biological production has grown rapidly with recent advances in metabolic engineering, synthetic biology and bio-based production technologies [2,3]. Owing largely to the relatively high cost of supplying molecular oxygen (O<sub>2</sub>) to a submerged culture, aerobic fermentation has historically primarily been applied to produce lower volume, higher value (higher margin) compounds like pharmaceuticals and specialty chemicals. The challenges to achieving economical aerobic production become greater for larger volume, lower margin products where material and utility costs generally dominate fermentation economics [4]. The higher capital and operating costs for aerobic production are well recognized [5,6] and are also stimulating research and development on anaerobic routes for biological production. [7,8]. Cost constraints become the most acute for economic aerobic production of extremely low-margin, high-volume commodity products like biofuels, and this motivated us to assess aeration costs for large-scale aerobic production in the context of such products.  
  
Aerobic fermentation is a critical unit operation in the process of making fuel-range hydrocarbons from sugars, when the hydrocarbon or its precursor, e.g., a lipid or free fatty acid, is directly produced in submerged culture by a microorganism. However, little public domain information exists about state-of-the-art designs and economics of large-scale aerobic bioprocesses, especially for those producing low-margin, commodity products like biofuels where extreme cost minimization is required. Previous techno-economic analysis (TEA) reports from the National Renewable Energy Laboratory (NREL) [9–11] demonstrated that, in the case of cellulosic ethanol, the fermentation area (comprising mechanically simple but extremely large anaerobic fermentation vessels up to 10<sup>6</sup> gallons) was not a primary cost contributor, generally falling behind larger cost drivers including biomass pretreatment, cellulase enzyme production/purchase, and wastewater treatment. A more recent TEA report [12] examined the aerobic conversion of lignocellulosic sugars to hydrocarbons by way of a fatty acid intermediate. In contrast to the earlier ethanol analyses [12], concluded that the aerobic fermentation area was a primary cost contributor for integrated cellulosic biofuel production; in fact, it was the largest contributor of all process areas, with fermentation compressors and agitators also representing the largest power demand in the biorefinery process.  
  
As the first publicly available TEA for such a technology pathway, the [12] analysis carried a higher degree of uncertainty in its underlying process design and capital cost assumptions than more established pathway concepts. Key among such uncertainties were the operating conditions, performance parameters, and cost contributions of the aerobic fermentation step. Parts of the process design were supported by a partner engineering company, which provided initial input on the design of stirred-tank aerobic bioreactors, and associated capital cost estimates. Since publication, this design has been reviewed by several engineering companies and consultants, including Harris Group, Katzen International, Benz Technologies, and Geno-  
  
**ABSTRACT**  
  
To overcome knowledge gaps in the economics of large-scale aeration for production of commodity products, Aspen Plus is used to simulate steady-state oxygen delivery in both stirred-tank and bubble column bioreactors, using published engineering correlations for oxygen mass transfer as a function of aeration rate and power input, coupled with new equipment cost estimates developed in Aspen Capital Cost Estimator and validated against vendor quotations. These simulations describe the cost efficiency of oxygen delivery as a function of oxygen uptake rate and vessel size, and show that capital and operating costs for oxygen delivery drop considerably moving from standard-size (200 m<sup>3</sup>) to world-class size (500 m<sup>3</sup>) reactors, but only marginally in further scaling up to hypothetically large (1000 m<sup>3</sup>) reactors. This analysis suggests bubble-column reactor systems can reduce overall costs for oxygen delivery by 10–20% relative to stirred tanks at low to moderate oxygen transfer rates up to 150 mmol/L-h.  
  
© 2017.  
  
*Corresponding author.  
E-mail address: ryan.davis@nrel.gov (R. Davis)  
  
https://doi.org/10.1016/j.bej.2017.08.006  
1369-703/© 2017.  
  
Pursuant to the DOE Public Access Plan, this document represents the authors’ peer-reviewed, accepted manuscript. The published version of the article is available from the relevant publisher.  
  


---

## Page 2

2  
  
Biochemical Engineering Journal xxx (2017) xxx-xxx  
  
matica. Following these critical reviews, it was concluded that several assumptions pertaining to the operational performance and capital costs used in [12] erred on the optimistic side for commercial-scale aerobic fermentation.  
  
This article documents efforts to reduce uncertainty in such key process and cost parameters through (1) development of an independent framework for bioreactor cost estimation that is validated against high-quality vendor quotes and (2) modeling of low-viscosity, aerobic fermentation using simple design equations and a steady-state process simulator, to understand achievable oxygen transfer rates as a function of vessel configuration, power input, and aeration rates. Together, these developments will be used to guide future refinements in conceptual design and TEA of biochemical conversion processes.  
  
2. Calculations  
  
2.1. Bioreactor capital cost estimation  
  
Ideally, well validated TEA studies should favor direct capital equipment inputs/quotations from equipment vendors, especially for critical and costly items like fermentors. However, external estimates are not always readily obtained for conceptual studies and can be scattered and sometimes conflicting. To facilitate rapid comparative analysis across multiple technology options, methods for consistent estimation of bioreactor capital costs were developed using Aspen Capital Cost Estimator (ACCE). ACCE estimates costs for individual equipment items using volumetric models (as opposed to factored models), which compute total estimated materials and labor involved in building a piece of equipment based on its specified size. For example, if a specified vessel is too large or heavy to be transported in one piece (and all the vessels considered in this article are), ACCE will compute costs for shop fabrication of transportable pieces and costs for final field fabrication, all as part of a total bare equipment cost.  
  
A variety of high-quality bioreactor quotes obtained over recent years from vendors and engineering firms were used to create general guidelines for specifying fermentation vessels in ACCE, resulting in reasonably accurate, absolute capital cost predictions for both stirred-tank reactors (STRs) and bubble-column reactors (BCRs).  
  
With these specification guidelines, a set of capital costs for STRs and BCRs were developed at different standard vessel volumes. Economies of scale naturally dictate use of the largest reaction vessel possible; however, while million-gallon (3800 m³) anaerobic fermentors are in use at industrial fuel ethanol plants, the maximum practical aerobic reactor volume is less clear. Our industry contacts have intimated that the largest STRs in operation are in the hundreds of cubic meters (≤500 m³) and their ultimate maximum size must be on the order of 1000 m³, owing to diminishing returns on oxygen transfer relative to volumetric power input, as well as practical limitations regarding the fabrication and maintenance of very large impellers, shafts, bearings, and motors. Bubble columns are not limited by moving parts and BCRs up to 1000 m³ are known to be in operation [6]. Costs were therefore estimated for BCRs and STRs at three standard vessel sizes, with the understanding that uncertainty in cost increases with vessel size:  
  
•	200 m³, representing an "off-the-shelf," readily purchasable reactor.  
•	500 m³, representing a "world's-largest" class of reactor that exists in relatively small numbers.  
•	1000 m³, representing a "hypothetically large" reactor that may or may not exist today, representing a ceiling for what is likely viable from a design and operational standpoint.  
  
2.2. Flowsheet simulation of aerobic fermentation  
  
To accompany the new standard bioreactor capital costs, we carried out steady-state flowsheet simulations in Aspen Plus to investigate the operating costs associated with aeration power demand. Fig. 1 depicts the general bioreactor schematic considered here, equally applicable to STR or BCR vessels aside from the depicted agitator; a bioreactor is part of a complex of interacting energized systems, including an agitator (for STRs, eliminated for BCRs), an air compressor with discharge cooler, and a chilled-water system for temperature control, itself connected to a larger cooling water system. The system shown in Fig. 1 uses forced-circulation heat removal, but jackets or coils may be favored instead, depending on sterility and shear stress concerns. Aspen Plus simulations of STRs and similarly-equipped BCRs of 200, 500, and 1000 m³ were performed to  
  
Vent  
Substrate  
Air  
Air Compressor  
Product  
∞  
Air Cooler  
Cooling Tower  
1888  
STR  
Sparger  
Fermentation  
Chiller  
Circulation Pump  
Chilled Water System  
Fig. 1. Flow diagram of a single STR and support equipment. The flow diagram for a BCR is identical, except for elimination of the agitator.  
  
Pursuant to the DOE Public Access Plan, this document represents the authors' peer-reviewed, accepted manuscript.  
The published version of the article is available from the relevant publisher.  
  


---

## Page 3

Biochemical Engineering Journal xxx (2017) xxx-xxx  3  
  
determine the total system power demand for most of the users shown  
in Fig. 1: air compressor, air cooler, agitator for STRs, circulation  
pump, and chiller (scaled by cooling duty). The cooling tower was not  
included because its power contribution is insignificant compared to  
the chiller.  
  
The independent variable determining total system power was  
taken to be the oxygen uptake rate (OUR). In an operating bioreactor,  
the submerged culture provides some OUR, which, at steady-state, is  
equal to an oxygen transfer rate (OTR); the product of a mass transfer  
coefficient, k₁, a mean bubble specific interfacial surface area, a, and  
an oxygen concentration driving force, (C-C₁):  
  
OUR = OTR = k₁ a (C-C₁) (1)  
  
where k₁a is usually lumped together and C and C₁ are respec-  
tively the equilibrium and the actual dissolved oxygen concentrations  
(mmol/L). For reactor design purposes, several literature correlations  
are available to relate k₁a to fundamental operating parameters. In  
STRs, the non-viscous mass transfer correlation of [13] is frequently  
used as a design equation. This correlation describes k₁a as a function  
of bioreactor gassed power input (P) per unit volume (V) and the gas  
superficial velocity within the reactor, us:  
  
k₁a [s] = 0.002 (P/V [W/m³])⁰·⁷ (us [m/s])⁰·² (2)  
  
where the pre-factor and exponents are adjustable for specific sys-  
tems. This correlation is often relied on for its simplicity, as it does  
not depend on specific reactor geometry, or impeller speed, number,  
and type (though the accessible range of P/V is an implicit function of  
these [14]). The review of [15] lists other, more complex, correlations  
for k₁a, but notes that the original Van't Riet correlation (Eq. (2)) is  
the most frequently used for basic design in non-viscous systems. Re-  
actor sizes >100 m³ are out of the fit space for the original correlation,  
but [16] developed a zoned model where the correlation was applied  
independently to stirred and unstirred zones within a larger reactor,  
and concluded that in the limit of good mixing (1/k₁a > tmix), the cor-  
relation could be simply applied to the entire volume. In any event,  
well proven correlations like Eq. (2) can be used to determine ideal-  
ized scaled-up aerated bioreactor scenarios and make cost predictions.  
For BCRs, [17] proposed a similar correlation, with k₁a a primary  
function of the gas superficial velocity only. [13] further described  
how this correlation can be corrected for temperature, T, and effective  
broth viscosity, μeff resulting in:  
  
k₁a [s] = 0.32 (us [m/s])⁰·⁸⁴ (μeff [cP])⁰·⁸⁴ × 1.025⁽ᵀ⁻²⁰⁾ (3)  
  
It should be noted that BCRs are not normally recommended for  
fermentations where the broth viscosity is higher than 2 cp. We there-  
fore limit our comparisons to non-viscous (aqueous) systems in the  
scope of this study.  
  
In aerobic cultures where molecular oxygen (O₂) is the primary  
electron acceptor at the end of the electron transport chain, it can be  
shown that the heat of reaction is proportional to the oxygen uptake  
rate, regardless of the actual effective stoichiometry or products of  
the culture [18]. Approximately 110 kcal of heat is released per g-mol  
O₂ consumed, which is equivalent to the heat of reaction (on an O₂  
basis) of the glucose combustion reaction (C₆H₁₂O₆ + 6 O₂ → 6  
CO₂ + 6 H₂O). Thus, rather than assume a specific biological system/  
product in the Aspen Plus simulation, OUR is simply taken in this  
work to be a volumetric rate of combustion of glucose by oxygen,  
in the liquid phase, in units of mmol O₂ consumed per liter per hour  
(mmol/L-h). For a given OUR, the simulation computed OTR from  
the aeration rate using Eq. (1) and the correlation in Eq. (2) (STRs) or  
Eq. (3) (BCRs). The inlet air rate was then varied to set OTR equal to  
OUR. The STR correlation lends itself to power optimization between  
agitator power and gas superficial velocity (and compression); an op-  
timization routine was used to vary these simultaneously to find the  
minimum total power for a given OUR. The BCR correlation cannot  
be similarly optimized, i.e., there is only a single uₛ (and thus a single  
power) for a given OUR.  
  
Simulations were run at steady state with stoichiometric glucose  
feed rate determined by OUR and vessel size. The reactor was mod-  
eled as a RSTOIC reactor block with flash vessel for vapor/liquid dis-  
engagement. CO₂ and water formed in the combustion reaction were  
removed via the vent and liquid product streams. Air was supplied  
through a compressor with discharge pressure determined by the liq-  
uid head in the reactor, plus line losses. The inlet air was 70% satu-  
rated with water to avoid a significant makeup flow due to evaporative  
stripping by the sparged air. The reactor block ran adiabatically with  
outlet temperature maintained at 32 °C by continuous pump-around  
circulation of the liquid through a heat exchanger with a 20 °C outlet;  
as noted above, depending on the specific needs for a given produc-  
tion organism, e.g. regarding sterility or shear stress concerns, alterna-  
tive designs for temperature control may be appropriate such as vessel  
jacketing. This cooling loop removes all heat produced by the com-  
bustion reaction as well as (for STRs) the heat generated in dissipating  
agitator power (applied power less drive and bearing inefficiencies)  
[19]. The chiller duty was converted to power using a rule of thumb of  
1.24 hp/ton refrigeration [20].  
  
Due to the high circulation rate, both BCRs and STRs were as-  
sumed to be well-mixed and an overall concentration driving force  
was taken to be the log-mean average between the well-mixed O₂  
concentration and the Henry-saturated concentrations at the bottom  
and top of the reactor. This is an important limitation of the model;  
the steady-state, well-mixed, dissolved O₂ concentration is implicitly  
a function of OUR and thus cannot be set independently. In prac-  
tical batch or fed-batch bioreactor operation, aeration and agitation  
would be controlled along with substrate and nutrient feed rates to  
keep the dissolved O₂ concentration near zero, where mass transfer  
is most efficient. Moreover, in practice for a biological system, OUR  
may be highly variable over the course of a fermentation cycle be-  
tween cell-growth versus product (e.g. lipid) accumulation stages, fur-  
ther confounded by changing liquid levels in fed-batch operation; such  
variables are not part of the intended focus of this paper which mod-  
els a fixed-volume batch operation with all solubilized oxygen con-  
verted via a generic combustion reaction. Additionally, in a biologi-  
cal system with high OURs and also high vessel fill levels, flooding  
of liquid out the vent could become a concern, which would need to  
be addressed through appropriate maximum fill thresholds (minimum  
vessel headspace) and/or antifoam agents (again, beyond the scope of  
this analysis, where all cases assumed a fixed 80% ungassed working  
volume). A dynamic model (in preparation) will permit more sophisti-  
cated study of these issues and associated economics; the steady-state  
model, however, affords strong conclusions about conceptual process  
configuration and bioreactor selection.  
  
Pursuant to the DOE Public Access Plan, this document represents the authors' peer-reviewed, accepted manuscript.  
The published version of the article is available from the relevant publisher.  
  


---

## Page 4

# 3. Results and discussion  
  
## 3.1. Bioreactor capital costs  
  
Table 1 details four comparisons between vendor quotes obtained by NREL and costs estimated with ACCE, for medium- to large-scale STRs and BCRs and one extremely large anaerobic ethanol fermentor. Only costs for bare vessels (no agitators) are compared. The "vertical process vessel" item from the ACCE equipment library was used for BCRs and bare STRs. The million-gallon anaerobic fermentor was approximated with the "flat bottom storage tank" item, which it more closely resembles physically. Metallurgy and design pressures are key to cost estimation because ACCE computes vessel thickness (and therefore vessel weight) from these. In storage tanks, which ACCE assumes to be liquid-full, only the pad pressure is required. In process vessels, which are not full by default, an allowance should be added for head pressure at the vessel bottom. In steam-sterilizable vessels, design for vacuum is required by code; this requires stiffening rings inside the vessel. In ACCE, these rings add essentially the same cost at low vacuum and full vacuum. As seen in Table 1, from a limited number of details about a vessel, and some general specification guidelines, it is thus possible to achieve reasonable cost agreement with vendor quotes by correctly specifying an analogous vessel in ACCE.  
  
Using these guidelines, and a preference for 316 stainless steel, Table 2 presents costs for bare vessels in the standard sizes discussed in Section 2.1, along with relevant specifications provided to ACCE. Vessel perforations (e.g., nozzles and manholes) and their associated connection flanges can have a large effect on the vessel weight and therefore its cost, so these are presented as well. The STR costs in Table 2 do not include agitators. As the agitator power increases, however, the total reactor cost must increase as well, due to larger motors, gear boxes, and associated stabilizing infrastructure. ACCE captures this cost increase, as shown in Fig. 2, which presents the total costs of vessel and agitator for the three STR sizes in 316SS at motor powers from 10 to 2,500 hp. The ACCE "agitated tank-enclosed" equipment item was used to generate these costs.  
  
## 3.2. Total cost of aeration  
  
Fig. 3a shows the power required to deliver a kilogram of oxygen in STR and BCR systems for the three vessel sizes and OURs ranging from 10 to 150 mmol O2/L-h. (BCRs are generally not considered above 150 mmol/L-h, due to jet flooding at high gas velocity.) For STRs, Fig. 3a indicates that the specific O₂ delivery power is nearly constant; this is in part due to the optimization of agitation and aeration powers. Furthermore, the power required to achieve a given OTR does not change significantly with vessel size (the difference between 500 m³ and 1000 m³ is less than 5%). For BCRs, there is a more pronounced increase for gassing power input over the same OTR range, as OTR is only controlled by aeration rate and higher  
  
<br>  
  
Table 1  
  
Comparison of bioreactor cost quotes obtained from vendor/EPCs and costs estimated with ACCE (2014$).  
  
| Description | Quoted Specs | Quote | ACCE Specs | ACCE cost |  
|---|---|---|---|---|  
| 1 MMgal anaerobic fermentor (bare vessel) | 304SS shell 556 diam. X 534 height Atmospheric pressure | $907,000 | Storage tank, cone roof 304SS shell 554 diam. X 534 height 5 psig | $911,000 |  
| 200 m³ STR (bare vessel) | 304SS shell 15é diam. X 40 height -0.5 to 1 psig | $356,000 | Vertical process vessel 304SS shell 15é diam. X 40 height Vacuum to 45 psig | $383,000 |  
| 300 m³ STR (bare vessel) | 316SS shell 300 m³, 2.7:1 H/D Atmospheric pressure Internal cooling coil | $442,000 | Vertical process vessel 316SS shell 17é diam. X 45.5¢ height 0-45 psig +20% allowance for internals | $440,000 |  
| 670 m² BCR | 316SS shell 670 m², 6:1 H/D Vacuum to 45 psig Jacketed | $1,900,000 | Vertical process vessel 316SS shell 17 diam. X 100 height Vacuum to 45 psig Half-pipe jacket in A204C | $2,040,000 |  
  
  
<br>  
  
Table 2  
  
Vessel specifications and capital costs for STRs and BCRs estimated with ACCE (2014$).  
  
|  | STR | BCR |  
|---|---|---|  
| Nominal Volume | 200 m³ | 500 m³ | 1000 m³ | 200 m³ | 500 m³ | 1000 m³ |  
| Shell material | 316SS | 316SS | 316SS | 316SS | 316SS | 316SS |  
| Vessel Diameter | 15 ft. | 21 ft. | 26 ft. | 11.5 ft. | 15.5 ft. | 20 ft. |  
| Vessel T-T | 40 ft. | 51 ft. | 66.5 ft. | 69 ft. | 93 ft. | 120 ft. |  
| Skirt height | 8 ft. | 10 ft. | 13 ft. | 5 ft. | 8 ft. | 10 ft. |  
| Design pressure | 45 psig | 45 psig | 45 psig | 45 psig | 45 psig | 45 psig |  
| Design vacuum | full | full | full | full | full | full |  
| Design temp | 250 °F | 250 °F | 250 °F | 250 °F | 250 °F | 250 °F |  
| Agitator power | 10-2500 hp | 10-2500 hp | 10-2500 hp | – | – | – |  
| Impellers | 3 x 5.5 ft. | 3 × 8 ft. | 3 x 8.5 ft. | – | – | – |  
| Perforations |  |  |  |  |  |  |  
| Air inlet | 1 x 10 in. | 1 x 10 in. | 1 x 10 in. | 1 x 16 in. | 1 x 16 in. | 1 x 16 in. |  
| Drain | 1 x 12 in. | 1 x 20 in. | 1 x 24 in. | 1 x 8 in. | 1 x 12 in. | 1 x 24 in. |  
| Fill/cire return | 1 x 10 in. | 1 x 16 in. | 1 x 20 in. | 1 x 8 in. | 1 x 12 in. | 1 x 20 in. |  
| CIP | 2 x 10 in. | 2 x 10 in. | 2 x 10 in. | 2 x 10 in. | 2 x 10 in. | 2 x 10 in. |  
| Antifoam | 2 x 6 in. | 2 x 6 in. | 2 x 6 in. | 2 x 6 in. | 2 x 6 in. | 2 x 6 in. |  
| Vent | 1 x 10 in. | 1 x 16 in. | 1 x 20 in. | 1 x 10 in. | 1 x 16 in. | 1 x 20 in. |  
| Level | 1 x 3 in. | 1 x 3 in. | 1 x 3 in. | 1 x 3 in. | 1 x 3 in. | 1 x 3 in. |  
| Probe | 1 x 2 in. | 1 x 2 in. | 1 x 2 in. | 1 x 2 in. | 1 x 2 in. | 1 x 2 in. |  
| Relief | 4 x 8 in. | 4 x 12 in. | 4 x 16 in. | 4 x 8 in. | 4 x 12 in. | 4 x 16 in. |  
| Manhole | 2 x 20 in. | 2 x 20 in. | 2 x 20 in. | 2 x 20 in. | 2 x 20 in. | 2 x 20 in. |  
| ACCE Cost | $442,000 | $974,000 | $1,631,000 | $412,000 | $905,000 | $1,691,000 |  
  
Pursuant to the DOE Public Access Plan, this document represents the authors' peer-reviewed, accepted manuscript.  
The published version of the article is available from the relevant publisher.  
  


---

## Page 5

# Biochemical Engineering Journal xxx (2017) xxx-xxx  
  
5  
  
## Vessel+agitator capital cost ($MM)  
  
$3.0  
  
$2.5  
  
$2.0  
  
1,000 m³  
  
$1.5  
  
500 m³  
  
$1.0  
  
200 m³  
  
$0.5  
  
$0.0  
  
0  
  
500 1000 1500 2000 2500  
  
**Agitator power (hp)**  
  
**Fig. 2.** Capital costs (uninstalled, 2014$) of STRs in 316SS as a function of agitator  
power.  
  
compression power is required for larger volumes of air. The power  
scales slightly more favorably with volume at higher OTR, with a 10%  
power reduction between 500 m³ and 1000 m³. In either case, for large  
reactors at a given OTR, the total bioreactor system power varies ap-  
proximately linearly with total liquid volume. This implies that any  
beneficial economies of scale realized at larger vessel sizes are more  
strongly a result of reduced capital costs for the vessels and agitators  
than reduced operating costs resulting from differences in power de-  
mand or cost efficiency.  
  
To investigate the economies of scale possible for aeration, capital  
and operating costs were incorporated into the analysis. The bioreactor  
capital costs were taken from ACCE as discussed above. For STRS,  
these were obtained from Fig. 2 as a function of optimized agitator  
power. A fixed installation factor of 2.3 was used to obtain a total di-  
rect cost for the bioreactors. Capital costs for compressors, pumps, and  
heat exchangers were also estimated with ACCE, though these were  
generally small compared to the reactor cost. The total capital cost  
was then converted to an amortized fixed cost ($/h) using a 13% an-  
nual capital charge factor and 8400 operating hours per year, consis-  
tent with NREL's cash flow calculation methodologies, e.g., as pub-  
lished in [12] and [10]. Operating costs were calculated as the sum of  
electricity at $0.06/kWh and maintenance at 6% of total installed cap-  
ital. The resulting aggregate OPEX plus amortized CAPEX costs were  
combined with the oxygen delivery rate required for each combination  
of OUR and vessel size, yielding a $/kg O₂ cost, shown in Fig. 3b.  
This can be thought of as the total cost to deliver a kg of oxygen to a  
culture, for a single reactor and the associated equipment depicted in  
Fig. 1. Fig. 3c shows the same data plotted in terms of the total annual  
cost required to operate the system in Fig. 1 (total cost of ownership),  
normalized by reactor volume ($/y-m³). Note that the cost of substrate  
(glucose) has not been included in Fig. 3b-c; substrate cost of course  
increases linearly with OUR, and has been omitted here to focus on the  
cost efficiency of O₂ delivery, which is primarily a function of power.  
  
There are several conclusions to be drawn from the curves in Fig.  
3b-c. First, with the k₁a correlations used and over the OUR range  
studied, BCRs are always less expensive to operate than STRs of  
the same size, with larger savings at lower OUR. Van't Riet (1991)  
reached an analogous conclusion in a similar analysis (see Example  
18.3). Depending upon the cost metric assessed, $/kg O₂ supplied (Fig.  
3b) or $/y-m³ (Fig. 3c), use of BCRs reduces overall aeration costs  
by 10-20% relative to STRs, assuming the process is suitable for im-  
plementing in a BCR. Second, for both reactor types there is a sig-  
nificant cost advantage in scaling up from 200 to 500 m³ and a rel-  
  
  
## Power to deliver oxygen  
**(kWh/kg O₂)**  
  
2.0  
  
1.5  
  
1.0  
  
0.5  
  
**(a)**  
  
0.0  
  
0 25 50 75 100 125 150  
  
**OUR (mmol/L-h)**  
  
  
## Cost to deliver oxygen  
**($/kg O₂)**  
  
$0.80  
  
$0.60  
  
$0.40  
  
$0.20  
  
$0.00  
  
**(b)**  
  
0 25 50 75 100 125 150  
  
**OUR (mmol/L-h)**  
  
  
## Annual cost of ownership  
**($/y-m³)**  
  
$8000  
  
$6000  
  
$4000  
  
$2000  
  
0  
  
0 25 50 75 100 125 150  
  
**OUR (mmol/L-h)**  
  
**(c)**  
  
STR 200 m³  
STR 500 m³  
STR 1,000 m³  
BCR 200 m³  
BCR 500 m³  
BCR 1,000 m³  
  
**Fig. 3.** (a) Specific total power demand, (b) specific aggregate capital and operating cost  
and (c) annual aggregate capital and operating cost to deliver oxygen in STR and BCR  
systems at varying vessel volume and OUR.  
  
atively smaller advantage in further scaling up from 500 to 1000 m³.  
This effect may be larger in the context of a whole-plant analysis,  
since the aggregate costs in Fig. 3b-c do not include manpower,  
which should naturally decrease with a smaller number of larger re-  
actors. Third, specific oxygen delivery cost flattens out near an OTR  
of roughly 50-75 mmol/L-h, for all reactors, indicating that the cost  
efficiency of delivering O₂ is better at higher OTR up to this limit. Fi-  
nally, Fig. 3b indicates there is likely little incentive to make a biore-  
actor larger than 1000 m³. Beyond the physical limitations discussed  
earlier, the diminishing economies of scale are unlikely to justify de-  
velopment of such a large unit.  
  
The above observation that O₂ delivery is more cost-efficient at  
moderate to high OTR has implications for the production of high-vol-  
ume commodities like bulk chemicals and biofuels where extreme  
cost minimization is essential for techno-economic viability. For ex-  
ample, to make the most efficient use of fermentor capital equip-  
ment, it is important to be able to obtain and maintain a high vol-  
umetric productivity during the production phase of the target  
  
Pursuant to the DOE Public Access Plan, this document represents the authors' peer-reviewed, accepted manuscript.  
The published version of the article is available from the relevant publisher.  
  


---

## Page 6

6  
  
Biochemical Engineering Journal xxx (2017) xxx-xxx  
  
product. For chemical or fuel precursors produced aerobically at high  
productivity, the OTR requirements can be significant. The  
techno-economic trends shown here are encouraging, as they indicate  
that higher-OTR processes are more cost-efficient. Nonetheless, sub-  
stantial challenges remain to making biofuels cost effectively via aer-  
obic routes [21].  
  
The trends established from the analysis and methodology pre-  
sented here will help to define optimal operating conditions for fu-  
ture detailed models of aerobic processes, e.g., favoring BCRs over  
STRs where possible, and assuming bioreactor sizes of 500-1000 m³.  
For low-margin, commodity fuels and chemicals processes, BCRs are  
likely more cost-effective than STR vessels based both on the pre-  
sent analysis as well as feedback from industry. For processes not  
amenable to BCRs, an optimum STR design would likely be based on  
a 500 m³ vessel volume operating at an OTR above 50 mmol/L-h. Al-  
though slight cost improvements may be seen going to larger volumes,  
such reactors would be larger than commercially available units today.  
  
4. Conclusions  
  
Uncertainty in aerobic bioreactor capital and operating costs in  
conceptual process design and TEA remains largely inevitable as  
many biological parameters, including oxygen transfer requirements,  
are generally not firmly established at the time of analysis. The meth-  
ods described here help to reduce uncertainty by validating software  
capital cost estimates against high-quality vendor quotes and by us-  
ing simple design equations in a steady-state process simulator to as-  
sess the cost efficiency of oxygen delivery in different vessel config-  
urations. Vessel metallurgy and design pressure are the keys to ac-  
curate cost estimation, and significant cost efficiencies can be real-  
ized by favoring BCRs over STRs, at a maximum bioreactor size of  
500-1000 m³ and OTR between 50 and 150 mmol/L-h.  
  
These observations will inform future detailed models of aerobic  
production. As researchers at NREL and elsewhere continue to iden-  
tify aerobic cultures and optimize their performance, a theory-based  
economics approach such as the one presented here can be used to  
guide research.  
  
Acknowledgements  
  
This work was supported by the U.S. Department of Energy un-  
der Contract No. DEAC36-08GO28308 with the National Renew-  
able Energy Laboratory. Funding provided by U.S. DOE Office of  
Energy Efficiency and Renewable Energy, Bioenergy Technologies  
Office (BETO). We thank our colleagues at Harris Group, Katzen  
International, Benz Technologies, and Genomatica for their valuable  
inputs. The U.S. Government retains and the publisher, by accepting  
the article for publication, acknowledges that the U.S. Government re-  
tains a nonexclusive, paid-up, irrevocable, worldwide license to pub-  
lish or reproduce the published form of this work, or allow others to  
do so, for U.S. Government purposes.  
  
References  
  
[1] S. Aiba, A.E. Humphrey, N. Millis, Biochemical Engineering, second edition,  
Academic Press, New York, 1973, (Chapter 1).  
  
[2] Aden A., Ruth M., Ibsen K., Jechura J., Neeves K., Sheehan J., Wallace B.,  
Montague L., Slayton A., Lukas J., 2002. Process Design Report for Stover  
Feedstock: Lignocellulosic Biomass to Ethanol Process Design and Economics  
Utilizing Co-Current Dilute Acid Prehydrolysis and Enzymatic Hydrolysis for  
Corn Stover (No. NREL/TP-510-32438). National Renewable Energy Lab.  
(NREL), Golden, CO (United States).  
  
[3] Biotechnology Innovation Organization (BIO), Advancing the Biobased Econ-  
omy: Renewable Chemical Biorefinery Commercialization, Progress, and Mar-  
ket Opportunities, 2016 and Beyond, 2016.  
  
[4] J. Van Brunt, Fermentation economics, Nat. Biotechnol. 4 (1986) 395-401.  
  
[5] J.R. Hannon, A. Bakker, L.R. Lynd, C.E. Wyman, Comparing the scale-up of  
aerobic and anaerobic biological processes, 2007 AIChE Annual Meeting  
(2007), Abstract (Handout of presentation available at: http://www.bakker.org/  
cfm/publications/AIChE-2007-Hannon.pdf).  
  
[6] Crater J., Galleher C., Lievense J. 2017. Consultancy on Large-Scale Submerged  
Aerobic Cultivation Process Design-Final Technical Report, NREL Subcontract  
Report NREL/SR-5100-67963 (May 2017), Table 1, , p6 and Table 2, p16. http://  
www.nrel.gov/docs/fy17osti/67963.pdf.  
  
[7] R.A. Weusthuis, I. Lamot, J. van der Oost, J.P.M. Sanders, Microbial production  
of bulk chemicals: development of anaerobic processes, Trends Biotechnol.  
29 (2011) 153-158.  
  
[8] H.F. Cueto-Rojas, A.J.A. van Maris, S. Aljoscha Wahl, J.J. Heijnen, Thermody-  
namics-based design of microbial cell factories for anaerobic product formation,  
Trends Biotechnol. 33 (2015) 534-546.  
  
[9] A. Aden, M. Ruth, K. Ibsen, J. Jechura, K. Neeves, J. Sheehan, B. Wallace, L.  
Montague, A. Slayton, J. Lukas, Process Design Report for Stover Feedstock:  
Lignocellulosic Biomass to Ethanol Process Design and Economics Utilizing  
Co-Current Dilute Acid Prehydrolysis and Enzymatic Hydrolysis for Corn  
Stover (No. NREL/TP--510-32438), National Renewable Energy Lab. (NREL),  
Golden, CO (United States), 2002.  
  
[10] D. Humbird, R. Davis, L. Tao, C. Kinchin, D. Hsu, A. Aden, P. Schoen, J.  
Lukas, B. Olthof, M. Worley, D. Sexton, D. Dudgeon, Process Design and Eco-  
nomics for Biochemical Conversion of Lignocellulosic Biomass to Ethanol: Di-  
lute-Acid Pretreatment and Enzymatic Hydrolysis of Corn Stover (No. NREL/  
TP-5100-47764), National Renewable Energy Laboratory (NREL), Golden, CO,  
2011.  
  
[11] R. Wooley, M. Ruth, J. Sheehan, K. Ibsen, H. Majdeski, A. Galves, Process De-  
sign Report for Wood Feedstock: Lignocellulosic Biomass to Ethanol Process  
Desing and Economics Utilizing Co-Current Dilute Acid Prehydrolysis and En-  
zymatic Hydrolysis Current and Futuristic Scenarios (No. NREL/  
TP--580-26157), National Renewable Energy Lab. (NREL), Golden, CO (United  
States), 1999.  
  
[12] R. Davis, L. Tao, E.C.D. Tan, M.J. Biddy, G.T. Beckham, C. Scarlata, J. Jacob-  
son, K. Cafferty, J. Ross, J. Lukas, D. Knorr, P. Schoen, Process Design and  
Economics for the Conversion of Lignocellulosic Biomass to Hydrocarbons: Di-  
lute-Acid and Enzymatic Deconstruction of Biomass to Sugars and Biological  
Conversion of Sugars to Hydrocarbons (No. NREL/TP-5100-60223), National  
Renewable Energy Laboratory (NREL), Golden, CO, 2013.  
  
[13] K. Van't Riet, J. Tramper, Basic Bioreactor Design, M. Dekker, New York,  
1991.  
  
[14] A. Nienow, Stirred Bioreactor Engineering for Production Scale Low Viscosity  
Aerobic Fermentations: Part 2, 2012.  
  
[15] F. Garcia-Ochoa, E. Gomez, Bioreactor scale-up and oxygen transfer rate in mi-  
crobial processes: an overview, Biotechnol. Adv. 27 (2009) 153-176, https://doi.  
org/10.1016/j.biotechadv.2008.10.006.  
  
[16] N.M.G. Oosterhuis, N.W.F. Kossen, Dissolved oxygen concentration profiles in  
a production-scale bioreactor, Biotechnol. Bioenergy. 26 (1984) 546-550.  
  
[17] J.J. Heijnen, K. Van't Riet, Mass transfer, mixing and heat transfer phenomena  
in low viscosity bubble column reactors, Chem. Eng. J. 28 (1984) B21-B42,  
https://doi.org/10.1016/0300-9467(84)85025-x.  
  
[18] P. Doran, Bioprocess Engineering Principles, Academic Press, San Diego, Calif,  
1995.  
  
[19] Handbook of Industrial Chemistry and Biotechnology, in: J.A. Kent (Ed.),  
Boston, MA, Springer US, 2012.  
  
[20] J.R. Couper, W.R. Penney, J.R. Fair, S.M. Walas, Chemical Process Equipment:  
Selection and Design, Revised, 2nd ed., Elsevier, 2010.  
  
[21] J.D. McMillan, G.T. Beckham, Thinking big: towards ideal strains and processes  
for large-scale aerobic biofuels production, Microb. Biotechnol. 10 (2017)  
40-42.  
  
Pursuant to the DOE Public Access Plan, this document represents the authors' peer-reviewed, accepted manuscript.  
The published version of the article is available from the relevant publisher.  


---

