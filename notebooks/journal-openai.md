## Page 1

# Aeration costs in stirred-tank and bubble column bioreactors  
  
**D. Humbird\*, R. Davis\*, J.D. McMillan\***    
* D HWI Process Consulting LLC, Centennial, CO, United States    
* National Renewable Energy Laboratory, Golden, CO, United States  
  
## A R T I C L E   I N F O  
  
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
  
## A B S T R A C T  
  
To overcome knowledge gaps in the economics of large-scale aeration for production of commodity products, Aspen Plus is used to simulate steady-state oxygen delivery in both stirred-tank and bubble column bioreactors, using published engineering correlations for oxygen mass transfer as a function of aeration rate and power input, coupled with new equipment cost estimates developed in Aspen Capital Cost Estimator and validated against vendor quotations. These simulations describe the cost efficiency of oxygen delivery as a function of oxygen uptake rate and vessel size, and show that capital and operating costs for oxygen delivery drop considerably moving from standard-size (200 m³) to world-class size (500 m³) reactors, but only marginally in further scaling up to hypothetically large (1000 m³) reactors. This analysis suggests bubble-column reactor systems can reduce overall costs for oxygen delivery by 10–20% relative to stirred tanks at low to moderate oxygen transfer rates up to 150 mmol/L⋅h.  
  
---  
  
## 1. Introduction  
  
Since the development of penicillin production by submerged aerobic cultivation of *Penicillium chrysogenum*, aerobic biological production (“aerobic fermentation”) has been used to produce an increasing variety of chemical products [1]. The range of products being produced or considered for biological production has grown rapidly with recent advances in metabolic engineering, synthetic biology and bio-based production technologies [2,3]. Owing largely to the relatively high cost of supplying molecular oxygen (O₂) to a submerged culture, aerobic fermentation has historically primarily been applied to produce lower volume, higher value (higher margin) compounds like pharmaceuticals and specialty chemicals. The challenges to achieving commercial aerobic production become greater for larger volume, lower margin products where material and utility costs generally dominate fermentation economics [4]. The higher capital and operating costs for aerobic production are well recognized [5,6] and are also stimulating research and development on anaerobic routes for biological production [7,8]. Cost constraints become the most acute for economic aerobic production of extremely low-margin, high-volume commodity products like biofuels, and this motivated us to assess aeration costs for large-scale aerobic production in the context of such products.  
  
Aerobic fermentation is a critical unit operation in the process of making fuel-range hydrocarbons from sugars, when the hydrocarbon is our precursor, e.g., a lipid or free fatty acid, is directly produced in submerged culture by a microorganism. However, little bio-economic information exists about state-of-the-art designs and costs of large-scale aerobic bioprocesses, especially for those producing low-margin, commodity products like biofuels where time cost minimization is required. Previous techno-economic analysis (TEA) from the National Renewable Energy Laboratory (NREL) [9–11] demonstrated that, in the case of absolute ethanol, the fermentative production costs stemming mechanically from the overall large aerobic fermentation vessel (up to 10 gallons) was not a primary cost contributor, generally falling behind larger cost drivers including biomass pretreatment, enzyme production/purchase, and wastewater treatment. A more recent TEA report [12] examined the aerobic conversion of lignocellulosic sugars to hydrocarbons by way of a fatty acid intermediate. In contrast to the earlier analysis [12], concluded that the aerobic fermentation area was a primary cost contributor for integrated aerobic biofuel production; in fact, it was the largest contributor of all process areas, with fermentation compressors and agitators also representing the largest power demand in the biorefinery process.  
  
As the first publicly available TEA for such a technology pathway, the [12] analysis carried a higher degree of uncertainty in its underlying process design and capital cost assumptions than more established pathways. Among such uncertainties were the operating conditions, performance parameters, and cost contributions of the aerobic fermentation step. Parts of the process design were supported by a partner engineering company, which provided initial input on the design of stirred-tank aerobic bioreactors, and associated capital costs estimating. Since publication, this design has been reviewed by several engineering companies and consultants, including Harris Group, Katzen International, Benz Technologies, and Gevo.  
  
© 2017.

---

## Page 2

# Biochemical Engineering Journal xxx (2017) xxx–xxx  
  
matica. Following these critical reviews, it was concluded that several assumptions pertaining to the operational performance and capital costs used in [12] erred on the optimistic side for commercial-scale aerobic fermentation.  
  
