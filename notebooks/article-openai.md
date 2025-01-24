## Page 1

Reactions and Separations  
  
# Optimize Power Consumption in Aerobic Fermenters  
  
**GREGORY T. BENZ**    
Benz Technology International, Inc.  
  
By performing the necessary pilot work, and rigorously calculating the full-scale performance instead of using simple rules-of-thumb for scale-up, significant energy savings can be achieved in fermenters.  
  
---  
  
AEROBIC FERMENTATION WAS PUT TO commercial use in the 1940s to make penicillin. Later, many other antibiotics were made via this method. Over the years, it has become a route to economically produce a variety of compounds, including enzymes, amino acids, vitamins, flavor enhancers, thickening and binding agents, and cleaning compounds. The list keeps growing.   
  
One reason for its widespread use is its specificity for producing compounds — that is, some species are difficult to make by other means, and other routes may produce high concentrations of byproducts. Another reason is that fermentation requires comparatively mild conditions, in terms of temperature, pressure and pH. This often allows for less-costly equipment and lower energy costs compared with using standard chemical synthesis. Still, few operating fermenters are designed to minimize their total operating power, which is used primarily by:  
- the agitator, which disperses air into the broth and provides for a reasonable level of compositional uniformity, and  
- the air-delivery system, which comprises a compressor, filter and associated piping.  
  
## Current practice  
  
Most aerobic fermenters are, in fact, designed using little data. Typically, engineers simply select equipment that has been found to be suitable for making similar products. Often, only a little or no pilot work is done. If these studies are undertaken, they are carried out to determine the ideal conditions for the organism, such as pH, temperature, and concentrations of dissolved oxygen (DO). Nutrients from the feed vs. feedstock consumption may also be investigated.  
  
