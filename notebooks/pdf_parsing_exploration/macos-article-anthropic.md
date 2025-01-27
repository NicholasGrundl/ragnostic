## Page 1



---

## Page 2

# Correct pilot studies are the key  
  
To optimize full-scale energy consumption, it is necessary to quantitatively predict the relationship between mass-transfer rate, driving force, agitator power and superficial gas velocity (J). To obtain this relationship accurately, the pilot plant must be operated under the same range of conditions as will be found in the full-scale equipment. In practice, this means using much more air and much less agitation than is normal for pilot operation. To obtain the same superficial gas velocity in the pilot plant as in the production equipment, it is not unusual to need a V/VM of 10–15/min, whereas the full-scale V/VM may be 0.5–1.5/min. If the pilot facility does not have sufficient air available, then its air-delivery system must be beefed up. Otherwise, the correlations obtained will not be accurate.  
  
Data must be taken using an impeller system similar to the one that will be used in the full-scale fermenter. Although impeller system design is beyond the scope of this article, properly sized axial pump impellers combined with a lower concave radial impeller have been found to promote excellent liquid-phase OTR uniformity. The gas entrainment has a high gas-handling ability and the difference in power draw between the ungassed and the gassed states is minimal (2).  
  
## Determining system parameters  
  
The defining equation for mass transfer in a fermenter is:  
  
OTR = kLa (Csat – C)                (1)  
  
The goal of the pilot study is to correlate kLa, the overall mass-transfer coefficient, to the agitation and airflow conditions. The correlation is ideally done around the point in the process where oxygen demand is at a maximum, and under similar levels of agitator specific power and superficial gas velocity. This correlation is established by using a simple exponential relationship:  
  
kLa = a(PV)b(J)c                     (2)  
  
The constants a, b and c are derived by empirically fitting the experimental data to the function. With a clean water system, it is possible to fit the data to Eq. 2 with a ±5% variation. In a complex fermenter broth, agreement is often no better than ±30% (2). Care must be taken when designing to allow for such data errors.  
  
It is also important to directly gas saturation data for the specific broth. Predictions based on the solvent (usually water) can be in error because the presence of biomass and dissolved solids may affect the ability to hold dissolved gas. Henry's law may generally be used to correlate data and compensate for changes in absolute partial pressure of the gas.  
  
## Full-scale degrees of freedom  
  
It is possible to get the desired OTR in the full-scale equipment in a number of different ways. At low airflow rates, the gas superficial velocity will be low, so higher agitation power is needed to compensate for this, even to get an equal mass-transfer coefficient. Low gas flow also equates to more oxygen depletion in the exit gas, resulting in a reduced concentration-driving force, which further requires more agitation. In fact, there is a theoretical minimum airflow that must be used given an OTR in the air stream. Below this required OTR, to such a degree, impractical levels of agitation would be required since the driving force would be small at the inlet and zero at the outlet.  
  
At higher air flowrates, the driving force and gas superficial velocity will be larger, resulting in less agitator power being needed to achieve the same OTR. There is a practical maximum air flow as well. The author's experience suggests that operating at superficial gas velocities above 0.6 m/s should be avoided, so as not to allow excessive entrainment of the process fluid in the vented gas.  
  
Within this range from a theoretical minimum to practical maximum, the compressor power requirements increase with airflow, but the required agitator power simultaneously decreases. The sum of the agitator and the compressor power will, in fact, pass through a minimum. It is the goal of the article to show how to operate as close to this minimum as possible.  
  
## Optimizing full-scale design  
  
The following steps should produce a system design that operates close to the minimum power requirement.  
  
Step 1. Based on the peak OTR, calculate the minimum air flow required at 100% utilization.  
  
Step 2. Choose an air flow that is greater than the theoretical minimum calculated in Step 1 for the first design calculation. Start out at about 20% above the minimum.  
  
Step 3. Perform a mass balance and determine the exit gas flowrate and composition, including the amount of CO2 respired.  
  
Step 4. Calculate the driving force for mass transfer. For full-scale equipment, use a log-mean driving force, rather than the simple form given in Eq. 1. Accurate saturation data are needed.  
  
## Nomenclature  
  
a,b,c = empirical constants in Eq. 2    
C = dissolved oxygen concentration, mg/L    
Csat = dissolved oxygen concentration at saturation, mg/L    
DO = dissolved oxygen concentration, mg/L    
kLa = overall mass-transfer coefficient, s-1 or h-1    
OTR = oxygen transfer rate, mg/L-h    
PV = specific power, W/M3    
J = superficial gas velocity, M/s    
V/VM = volume of gas per volume of liquid per minute, min-1  
  
CEP May 2003 www.cepmagazine.org 33

---

## Page 3



---

## Page 4

Step 2. Normally, the iteration process would start with 20% higher airflow than the above value, but for iteration purposes, only one iteration is needed. Therefore, twice the above value is used (vs. 1.20 times the flowrate), which = 25 nM³/min.  
  
Step 3. Perform the mass balance. The inlet airflow of 25 nM³/min contains a total of 1,115 gmol/L of which 234.2 are O₂, and the balance, 880.8 gmol, is other gases, which will be carried through the fermenter unchanged. 7,125 gmol/h, or 118.8 gmol/min of O₂ are consumed, leaving 115.4 gmol/min of O₂ in the outlet gas. In addition, CO₂ is generated at the rate of 112.8 gmol/min (95% of the value of oxygen consumed). So, the outlet gas rate is 1,109 gmol/min with 10.4% O₂. This corresponds to a gas flow at the outlet of 24.9 M³/min.  
  