This article documents efforts to reduce uncertainty in such key process and cost parameters through (1) development of an independent framework for bioreactor cost estimation that is validated against high-quality vendor quotes and (2) modeling of low-viscosity, aerobic fermentation using simple design equations and a steady-state process simulator, to understand achievable oxygen transfer rates as a function of vessel configuration, power input, and aeration rates. Together, the developments will be used to guide future refinements in conceptual design and TEA of biochemical conversion processes.  
  
## 2. Calculations  
  
### 2.1. Bioreactor capital cost estimation  
  
Ideally, well validated TEA studies should favor direct capital equipment inputs/quotations from equipment vendors, especially for critical and costly items like fermentors. However, external estimates are not always readily obtained for conceptual studies and can be scattered and sometimes conflicting. To facilitate rapid comparative analysis across multiple technology options, methods for cost estimation of bioreactor capital costs were developed using Aspen Capital Cost Estimator (ACCE). ACCE estimates costs for individual equipment items using volumetric models (as opposed to factored models), which compute total estimated materials and labor involved in manufacturing each equipment at a given scale. Equipment costs are then interpolated for capacity, with the addition of cost factors for shop fabrication of transportable pieces and costs for final field fabrication, all as part of a total bare equipment cost. A variety of high-quality bioreactor quotes obtained over recent years from vendors and engineering firms were used to create general guidelines for specifying fermentation vessels in ACCE, resulting in reasonably accurate, absolute capital cost predictions for both stirred-tank reactors (STRs) and bubble-column reactors (BCRs).  
  
With these specification guidelines, a set of capital costs for STRs and BCRs were developed at different standard vessel volumes. Economics of scale naturally dictate use of the largest reaction vessel possible; however, while million-gallon (3800 m³) anaerobic fermentors are in use at industrial fuel ethanol plants, the maximum practical aerobic reactor volume is less clear. Our industry contacts have intimated that the largest STRs in operation are in the hundreds of cubic meters (≤500 m³) and their ultimate maximum size must be on the order of 1000 m³, owing to diminishing returns on oxygen transfer relative to volumetric power input, as well as practical limitations regarding the fabrication and maintenance of very large impellers, shafts, bearings, and motors. Bubble columns are not limited by moving parts and BCRs up to 1000 m³ are known to be in operation [6]. Costs were therefore estimated for BCRs and STRs at three standard vessel sizes, with the understanding that uncertainty in costs increases with vessel size:  
  
- 200 m³, representing an “off-the-shelf,” readily purchasable reactor.  
- 500 m³, representing a world’s-largest class of reactor that exists in relatively small numbers.  
- 1000 m³, representing a “hypothetically large” reactor that does not exist today, representing a ceiling of what is likely viable from a design and operational standpoint.  
  
### 2.2. Flowshear simulation of aerobic fermentation  
  
To accompany the new standard bioreactor capital costs, we carried out steady-state flowsheet simulations in Aspen Plus to estimate the economics and resource costs associated with aerobic power demand. Fig. 1 shows a flow diagram of a single STR and support equipment. The flow diagram for a BCR is identical, except for elimination of the agitator.  
  
![Flow diagram of a single STR and support equipment. The flow diagram for a BCR is identical, except for elimination of the agitator.](path_to_image)  
  
*Pursuant to the DOE Public Access Plan, this document represents the authors' peer-reviewed, accepted manuscript. The published version of the article is available from the relevant publisher.*

---

## Page 3

determine the total system power demand for most of the users shown in Fig. 1: air compressor, air cooler, agitator for STRs, circulation pump, and chiller (also by cooling duty). The cooling tower was not included because its power contribution is insignificant compared to the chiller.  
  
The independent variable determining total system power was taken to be the oxygen uptake rate (OUR). In an operating bioreactor, the submerged culture provides some OUR, which, at steady-state, is equal to an oxygen transfer rate (OTR); the product of a mass transfer coefficient, k_L, a mean bubble specific interfacial surface area, a, and an oxygen concentration driving force, (C*−C_J):  
   
OUR = OTR = k_L a (C* − C_J)       (1)  
  
