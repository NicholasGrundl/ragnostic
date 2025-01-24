## Page 1

# Optimize Power Consumption in Aerobic Fermenters  
  
By performing the necessary pilot work, and rigorously calculating the full-scale performance instead of using simple rules-of-thumb for scale-up, significant energy savings can be achieved in fermenters.  
  
Aerobic fermentation was put to commercial use in the 1940s to make penicillin. Many other antibiotics were made via this method. Over the years, it has become a route to economically produce a variety of compounds, including enzymes, amino acids, vitamins, flavors, biofuels, think kening agents, and cleaning compounds. The list keeps growing.  
  
One reason for its widespread use is its specificity for producing compounds—that is, some species are difficult to make by other means, and others may produce high concentrations of byproducts. Another reason is that fermentation requires comparatively mild conditions, in terms of temperature, pressure and pH. This often allows for less-costly equipment and lower energy costs compared with using standard chemical synthesis.  
  
Still, for operating fermenters as designed to minimize energy use, surprisingly little attention is given to collecting the data needed to predict the full-scale oxygen transfer and energy consumption. To make matters worse, the pilot conditions usually differ from those in the scaled-up, commercial unit. Compared with commercial equipment, pilot units operate at a much higher agitation power (power/unit mass or volume) and a much lower superficial gas velocity (actual gas flow divided by the tank's cross-sectional area).  
  
Nonetheless, attempts are sometimes made to scale up from the limited pilot data. These can be based on an equal power per unit volume, an equal volume of gas per volume of liquid per minute (VVM), or when such a technique yields unreasonably large equipment, as it usually does, engineering judgment is employed to compensate for the increase in superficial gas velocity and pressure driving force in the full-scale equipment.  
  
However, such judgment carries some risk, since the relative contribution of agitation and airflow to mass transfer can vary considerably for different processes and different agitation systems.

---

## Page 2



---

## Page 3

# Reactions and Separations  
  
## Step 5. Calculate the required k₂a.  
## Step 6. Calculate the actual volumetric air flow at the agitator impeller tip. Use the volumetric flow rate to account for temperature, composition, backpressure and liquid head. Use the average flowrates for the inlet and outlet.   
## Step 7. Calculate the superficial gas velocity at the impeller using the above as volumetric.  
## Step 8. Using the mass-transfer relationship developed from pilot scale data, solve for the agitator power. Add about 5% to account for the gear drive and seal losses to get the required motor power draw.  
## Step 9. Calculate compressor power. Include the backstage, liquid head, pressure, and losses from the sparging, piping and filtration systems. Also include the manufacturer's compression efficiency to calculate motor power draw required (typically 50-80%). For an existing plant, these should be calculated based on the actual piping system. For a new plant optimization study, a simplified assumption can be made: the piping system will be sized based on a certain maximum pressure drop at the inlet airflow chosen.  
## Step 10. Calculate the total power of the agitator and the compressor.  
## Step 11. Repeat Step 1-10 for an incremental change in airflow. An increment of 10% of the theoretical minimum is suggested.  
## Step 12. Repeat Step 11 until a minimum total power is found. Add in safety factors to account for data errors and flexibility for future process changes.  
  
This procedure is primarily designed to allow optimization of the original installed compressor and agitator power. It can also be used in an existing fermenter to compute the optimum conditions during the batch cycle, which of course, has a varying oxygen demand from beginning to end. If the airflow and agitator speed are both variable, then a control-logic sequence can be developed to minimize energy usage throughout the processing sequence.  
  
This procedure may seem to involve a lot of calculation time. Of course, once the system equations have been defined, they can be put into a computerized spreadsheet so repeated calculations will take little time. The potential reward can be significant. It is not unusual for a 150,000-L fermenter to operate at 100 kW or more away from the optimum, so reducing power consumption by 25% or more is achievable.  
  
Example:  
The figure on the right shows how the power consumption varies when this procedure is used. A simplifying assumption of constant gas pressure drop was made.

---

## Page 4

# Step 2. Normally, the iteration process would start at a value 20% higher than the literature value, but for this case, it was started at 0.02, 0.06, and 0.06, respectively, based on units of g, kW/m^3, and kw/m^2. This strategy was used to converge faster. The remaining steps in this process should be derived from values stated in the actual broth and impeller system data that will be used. Based on a required k_a of 0.0649/s and a superficial gas velocity of 0.0204 m/s, the required agitator power/V = 349 W/m^3. For a batch size of 114 M^3, this gives a total installed power of 39.8 kW. Allowing for 70% power transmission efficiency through the gear drive and seal, the motor power draw required is about 41.9 kW. This figure seems low, it is because the required OTR for this problem is low, so the "easy" fermentation (step 9) to calculate the compressor power, the inlet airflow and pressure are needed, as well as the outlet compressor power, assuming roughly adiabatic operation.  
  
# Step 4. To calculate the driving force, we need to know the absolute pressure and concentration of the air stream at the top and bottom, as well as the DO concentration in the broth at the top and bottom. The bottom pressure equals the backpressure plus liquid head: 0.68 atm + 1 atm (gage pressure) + 1.06 atm (10.97 m liquid head at 1.0 g/L) = 2.74 atm abs. Since the saturation value at 1 atm is 21% and 2.74 atm, is 7.87%, the saturation concentration at the bottom is 7.87% * (0.68 + 1.06) = 1.19 mM.  
  
# Step 5. The pressure at the top is 1.68 atm (abs) and the concentration of O2 is 10.4%, so saturation at the outlet is 7 mg/L + 1.68 x (10.42/1) = 5.82 mg/L. Now that saturation values have been established, calculate the driving force. To do this, the liquid DO concentrations must also be known. It has been established that a minimum of 2 mg/L is needed for the process to work effectively. However, real fermenters are not perfectly mixed, so there will be a concentration gradient.  
  
# Step 6. The average molar flow of gas at the middle is 0.115 + 1.109 / 2 = 1.112 gmol/min. The absolute pressure at the midpoint equals the backpressure plus half of the liquid head, or 0.68 + 1 + 0.53 = 2.21 atm. The temperature is 38°C or 311 K. Based on these lab adjustments, the actual gas flow is 24.93 x (1/2.21)(311/273) = 12.85 M^3/min.  
  
# Step 7. Based on the tank diameter of 3.66 M, the superficial gas velocity is 0.0204 m/s.  
  
# Step 8. For this example, it is assumed that the concentration of O2 in the broth and impeller system data that will be used.  
  
Literature Cited  
1. Nishino, A. W., "Gas Dispersion Performance in Fermentor Operation," Chem. Eng. Progress, 86 (2), pp. 61-71 (Feb. 1990).  
2. Baddour, R., et al., "How to Disperse Gases in Liquids," Chem. Eng., 101 (12), pp. 98-104 (Dec. 1994).  
GREGORY Z. BELL is President of Berg Technology International (cass, Louisville Road, Clarksville, GA 30523): Phone: (706) 359-6456; Fax: (706) 359-3941. A registered professional engineer in Georgia, he has over 15 years of experience in the design and commercialization of biotechnology processes, specialized in fermentation and biocatalysis. His company performs general engineering, and consults in mixing and bioreactor design, including equipment specification and bid evaluation. Berg has also presented at seminars in the US, France and China, the received BEMA from the University of Cincinnati, and is a member of AlChE, the International Society of Pharmaceutical Engineers and the American Chamber of Commerce in Shanghai.

---