Step 4. To calculate the driving force, we need to know the absolute pressure and concentration of the air stream at the top and bottom, as well as the DO concentration in the broth at the top and bottom. The bottom pressure equals the backpressure plus liquid head: 0.68 atm + 1 atm (gage pressure) = 1.06 atm (1.0 atm = liquid head at 10 m). So, T = 1.06 atm. Since the saturation concentration at the bottom of the fermenter is 7 × 2.74, the saturation value is 19.18 mg/L.  
  
The pressure at the top is 1.68 atm (abs.) and the concentration of O₂ is 10.4%, so saturation at the outlet is 7 mg/L × 1.68 × (10.4/21) = 5.82 mg/L. Now that saturation values have been established, calculate the driving force. To do this, the liquid DO concentrations must also be known. It has been established that a minimum of 2 mg/L is needed for the process to work effectively. However, real fermenters are not perfectly mixed, so there will be a concentration gradient.  
  
The author has seen cases using multiple radial impellers where the DO varied from bottom to top by more than an order of magnitude. Therefore, if a combination of axial and radial impellers is used in fermenters of this size, the DO at the bottom will be about 50% higher than the top. Using this basis, assign a value of 2 mg/L at the top and 3 mg/L at the bottom. The log-mean driving force is 8.55 mg/L = [(5.82−2)−19.18−3)]/ [ln((5.82−2)/(19.18−3)] = 8.55.  
  
Step 5. The required kₗa = OTR/driving force = (2,000 mg/L·s)/0.8.55 mg/L = 233.9 × 0.06449/s.  
  
Step 6. The average molar flow of gas at the middle is (1,115 + 1,109) / 2 = 1,112 gmol/min, or 24.93 nM³/min. The absolute pressure at the midpoint equals the backpressure plus one-half of the liquid head, or 0.68 + 1 + 0.53 = 2.21 atm. The temperature is 38°C or 311 K. Based on ideal gas law adjustments, the actual gas flow is 24.93 × (1/2.21)(311/273) = 12.85 M³/min.  
  
Step 7. Based on the tank diameter of 3.66 M, the superficial gas velocity is 0.0204 M/s.  
  
Step 8. For this example, it is assumed that the constants a, b and c in Eq. 2 are 0.02, 0.6 and 0.6 respectively, based on units of 1/s for kₗa, W/M³ for P/V and M/s for Vs. Ideally, such constants should be derived from experimental data taken in the actual broth and impeller system that will be used. Based on a required kₗa of 0.06449s and a superficial gas velocity of 0.0204 M/s, the required agitator P/V = 350 W/M³. For a batch size of 114 M³, this gives a total invested power of 39.8 kW. Allowing for 95% power transmission efficiency through the gear drive and seal, the motor power draw required is about 41.9 kW. If this figure seems low, it is because the required OTR for this problem is low: this is an "easy" fermentation.  
  
Step 9. To calculate the compressor power, the inlet airflow and pressure are needed, as well as the outlet compressor power, assuming roughly adiabatic operation. More detailed calculations can be made after the final system is chosen. Adjusting for units of kW for power, atm for pressure and airflow in M³/min, and using a specific heat ratio for air of 1.40, the required compressor power is 5.97 × (inlet pressure) × rate(s) flow × [(pressure ratio)⁰·³-1]  
  
For inlet pressure is 1 atm. The airflow is adjusted to 20°C (293 K) is 26.83 M/min. The outlet pressure is the back pressure plus the liquid head plus the line losses, or 1 + 0.68 + 1.06 + 2 + 0.4 = 4.78 atm. Thus, the pressure ratio is also 4:78. The compressor power is 5.97 × 1 × 26.83 × [(4.78)⁰·²⁸¹-1] = 89.2 kW. Allowing for 70% efficiency, the motor power required is 127.4 kW.  
  
Step 10. The total power of the agitator plus that of compressor is 41.9 + 127.4 = 169.3 kW.  
  
Step 11. The optimization steps will not be repeated here, but by varying the air flow, the point of minimum power can be found, as shown in the figure on the previous page.  
  
## Literature Cited  
  
1. Nienow, A. W., "Gas Dispersion Performance in Fermenter Operation," Chem. Eng. Progress, 86 (2), pp. 61-71 (Feb. 1990).  
2. Bakker, A., et al., "How to Disperse Gases in Liquids," Chem. Eng., 101 (12), pp. 98-104 (Dec. 1994).  
  
GREGORY T. BENZ is president of Benz Technology International (2959 Clarksville Road, Clarksville, OH 45113; Phone: (937) 289-0636; Fax: (937) 289-3910; Email: benztech@btech.net). A registered professional engineer in Ohio, he has over 25 years of experience in the design of agitation equipment for the chemical process industries. The company performs general engineering, and consults in training and equipment design, including equipment specification and bid evaluation. Benz has both Bachelor and Master of Science degrees. He is involved in the BHR Group in line, of Cincinnati, and is a member of AIChE, the International Society of Pharmaceutical Engineers and the American Chamber of Commerce in Shanghai.  
  
CEP May 2003 www.cepmagazine.org 35

---