where k_L is usually lumped together and C* and C_J are respectively the equilibrium and the actual dissolved oxygen concentrations (mmol/L). For reactor design purposes, several literature correlations are available to relate k_L to fundamental operating parameters. In STRs, the non-viscous mass transfer correlation of [13] is frequently used as a design equation. This correlation describes k_L as a function of bioreactor gassed superficial power input (P) per unit volume (V) and the gas superficial velocity within the reactor, u_G:  
  
k_L a [s^−1] = 0.002 (P/V[m³] x m)²⁰ (u_G [m/s])⁰²  
  
where the pre-factor and exponents are adjustable for specific systems. This correlation is often relied on for its simplicity, as it does not depend on specific reactor geometry or impeller speed, number, and placement, unless other correlations are utilized for these parameters. In addition, STRs cannot be made to exceed more than 1.24 hr per fermentation [20].  
  
To be consistent, these simulations were run at steady state with stoichiometric glucose feed rate determined by OUR and vessel size. The reactor was modeled as a RSTIC reactor block with half vessel for roughness disengagement, CO₂ and water removed in the combustion contract removed with the water and liquid product stream. Air was supplied through a compressor which was rendered by the liquid head in the reactor. In these runs, the inlet air was 70% saturated to avoid a significant makeup flow due to evaporative stripping by the sparged air. The reactor block ran adiabatically with outlet temperature maintained at 32 °C by continuous pump-activated circulation of the liquid through a heat exchanger at a 20 °C outlet, as noted above, depending on the specific needs for a given production organism, for example, sterility or shear stress concerns, alarming needs for temperature control may be appropriate such as vessel jacketting. This cooling power must be included empirically for real situations to finalize results based on the mass flow rate of the liquid product and any heating needs due to product build-up, requiring estimations of 1.24 hr per fermentation time.  
  
It should be noted that BCRs are not normally recommended for fermentations where the broth viscosity is higher than 2 cp. We therefore limit our comparisons to non-viscous (aqueous) systems in the scope of this study.  
  
In aerobic cultures where molecular oxygen (O₂) is the primary electron acceptor at the end of the electron transport chain, it can be shown that the heat of reaction is proportional to the oxygen uptake rate, regardless of the actual effective stoichiometry or product of the culture [18]. Approximately 110 kJ of heat is released per g-mol O₂ consumed, which is equivalent to the heat of reaction (on an O₂ basis) of the process of conversion (C₆H₁₂O₆ + 6 O₂ → 6 CO₂ + 6 H₂O). Thus, rather than assume a specific biological system product in the Aspen Plus simulation, OUR is simply taken in this work in the liquid phase, in units of mmol O₂ consumed per liter per hour (mmol·L⁻¹·h⁻¹). For a given OUR, the simulation computed OTR from the aeration rate using Eq. (1) and the correlation for Eq. (3) (BCRs). The reactor block ran adiabatically with the air rate was then varied to set OTR equal to OUR. The STR correlation lends itself to power optimization between agitator power and gas superficial velocity (and compression); an optimization routine was used to vary these simultaneously to find the minimum total power for a given OUR. The BCR correlation cannot be similarly optimized, i.e., there is only a single u_G (and thus a single power) for a given OUR.  
  
Simulations were run at steady state with stoichiometric glucose feed rate determined by OUR and vessel size. The reactor was modeled as a RSTIC reactor block with half vessel for roughness disengagement, CO₂ and water removed in the combustion contract removed with the water and liquid product stream. Air was supplied through a compressor, which was rendered by the liquid head in the reactor. In these runs, the inlet air was 70% saturated to avoid a significant makeup flow due to evaporative stripping by the sparged air. The reactor block ran adiabatically with outlet temperature maintained at 32 °C by continuous pump-activated circulation of the liquid through a heat exchanger at a 20 °C outlet, as noted above, depending on the specific needs for a given production organism, for example, sterility or shear stress concerns, alarming needs for temperature control may be appropriate such as vessel jacketting. This cooling power must be included empirically for real situations to finalize results based on the mass flow rate of the liquid product and any heating needs due to product build-up, requiring estimations of 1.24 hr per fermentation.

---

## Page 4

3. Results and discussion  
  
3.1. Bioreactor capital costs  
  