However, little attention is given to collecting the data needed to predict the full-scale oxygen transfer and energy consumption. To make matters worse, the pilot conditions usually differ from those in the scale-up, commercial unit. Compared with commercial equipment, pilot units operate at a much higher agitator specific power (power/unit mass or volume) and a much lower superficial gas velocity (actual gas flow divided by the tank's cross-sectional area).  
  
Nonetheless, attempts are sometimes made to scale up from the limited pilot data. These can be based on using equal agitator power/volume, with the air flow scaled up using an equal volume of gas per volume of liquid per minute (VLM). When such a technique yields unreasonably large equipment, as it usually does, engineering judgment is employed to compensate for the increase in superficial gas velocity to preserve driving force in the full-scale equipment. However, such judgment carries some risk, since the relative contribution of agitation and air flow to mass transfer can vary considerably for different processes and different agitation systems.

---

## Page 2

# Correct pilot studies are the key  
To optimize full-scale energy consumption, it is necessary to quantitatively predict the relationship between mass-transfer rate, driving force, agitator power and super-ficial gas velocity (1). To obtain this relationship accurately, the pilot plant must be operated under the same range of conditions as will be found in the full-scale equipment. In practice, this means using much more air and much less agitation than is normal for pilot operation. To obtain the same superficial gas velocity in the pilot plant as in the production equipment, it is not unusual to need a VSM of 10–15/min, whereas the full-scale VSM may be 0.5–1.5/min. If the pilot facility does not have sufficient air available, then its air-delivery system must be beefed up. Otherwise, the correlations obtained will not be accurate. Data must be taken using an impeller system similar to the one that will be used in the full-scale fermenter. Although impeller system design is beyond the scope of this article, properly sized axial upper impellers combined with a lower concave radial impeller have been found to promote excellent liquid-phase DO uniformity. This arrangement has a high gas-handling ability and the difference in power draw between the ungassed and the gassed states is minimal.  
  
## Determining system parameters  
The defining equation for mass transfer in a fermenter is:    
\[ OTR = k_La(C^{*} - C) \tag{1} \]  
  
The goal of the pilot study is to correlate k_La, the overall mass-transfer coefficient, to the agitation and airflow conditions. The correlation is ideally done around the point in the process where oxygen demand is at a maximum, and under similar levels of agitator specific power and superficial gas velocity. This correlation is established by using a simple exponential relationship:    
\[ k_La = a(PV)(U)_{j} \tag{2} \]  
  
The constants a, b and c are derived by empirically fitting the experimental data to the equation. With a clean  
  
## Nomenclature  
- \( a, b, c \) = empirical constants in Eq 2  
- \( C_{x} \) = dissolved oxygen concentration, mg/L  
- \( C_{x}^{*} \) = dissolved oxygen concentration at saturation, mg/L  
- \( b_{O} \) = dissolved oxygen concentration, mg/L  
- \( k_L \) = mass-transfer coefficient, s⁻¹ or hr⁻¹  
- \( OTR \) = oxygen transfer rate, mg-h/L  
- \( P_{V} \) = specific power, W/m³  
- \( U \) = superficial gas velocity, M/s  
- \( V_{M} \) = volume of gas per volume of liquid per minute, min⁻¹  
  
## Full-scale degrees of freedom  
It is possible to get the desired OTR in the full-scale equipment in a number of different ways. At low airflow rates, the gas superficial velocity will be low, so higher agitation power is needed to compensate for this, even to get an equal mass-transfer coefficient. Low gas flow also equates to more oxygen depletion in the exit gas, resulting in a reduced concentration-driving force, which further requires more agitation. In fact, there is a theoretical minimum airflow: that at which 100% of the oxygen in the air stream is required to meet the required OTR. In such a case, impractical levels of agitation would be required since the driving force would be small at the inlet and zero at the outlet. At higher airflow rates, the driving force and gas superficial velocity both increase, resulting in less agitator power being needed to achieve the same OTR. There is a practical maximum air flow as well. The author’s experience suggests that operation at superficial gas velocities above 0.6 m/s should be avoided, so as not to allow excessive reinvestment of the process liquid in the gas stream, which can range from a theoretical minimum to practical maximum, the compressor power requirements increase with airflow, but the required agitator power simultaneously decreases. The sum of the agitator and the compressor power will, in fact, push toward a minimum. It is the goal of this article to show how to operate as close to this minimum as possible.  
  
## Optimizing full-scale design  
The following steps should produce a system design that operates close to the minimum power requirement.  
1. Based on the peak OTR, calculate the minimum air flow required at 100% utilization.  
2. Choose an air flow that is greater than the theoretical minimum calculated in Step 1 for the first design calculation. Start out at about 20% above the minimum.  
3. Perform a mass balance and determine the exit gas flow rate and composition, including the amount of \( CO_{2} \) required.  
4. Calculate the driving force for mass transfer. For full-scale equipment, use a log-mean driving force, rather than the simple form given in Eq. 1. Accurate saturation data are needed.  


---

## Page 3

# Reactions and Separations  
  
**Step 5.** Calculate the required k_a.  
  
**Step 6.** Calculate the actual volumetric air flow at the midpoint of the unreacted broth height, being sure to account for temperature, composition, backpressure and liquid head. Use the average flowrates for the inlet and outlet.  
  
**Step 7.** Calculate the superficial gas velocity at the midpoint using the above gas flowrate.  
  
**Step 8.** Using the mass-transfer relationship developed from pilot scale data, solve for the agitator power. Add about 5% to account for the gear drive and seal losses to get the required motor power-draw.  
  
**Step 9.** Calculate compressor power. Include the backpressure, liquid head pressure, and losses from the sparger ring, piping and filtration systems. Also include the manufacturer’s compressor efficiency to calculate motor power-draw required (typically 50–80%). For an existing plant, these should be calculated based on the actual piping system. For a new plant optimization study, a simplifying assumption can be made: the piping system will be sized based on a certain maximum pressure drop at the final airflow chosen.  
  
**Step 10.** Calculate total power of the agitator and the compressor.  
  
**Step 11.** Repeat Steps 1–10 for an incremental air flow. An increment of 20% of the theoretical minimum is suggested.  
  
**Step 12.** Repeat Step 11 until a minimum total power is found. Add in safety factors to account for data error and reliability for future process changes.  
  
This procedure is primarily intended to allow optimization of the original installed compressor and agitator power. It can also be used in an existing fermenter to compute the optimum conditions during the batch cycle, which, of course, has a varying oxygen demand from beginning to end. If the agitator and agitator speed are both variable, then a control-logic sequence can be developed to minimize energy usage throughout the processing sequence.  
  
This procedure may seem to involve a lot of calculation time. Of course, once the system equations have been defined, they can be put into a computerized spreadsheet so repeated calculations will take little time. The potential reward can be significant. It is not unusual for a 150,000-L fermenter to operate at 100 kW or more away from the optimum condition. Assuming a typical plant has 10 such fermenters and the units run at full speed 50% of the year, the annual savings potential is about $350,000 at an electric power cost of $0.08/kWh. For designing a new system, such a determination will result in much lower capital costs, as well.  
  
## Example  
  
The figure on the right shows how the power consumption varies when this procedure is used. A simplifying assumption of constant gas pressure drop was made, as appropriate for new construction. The figure shows the compressor power, agitator power and total power as a function of air flow. Note that the beginning air flow used is close to the theoretical minimum, so the agitator power is rather high. There is a fairly broad band in which the required power is roughly constant. As long as the fermenter is designed in this range, it will be close to optimum. If an agitator impeller system is chosen that has most constant gassed power characteristics, then the agitator installed power can be fixed and airflow can be adjusted to the minimum that will provide the necessary DO level. This will allow for sufficient operating flexibility while keeping the capital and operating costs to a minimum. If the impeller system has a power draw that is sensitive to airflow, it may be necessary to use a variable-speed drive on the agitator to achieve the desired result.  
  
## Sample Problem  
  
Suppose a production fermenter has a diameter of 3.66 m, a liquid volume of 114 m³, and an ungasified liquid height of 10.97 m. The broth has an unreacted specific gravity of 1.0. The temperature is 38°C. At 1 atm, the saturation value of DO is 7.0 mg/L, based on air that is not enriched with oxygen. When oxygen is fed into the broth, 95% of it is returned as respired carbon dioxide. The consumption rate or OTR is 2,000 gmol/h. Minimum desired oxygen concentration in the broth is 2 mg/L. The fermenter will be operated at a gauge backpressure of 0.683 atm. Line losses from the sparger to the vessel will be 2.04 atm. Assume a 95% mechanical efficiency for the agitator and 70% for the compressor. The step-by-step optimization procedure is as follows:  
  
**Step 1.** Total OTR required is 2,000 mL/h x 114,000 L = 228 x 10⁶ mg/O₂/h = 1,125 mg/mol. One at normal conditions (0°C and 1 atm) contains 44.6 g/mol. Air at 21°C, O₂ contains 9.366 g of O₂/M³, so the air flowrate is 15,729.5/9.366 = 760.7 m³/h, or 12.68 m³/min.  
  
Figure. To optimize power consumption, the fermenter must be designed in the range where power consumption is roughly constant. In this example, the power consumption is relatively constant for a broad range.

---

## Page 4

Step 2. Normally, the iteration process would start with 20% higher airflow than the above value, but for illustration purposes, only one iteration is needed. Therefore, the flow rate above value is used (vs. 1.20 times the flowrate), which is 25 M³/min.   
  
Step 3. Perform the mass balance. The inlet airflow for 25 M³/min contains a total of 1,115 gmol/s, of which 234.2 are O₂, and the balance, 880.8 gmol, is other gases; which will be carried through the fermenter unchanged, 7.15 gmol/h, or 118.8 gmol/h O₂ consumed, leaving 115.4 gmol/min of O₂ in the outlet gas. In addition, CO₂ is generated at the rate of 112.8 gmol/min (95% of the value of oxygen consumed). So, the outlet gas rate is 1,109 gmol/min with 10.4% CO₂. This corresponds to a gas flow at the outlet of 24.9 M³/min.   
  
Step 4. To calculate the driving force, we need to know the absolute pressure and concentration of the air stream at the top and bottom, as well as the DO concentration in the broth at the top and bottom. The bottom pressure equals the backpressure plus liquid head: 0.68 atm + 1 atm (gage pressure) + 1.06 atm (1097 kg liquid head at 1.0 S.G.) = 2.74 atm abs. Since the saturation value at 1 atm and 21% O₂ is mg/L, the saturation concentration at the outlet of the fermenter is Y = 2.74, or 19.18 mg/L.  
  
The pressure at the top is 1.68 atm (abs.), and the concentration of O₂ is 10.46%, so saturation concentration is mg/L x 1.68 x (10.421) = 58.27 mg/L. Now that saturation values have been established, calculate the driving force. To this, the liquid DO concentrations must be known. It has been established that a minimum of 2 mg/L is needed for the fermenter to work effectively. However, since fermenters are not perfectly mixed, there will be a concentration gradient.  
  
The author has seen cases using multiple mini-pellers where DO varied from bottom to top by more than an order of magnitude. Therefore, for a combination of axial and radial impellers used in fermenters of this size, the DO at the bottom will be about 50% higher than at the top. Using this basis, assigning a value of 2 mg/L at the top and 3 mg/L at the bottom. The log-mean driving force is equal to [(58.27 - 19.81)/(ln(58.27/19.31)) = 8.56 mg/L.  
  
Step 5. The required kLa = OTR/driving force = (2,000 mg/L)/(8.56 mg/L) = 233.67 h⁻¹ or 0.06495.  
  
Step 6. The average molar flow of gas at the middle is (1,115 + 1,109) / 2 = 1,112 mg/min, or 24.93 M³/min. The absolute pressure at the midpoint equals the backpressure plus one-half of the liquid head, or 0.68 + 1 * 0.53 = 2.21 atm. The temperature is 293 K or 31.1 K. Based on ideal gas law adjustments, the actual gas flow is 24.93 x (1/2.213) = 12.85 M³/min.  
  
Step 7. Based on the tank diameter of 3.66 m, the superficial gas velocity is 0.2004 M/s.  
  
Step 8. For this example, it is assumed that the constants a, b and c in Eq. 2 are 0.02, 0.6, and 0.6, respectively, based on units of 1/h for kL, kA, W/m² for PV and M/S for U. Ideally, such constants should be derived from experimental data taken in the actual broth and impeller system that will be used. Based on a required kLa of 0.06495 and a superficial gas velocity of 0.2004 M/s, the required agitator P/V = 349 W/m³. For a batch size of 114 m³, this gives a total invested power of 39.8 kW. Allowing for 95% power transmission efficiency through the gear drive and seal, the motor power draw required is about 41.9 kW. If this figure seems low, it is because the required OTR for this problem is low; this is an "easy" fermentation.  
  
Step 9. To calculate the compressor power, the inlet airflow and pressure are read, as well as the outlet compressor power, assuming roughly adiabatic operation. More detailed calculations can be made after the final statement is chosen. Adjusting for units of work for power, atm for pressure and airflow in M³/min, and using a specific heat ratio for air of 1.394, the required compressor power is 57.97 x (k/inlet flow) x (pressure ratio)²⁸⁻¹.  
  
The inlet pressure is atm. The air inlet is adjusted to 20°C (293 K) is 26.83 M³/min. The outlet pressure is the back pressure plus the liquid pressure in the losses, or 1 + 0.68 + (0.5) = 2.04 + 4.78 atm. Thus, the pressure ratio is also 4.78. The compressor power is 57.97 x 26.83 x ( (4.78)²) = 89.2 kW. Allowing for 70% efficiency, the motor power drawn is 127.4 kW.   
  
Step 10. The total power of the agitators that comprises compressor is 41.9 + 127.4 = 169.3 kW.  
  
Step 11. The optimization steps will not be repeated here, but by varying the air flow, the point of minimum power can be found, as shown in the figure on the previous page.  
  
CEP  
May 2003 www.cpegmagazine.org  
35  
  
Literature Cited  
1. Niemow, A. W., "Gas Dispersion Performance in Fermenter Operation." Chem. Eng. Progress, 86 (2), 67-71 (Feb. 1990).   
2. Bakker, A., et al., "How to Disperse Gases in Liquids." Chem. Eng., 101 (12), pp. 98-104 (Dec. 1994).  
  
GREGORY E. BAZZETT is president of Beer Technology International (203) Clarksville Rd., Cranbury, OH 45327; Phone: (800) 858-2934; Fax: (937) 281-3939; E-mail: bazzett@chout.com. A registered professional engineer in Ohio, he has over 26 years of experience in the design of agitation systems, specializing in fermentation and bioreactors. His company performs general engineering, conducts studies in mixing and bioreactor design, including equipment specification and bid evaluation. Bazzett has acted as senior writers in the U.S. Finance and choice have been his BSCh from the University of Cincinnati, and he is a member of AICHE, the International Society of Pharmaceutical Engineers and the American Chamber of Commerce in Shanghai.

---