Table 1 details four comparisons between vendor quotes obtained by NRBC and costs estimated with ACCE, for medium- to large-scale STRs and BCRs and one extremely large anaerobic thermal fermentor. Only costs for bare vessels (no agitators) are compared. The "vertical process vessel" item from the ACCE equipment library was used for BCRs and bare STRs. The million-gallon anaerobic fermentor was approximated with the "flat bottom storage tank" item, since it more closely resembles physical metallurgy and design pressures are key to cost estimation because ACCE computes vessel thickness (and therefore vessel weight) from these. In storage tanks, which ACCE assumes to be liquid-full, only the pad pressure is required. In process vessels, which are not full by default, an allowance should be added for head pressure at the vessel bottom. In esterifiable vessels, design for vacuum is required by code; this requires stiffening rings inside the vessel. In ACCE, these rings effectively seem the same cost at low vacuum and full vacuum. As seen in Table 1, from a limited number of details about a vessel, and some general specification guidelines, it is possible to achieve reasonable cost agreement with vendor quotes by correctly specifying an analogous vessel in ACCE.  
  
Using these guidelines, and a preference for 316 stainless steel, Table 2 presents costs for bare vessels in the standard sizes discussed in Section 2.1, along with relevant specifications provided to ACCE. Vessel perforations (e.g., nozzles and manholes) and their associated connection flanges can have a large effect on the vessel weight and therefore its cost, so these are presented as well. The STR costs in Table 2 do not include agitators. As the agitator power increases, however, the total reactor cost must increase as well, due to larger motors, gear boxes, and associated shipping infrastructure. ACCE captures this cost increase, as shown in Fig. 2, which presents the total costs of vessel and agitator for the three STR sizes in 316SS at motor powers from 10 to 2,500 hp. The ACCE "agitated tank-enclosed" equipment item was used to generate these costs.  
  
3.2. Total cost of aeration  
  
Fig. 3 shows the power required to deliver a kilogram of oxygen in STR and BCR systems for the three vessel sizes and OTR, which are required to achieve similar specific growth rates. The power requirement is nearly constant; this is part due to the optimization of agitation and aeration powers. Furthermore, the power required to achieve a given OTR does not change significantly with vessel size (the difference between 500 m³ and 1000 m³ is less than 5%). For BCRs, there is a more pronounced increase for gasping power input over the same OTR range, as OTR is only controlled by aeration and other  


---

## Page 5

![](https://www.example.com)    
**Biochemical Engineering Journal** xxx (2017) xxx-xxx    
5    
  
**Fig. 2.** Capital costs (uninstalled, 2014$) of STRs in 316SS as a function of agitator power.    
  
compression power is required for larger volumes of air. The power scales slightly more favorably with volume at higher OTR, with a 10% power reduction between 500 m³ and 1000 m³. In either case, for large reactors at a given OTR, the total bioreactor system power varies approximately linearly with total liquid volume. This implies that any beneficial economies of scale realized at larger vessel sizes are more strongly a result of reduced capital costs for the vessels and agitators than reduced operating costs resulting from differences in power demand or cost efficiency.    
  
To investigate the economies of scale possible for aeration, capital and operating costs were incorporated into this analysis. The bioreactor costs data were taken from ACCE as discussed above. For STRs, the overall installation factor of 2.3 was used to obtain a total cost of the reactors. Capital costs for compressors, pumps, and heat exchangers were also estimated with ACCE, though these were comparatively small compared to the reactor cost. The total capital cost was then converted to amortized capital costs ($/h) using a 13% annual capital charge factor and 8400 operating hours per year, consistent with NREL's case study methodologies, as e.g. illustrated in [12] and [10]. Operating costs were calculated as the sum of electricity at $0.06/kWh and maintenance at 0.6% of total installed capital. The resulting aggregate OPEX post amortized CAPEX costs were combined with the oxygen delivery rate required for each combination of OUR and vessel size, yielding a $/kg O2 cost, shown in Fig. 3b. This can be thought of as the total cost to deliver a kg of oxygen to a culture.    
  
For a single reactor and the associated equipment depicted in Fig. 1, Fig. 3 shows the same data plotted in terms of the total amortized cost required to operate the system in Fig. 1 (total cost of ownership), normalized by reactor volume (S∙yr⁻¹). Note that the cost of substrate (glucose) has not been included in Fig. 3b; substrate cost of course increases linearly with OUR, and has been omitted here to focus on the cost efficiency of O2 delivery, which is primarily a function of power.    
  
There are several conclusions to be drawn from the curves in Fig. 3c–f. First, as with the k₄ concept, both above and over the OUR range studied, BCRs are always less expensive to operate than STRs of the same size, with larger savings at lower OUR. Van't Riet (1991) reached an analogous conclusion in a similar analysis (see Example 18.3). Depending upon the cost metrics assessed, k₄ (supplying glucose) or S (γ) (Fig. 3c), use of BCRs reduces overall startup costs by 10–20% relative to STRs, assuming the process is suitable for implementing in a BCR. Second, for both reactor types there is a significant cost advantage in scaling up from 200 to 500 m³ and a rel-    
  
**Fig. 3.** (a) Specific total power delivery; (b) specific aggregate capital and operating cost (and annual aggregate capital and operating cost to deliver oxygen in STR and BCR systems at varying vessel volume and size).    
  
![](https://www.example.com)  

---

## Page 6

\documentclass{article}  
\begin{document}  
  
\section*{Biochemical Engineering Journal xxx (2017) xxx-xxx}  
  
product. For chemical or fuel precursors produced aerobically at high productivity, the OTR requirements can be significant. The techno-economic trends show here are encouraging, as they indicate that high-OTR processes are more cost-efficient. Nonetheless, substantial challenges remain to making biofuels cost effectively via aerobic routes [21].  
  
The trends established from the analysis and methodology performed here will help to define optimal operating conditions for future detailed models of aerobic processes, e.g., favoring BCRs over STRs where possible, and assessing bioreactor sizes of 500-1000 m³. For low-margin, commodity fuels and chemicals processes, BCRs are likely more cost-effective than STR vessels based both on the present analysis as well as feedback from industry. For processes not amenable to BCRs, an optimum STR design would likely be based on a 500 m³ vessel volume operating at an OTR above 50 mmol O₂/L. Although slight improvements may be seen going to larger volumes, such reactors would be larger than commercially available units today.  
  
\section*{4. Conclusions}  
  
Unfortunately in aerobic bioreactor capital and operating costs in the process design phase and TEA margins heavily leverage various biological parameters, including oxygen transfer requirements, are generally not firmly established at the time of analysis. The methods described here help to reduce the uncertainty evaluating bioreactor capital costs estimates against high-capital- vendor quotes and by using sensitivity analyses to assign quantitative uncertainty to estimates of the process efficiency of oxygen delivery in different vessel configurations. Vessel mentality and design pressure are the keys to maximizing performance while minimizing costs.   
  
These observations will inform future detailed models of aerobic production. As researchers in ARIEL and elsewhere continue to identify aerobic cultures and optimize their performance, a theory-based economic approach such as the one presented here can be used to guide research.  
  
\section*{Acknowledgments}  
  
This work was supported by the U.S. Department of Energy under Contract No. DEAC36-08GO28308 with the National Renewable Energy Laboratory. Funding provided by U.S. DOE Office of Energy Efficiency and Renewable Energy, Bioenergy Technologies Office (BETO). We thank our colleagues at Harris Group, Katzen International, Benz Technology, and Genomatica for their valuable inputs. The U.S. Government retains and the publisher, by accepting the article for publication, acknowledges that the U.S. Government retains a nonexclusive, paid-up, irrevocable, worldwide license to publish or reproduce the published form of this work, or allow others to do so, for U.S. Government purposes.  
  
\section*{References}  
  
[1] S. Abib, A.E. Humphrey, N. Millic, Biochemical Engineering, second edition, Academic Press, New York, 1973, (Chapter 1).  
  
[2] Aben, A., Ruth, M., Iben, K., Kehrun, J., Neeves, K., Shahan, J., Wallace, B., Montegut, L., Slayton, A., Jadun, P., 2002. Process Design Report for Source-Grade Lignocellulosic Biomass to Ethanol Process Design and Economics Utilizing Co-Current Dilute Acid Hydrolysis and Enzymatic Hydrolysis for Corn Stove Over. NREL/TP-510-32433. National Renewable Energy Lab. (NREL), Golden, CO (United States).  
  
[3] Biotechnology Innovation Organization (BIO), Advancing the Biobased Economy: Renewable Chemical Biorefinery Commercialization, Progress, and Market Opportunities, 2016 and Beyond, 2016.  
  
[4] J.R. Harrold, A. Bakker, L.R. Lynd, C.E. Wyman, Comparing the scale-up of aerobic and anaerobic biological processes, Adv. Biochem. Eng. Biotechnol. (2007). Abstract (abstract of presentation available at: http://www.baker. org/ publications/ATCH-2007-Hann.pdf).  
  
[5] Carter, F., Gallager, K., Jelinek, J. 2011. Comparison of Large-Scale Submerged Aerobic Cell Culture Process Design: Final Technical Report, NREL Subcontract Report NREL/SR-510-76963 (May 2011), Table 1, p. 16 and Table 2, p. 16. http:// www.ars.usda.gov/is/np/2/16076/).  
   
[6] R.W. Weusthuis, L. Jansen, J. van der Lugt, J.P.M. Smeenk, Microbial production of biochemicals: development of anaerobic processes, Trends Biotechnol. 29 (2011) 153–158.  
  
[7] HLF- (2003). A.S.J.A. van Mairs, S. Aishwarya J.L. Riemen, thermodynamics-based designs of microbial cell-factories for anaerobic product formation. Trends Biochem. Sci. 35 (2010) 534–546.  
  
[8] Aben, A., M. Iben, K. Ijeh, J. Kehrun, K. Neeves, K. Wallace, L. Montegut, A. Slayton, J. Lukas, Process Design Report for Source Feedstock: Lignocellulosic Biomass to Ethanol Process Design and Economics Utilizing Co-Current Dilute Acid Prehydrolysis and Enzymatic Hydrolysis for Corn Stover. NREL/TP-510-32483. National Renewable Energy Lab. (NREL), Golden, CO (United States).  
  
[9] Dimbah, R., Davis, T., Lazo, C., Kimbro, J., Dugan, P., Process Design and Economics (for renewable chemicals), in: G.P. Santa, J. P. S. Whelan, Integrated Biochemical and Enzymatic Hydrolius Processes for Corn Stover. NREL/ (87-820-1675), National Renewable Energy Lab. (NREL), Golden, CO (United States), 1997).  
  
[10] R. Davis, T., L.E.C.D. T.M. Biddy, E.F. Graciano, C. Scarlatti, J. Jackson, K. Caffrey, R.S. Lukas, J. Knorr, P. Schoon, Process Economics for the Conversion of Lignocellulosic Biomass to Butanol: Dilute-Acid and Enzymatic Deconstruction of Biomass to Sugars and Biological Conversion of Sugars to Hydrocarbons, NREL/TP-510-46203, National Renewable Energy Laboratory (NREL), Golden, CO, 2011.  
  
[11] K. Van’t Riet, J. Tramper, Basic Bioreactor Design, M. Dekker, New York, 1991.  
  
[12] A. Nennio, Stirred Bioreactor Engineering for Production Scale to Low-Viscosity Anaerobic Fermentations: Part 2, 2012.  
  
[13] F. Garciaboi, C.R., G. E. Gomer, Bioreactor scale-up and oxygen transfer rate in microbial processes: an overview, Biotechnol. Adv. 27 (2009) 135–176, https://doi. org/10.1016/j.biotechadv.2008.10.006.  
  
[14] N.M.G. Oosterhuis, N.V.F. Kossen, Dissolved oxygen concentration profiles in a production-scale bioreactor, Biotechnol. Bioengrg. 26 (1984) 546–550.  
  
[15] J.J. Heijnen, K. Van’t Riet, Mass transfer, mixing and heat transfer phenomena in high viscosity bubble column reactors, Chem. Eng. J. 28 (1984) 821–842, https://doi.org/10.1016/0300-9467(84)50225-4.  
  
[16] P. Doran, Bioprocess Engineering Principles, Academic Press, San Diego, Calif., 1995.  
  
[17] Handbook of Industrial Chemistry and Biotechnology, in: J.A. Kent (Ed.), Boston, MA: Springer US, 2012.  
  
[18] J.R. Cooper, W.P. Remner, J.R. Fart, S.M. Wals, Chemical Process Equipment: Selection and Design, Revised, 2nd ed., Elsevier, 2010.  
  
[19] J.D. McMillan, G.T. Bechtel, Thinking big: industrial strains and processes for large-scale aerobic biofuels production, Microb. Biotechnol. 10 (2017) 40–42.  
  
\end{document}

---

