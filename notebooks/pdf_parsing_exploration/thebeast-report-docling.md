<!-- image -->

## Consultancy on Large-Scale Submerged Aerobic Cultivation Process Design - Final Technical Report

February 1, 2016 - June 30, 2016

Jason Crater, Connor Galleher, and Jeff Lievense Genomatica, Inc. San Diego, California

NREL Technical Monitor: James McMillan

NREL is a national laboratory of the U.S. Department of Energy Office of Energy Efficiency & Renewable Energy Operated by the Alliance for Sustainable Energy, LLC

This report is available at no cost from the National Renewable Energy Laboratory (NREL) at www.nrel.gov/publications.

Subcontract Report NREL/SR-5100-67963 May 2017

Contract No. DE-AC36-08GO28308

<!-- image -->

## Consultancy on Large-Scale Submerged Aerobic Cultivation Process Design Final Technical Report

February 1, 2016 - June 30, 2016

Jason Crater, Connor Galleher, and Jeff Lievense Genomatica, Inc. San Diego, California

NREL Technical Monitor: James McMillan Prepared under Subcontract No. AFC-6-62032-01

NREL is a national laboratory of the U.S. Department of Energy Office of Energy Efficiency & Renewable Energy Operated by the Alliance for Sustainable Energy, LLC

This report is available at no cost from the National Renewable Energy Laboratory (NREL) at www.nrel.gov/publications.

Subcontract Report NREL/SR-5100-67963 May 2017

Contract No. DE-AC36-08GO28308

## This publication was reproduced from the best available copy submitted by the subcontractor and received no editorial review at NREL.

## NOTICE

This report was prepared as an account of work sponsored by an agency of the United States government. Neither the United States government nor any agency thereof, nor any of their employees, makes any warranty, express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness of any information, apparatus, product, or process disclosed, or represents that its use would not infringe privately owned  rights.    Reference  herein  to  any  specific  commercial  product,  process,  or  service  by  trade  name, trademark, manufacturer, or otherwise does not necessarily constitute or imply its endorsement, recommendation, or  favoring  by  the  United  States  government  or  any  agency  thereof.    The  views  and  opinions  of  authors expressed herein do not necessarily state or reflect those of the United States government or any agency thereof.

This report is available at no cost from the National Renewable Energy Laboratory (NREL) at www.nrel.gov/publications.

Available electronically at SciTech Connect http:/www.osti.gov/scitech

Available for a processing fee to U.S. Department of Energy and its contractors, in paper, from:

U.S. Department of Energy Office of Scientific and Technical Information P.O. Box 62 Oak Ridge, TN 37831-0062 OSTI http://www.osti.gov Phone:  865.576.8401 Fax: 865.576.5728 Email: reports@osti.gov

Available for sale to the public, in paper, from:

U.S. Department of Commerce National Technical Information Service 5301 Shawnee Road Alexandria, VA 22312 NTIS http://www.ntis.gov Phone:  800.553.6847 or 703.605.6000 Fax:  703.605.6900 Email: orders@ntis.gov

## Contents

| Executive Summary .................................................................................................................................... 4 Contact Information .................................................................................................................................... 5 Introduction ................................................................................................................................................. 7   |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Feedback ...................................................................................................................................................... 8                                                                                                                                                                                                                                                                                                                      |
| Modeling Methodology .......................................................................................................................... 8                                                                                                                                                                                                                                                                                                                                      |
| Model Assumptions .............................................................................................................................. 11                                                                                                                                                                                                                                                                                                                                    |
| Strain Selection ..................................................................................................................................... 12                                                                                                                                                                                                                                                                                                                              |
| Bioreactor Type .................................................................................................................................... 12                                                                                                                                                                                                                                                                                                                                |
| Bioreactor Scale ................................................................................................................................... 15                                                                                                                                                                                                                                                                                                                                |
| Bioreactor Cooling Design ................................................................................................................... 18                                                                                                                                                                                                                                                                                                                                       |
| Bioreactor Operating Mode .................................................................................................................. 20                                                                                                                                                                                                                                                                                                                                        |
| Seed Train Design ................................................................................................................................ 22                                                                                                                                                                                                                                                                                                                                  |
| Recommendations .................................................................................................................................... 24                                                                                                                                                                                                                                                                                                                                |
| References ................................................................................................................................................. 25                                                                                                                                                                                                                                                                                                                        |

## Executive Summary

NREL is developing an advanced aerobic bubble column model using Aspen Custom Modeler (ACM). The objective of this work is to integrate the new fermentor model with existing technoeconomic models in Aspen Plus and Excel to establish a new methodology for guiding process design. To assist this effort, NREL has contracted Genomatica to critique and make recommendations for improving NREL's bioreactor model and large scale aerobic bioreactor design for biologically producing lipids at commercial scale.

While acknowledging the great work NREL has done to this point in developing a bioreactor model, Genomatica has highlighted a few areas for improving the functionality and effectiveness of the model. Genomatica recommends using a compartment model approach with an integrated black-box kinetic model of the production microbe. We also suggest including calculations for stirred tank reactors to extend the model's functionality and adaptability for future process designs.

Genomatica also suggests making several modifications to NREL's large scale lipid production process design. The recommended process modifications are based on Genomatica's internal techno-economic assessment experience and are focused primarily on minimizing capital and operating costs (critical for fuel product commercial viability, see Table 1 on page 6). These recommendations include selecting/engineering a thermotolerant yeast strain with lipid excretion; using bubble column fermentors; increasing the volume of production fermentors; reducing the number of vessels; employing semi-continuous operation; and recycling cell mass and glycerol.

## Contact Information

Genomatica, Inc. 4757 Nexus Center Drive San Diego, CA 92121

Jason Crater (Primary Contact)

Manager, Scale-up & Technology Transfer

Email: jcrater@genomatica.com

Phone: (858) 784-1922

Connor Galleher

Bioprocess Development Engineer

Email: cgalleher@genomatica.com

Phone: (858) 210-4413

Jeff Lievense, Ph.D.

Senior Advisor to the CEO

Email: jlievense@genomatica.com

Phone: (858) 210-4451

Table 1: List of Process Design Parameters with Associated Cost and Design Implications

| Parameter                   | Decreases Cost                | Increases Cost               | Considerations                                                                                                                                                        |
|-----------------------------|-------------------------------|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Oxygen                      | Anaerobic                     | Aerobic                      | Anaerobic fermentation eliminates  oxygen transfer costs, and may require  stirred tank reactors to mix.                                                              |
| Fermentor Volume            | Larger, fewer                 | Smaller, more                | Fabrication costs, operating mode,  gradients, mixing time, process/facility  complexity are all impacted.                                                            |
| Fermentor Type              | Bubble column                 | Stirred tank                 | Bubble column type is lower capital,  less maintenance, less contamination  risk, and lower OTRmax.                                                                   |
| Cooling Design              | External loop                 | Jacket, coils                | External loop has increased risk of  contamination, and impacts the broth  conditions in the loop.                                                                    |
| Operating Mode              | Semi-continuous,  continuous  | Batch, fed-batch             | Continuous mode uses fermentor  volume and associated system capital  equipment more efficiently.                                                                     |
| Specific Productivity  (qp) | Higher qp                     | Lower qp                     | Higher qp favors higher yield and rate.                                                                                                                               |
| Product Location            | Extracellular                 | Intracellular                | retention or recycle, increased yields,  and lower downstream processing  (DSP) costs.                                                                                |
| Product Properties          | Insoluble, low  boiling point | Soluble, high  boiling point | Insoluble extracellular product enables  physical separation. Low boiling point  enables direct distillation.                                                         |
| Broth Temperature           | ≥ 35 o C                      | ˂ 35 o C                     | Lower broth temperature requires a  chiller.                                                                                                                          |
| Broth Viscosity             | Lower                         | Higher                       | Lower broth viscosity reduces heat and  oxygen (aerobic only) transfer costs.                                                                                         |
| Glycerol Byproduct          | Recycle                       | Dispose as  waste            | Glycerol recycle increases carbon yield  by 5% .                                                                                                                      |
| Cell Mass Usage             | Retention                     | Single-use                   | Cell retention increases yield and rate,  but also contamination risk.                                                                                                |
| Sterility                   | Sanitary                      | Aseptic                      | Sterility is influenced by operating  conditions, microbe, and product.  Aseptic design requires more  opex/capex to maintain the integrity of  the sterile boundary. |

## Introduction

The National Renewable Energy Laboratory's (NREL's) Biochemical Platform is developing processing strategies for producing biofuels and bio-based products from lignocellulosic feedstocks. One approach is based on using pretreatment followed by enzymatic hydrolysis to deconstruct the major plant carbohydrates, cellulose and hemicellulose, into monomeric sugars. These biomass-derived sugars are then clarified using solid-liquid separation processes prior to being concentrated and converted to products. Submerged aerobic fermentation production of intracellular lipids from biomass-derived sugars using oleaginous yeast is one of several sugar upgrading conversion routes being considered. Once recovered, the lipids can then be hydrotreated and isomerized to produce a hydrocarbon biofuel (1).

NREL is developing an advanced aerobic bubble column model using Aspen Custom Modeler (ACM). The objective of this work is to integrate the new fermentor model with existing technoeconomic models in Aspen Plus and Excel to establish a new methodology for guiding process design. To assist this effort, NREL has contracted Genomatica to critique and make recommendations for improving NREL's bioreactor model and large scale aerobic bioreactor design for biologically producing lipids at commercial scale.

## Feedback

## Modeling Methodology

NREL is developing an advanced aerobic bubble column model using ACM that will be integrated with existing techno-economic models in Aspen Plus and Excel. The fermentation model in ACM is used to dynamically simulate a single batch from inoculation to harvest. The time-dependent results from the fermentation simulation are subsequently exported to Excel for integration and calculation of steady-state rates, which are then imported into techno-economic models in Aspen Plus (2). Genomatica has employed a similar methodology in which multiple software platforms (e.g. Mathematica, Excel, Aspen) are used to assess both steady state and dynamic processes. When modeling complete processes using multiple software platforms, Genomatica prefers to use an Excel interface with all other programs accessed on the back end, as Excel improves the accessibility of the model; i.e., most users are familiar with and comfortable using Excel.

Genomatica's dynamic fermentation model is set up in Mathematica and functions as a standalone program with a user interface that lets users easily manipulate model inputs (e.g., fermentor volume and dimensions, mixing design, process parameters, strain, etc.). The program also features a plotting tool that allows users to visualize all parameters calculated in the model without having to export the data to other software platforms. Additionally, the program allows for direct comparison of multiple simulations, which lets users assess the impact of changes in various design or process parameters on process performance. The ability to export data to other models or function as a stand-alone application improves the flexibility and effectiveness of the model. This enables the model to be used for various applications through all stages of a project. Genomatica's fermentation model has been used as a tool for large-scale bioreactor design, techno-economic assessment, and design of bioreactor scale-down experiments. Genomatica recommends building process modeling tools with flexibility and user-friendliness in mind to ensure the models are leveraged at every stage of the project. Flexibility will also facilitate adaptation of the model for future process designs.

One important distinction between Genomatica's and NREL's fermentation modeling methodologies is Genomatica uses a compartment model approach. Rather than modeling the fermentation broth as a single component, Genomatica's model compartmentalizes the broth based on assumed mixing patterns for bubble columns (based on L/D) and stirred tank reactors (based on impeller type and location). Gas and liquid phase component balances for O2 and CO2 are solved for each compartment simultaneously and iteratively using an ordinary differential equation (ODE) solver built in to Mathematica. Genomatica uses the same component balances and literature correlations for mass transfer coefficients, mass transfer rates, and gas hold-up reported for NREL's model (2). However, it is important to note that many of these literature correlations have correction factors for temperature, pressure, and/or viscosity, which can have a significant impact on the calculations. The impact of these operating parameters is highlighted in the Bioreactor Type section below (see page 12). It is also important to note that literature correlations should be cautiously applied, as >95% of these correlations are developed in lab scale or small pilot fermentors.

The advantage of using a compartment model is it provides insight into how fermentor volume and geometry impact axial gradients that the microbe will encounter at scale. Not only does this

aid in the initial bioreactor design, but it also facilitates the design of process scale-down studies to mimic the anticipated large-scale conditions in the laboratory. See the Bioreactor Scale section (page 15) for more details. Klaas van't Riet's and Johannes Tramper's Basic Bioreactor Design provides a detailed example (chapter 18, example 18.1) on how to set up a compartment model for bubble column reactors (3). Klaas van't Riet's and Rob van der Laans' 'Mixing in bioreactor vessels' provides useful information on broth mixing and compartmentalization in bubble column and stirred tank reactors (4).

In order to maximize the effectiveness of the compartment model, a black-box kinetic model of the production microbe should also be incorporated. Linking the kinetics of the host microbe's metabolism to the bioreactor model provides important insight into how the design (volume, geometry) impacts the environment (pH, temperature, pressure, pO2, pCO2, substrate concentration, etc.) the microbe experiences in different zones of the fermentor. The black box model can be used to calculate characteristic times for important process parameters, such as substrate, product, pH, temperature, O2, CO2, ammonium, byproducts, etc. These characteristic times can then be compared with mixing time estimates to assess the degree of broth heterogeneity for each parameter.

For example, substrate consumption rate and mixing time can be used to calculate the gradient in residual substrate concentration from the top (near the substrate addition point) to the bottom of the fermentor. If the microbe is sensitive to gradients in residual substrate concentration then the bioreactor volume, geometry, or number of substrate feed points may need to be adjusted to maximize process performance. Similarly, rates of O2 consumption and CO2 production can be used to calculate axial gradients in transfer rates and dissolved concentrations of O2 and CO2, respectively. Sensitivity to these parameters may also be addressed by modifying the bioreactor design (e.g., volume, aspect ratio), or by adjusting process parameters (e.g., aeration rate).

NREL's current model assumes a fully aerobic fermentation process with nitrogen (ammonium) limitation used as a lever to limit cell mass propagation and turn on TAG production. A simple black box model can be developed using the process reactions outlined in NREL's statement of work (1). Because ammonium is the limiting nutrient, a relation between specific growth rate (µ) and residual ammonium concentration is required. For this the Monod growth equation for microbes can be used (5):

Equation 1: 𝜇𝜇 = 𝜇𝜇𝑚𝑚𝑚𝑚𝑚𝑚 ∗ 𝑆𝑆 𝐾𝐾𝑆𝑆+𝑆𝑆

Where µ is the microbe specific growth rate (hr -1 ), µmax is the maximum microbe specific growth rate (hr -1 ), S is the concentration of the limiting nutrient (ammonium), and KS is the half-velocity constant (value of S where µ = 0.5*µmax).

Additionally, a relation for specific product formation rate (qp) as a function of µ is required. The qp(µ) relation can be easily determined from experimental data. If experimental data are not available, then assumptions must be made based on the anticipated relationship between µ and qp and the kinetics of product formation (qp,max). For an aerobic process producing a product that costs energy (i.e., the biosynthetic pathway has a net consumption of biochemical energy and thus a positive change in free energy), it is difficult to predict the algebraic form of the qp(µ)

relation. Typically, the qp(µ) function takes the form of a complex, non-linear relation. Example qp(µ) functions include (6):

𝑞𝑞𝑝𝑝,𝑚𝑚𝑚𝑚𝑚𝑚 ∗ 𝜇𝜇

Equation 2: 𝑞𝑞𝑝𝑝,1 = 𝛼𝛼 + 𝜇𝜇 Equation 3: 𝑞𝑞𝑝𝑝,2 = 𝑞𝑞𝑝𝑝,𝑚𝑚𝑚𝑚𝑚𝑚 1 + 𝜇𝜇 𝛼𝛼 Equation 4: 𝑞𝑞𝑝𝑝,3 = 𝑞𝑞𝑝𝑝,𝑚𝑚𝑚𝑚𝑚𝑚 ∗ 𝜇𝜇 𝛼𝛼 + 𝜇𝜇 + 𝜇𝜇 2 𝛽𝛽

Where qp,max is the maximum specific product formation rate (mmol product/g dcw/hr), and α/β are constants used to fit actual fermentation data. See Figure 1 below for example plots of the qp(µ) functions outlined above in Equations 2-4. Because it is assumed that ammonium limitation is being used to downregulate growth and upregulate TAG production, Equations 3 and 4 provide more realistic functions for NREL's black box model. Equation 3 should be used if peak specific TAG production occurs at true ammonium limitation when growth stops (µ = 0). If, however, peak specific TAG production occurs at some low level of residual ammonium and growth, then Equation 4 should be used. This would be the case if true ammonium limitation completely shuts down metabolism (growth, production, and substrate uptake). Note that maintaining a uniformly low residual ammonium concentration to maintain minimal growth and peak TAG production will likely prove difficult at scale, as gradients in residual ammonium concentration will exist at low concentration in any large fermentor.

Figure 1: Example qp(µ) functions that can be used to fit experimental fermentation data

<!-- image -->

The stoichiometric coefficients of the individual process reactions for growth, product formation, and maintenance can be used to define Herbert-Pirt distribution relations for all other process reaction components (substrate, O2, CO2, H2O, ammonium, heat) as a function of µ, qp, and maintenance coefficient (ms, g substrate/g dcw/hr). Specific rates for these components can then be calculated as a function of µ by combining the Herbert-Pirt relations with the qp(µ) relation. All component rates can then be linked to the residual ammonium concentration using the µ(S) function (6).

There are a number of useful sources published by J. J. Heijnen that explain the concepts behind the black-box model approach in great detail (6-11). Additionally, Biotechnology Studies Delft Leiden offers an annual Advanced Course Bioprocess Design that covers bioprocess reactions, stoichiometry, and black-box modeling with several useful and relevant examples included in the course work. The course also covers a number of other topics directly relevant to NREL's modeling work, including mass and heat transfer, mixing in large-scale bioreactor vessels, and scale-up/scale-down approaches (23). Genomatica highly recommends attending this course, which is held annually in April, either at TU Delft or Wageningen University (12).

## Model Assumptions

NREL's model currently assumes a theoretical maximum lipid yield of 0.33 g TAG/g glucose. It should be noted that the lipid yield (g TAG/g sugar) is very much dependent on the metabolic properties of the type of yeast used; the metabolic pathways for NADH, NADPH, and acetylCoA generation; their location in the cell (cytoplasm vs. mitochondria); and the type of sugar. Although there is some debate regarding the theoretical maximum yield (maximum chemical yield is 0.37 g/g), discussions with Hans Van Dijken and other literature references suggest the value is lower than the current model assumption (13). While strain engineering and alternative pathways may be employed to increase the theoretical maximum yield, Genomatica recommends performing a sensitivity analysis of yield on process economics.

Genomatica also believes NREL should reconsider the assumption that the TAG product must be intracellular. There are significant advantages associated with an extracellular product:

- 1. There is the potential to more closely approach the theoretical maximum yield when the product is excreted. This is because the ratio of product to cell mass can exceed 10, whereas for intracellular product the ratio is most probably less than 10 and even less than 5.
- 2. Product excretion would facilitate downstream product separation and eliminate the need for a cell lysis step, which would reduce both capital and operating costs. Insoluble extracellular product (lower density than water and cells) could be recovered by an inexpensive solid-liquid separation.
- 3. Product excretion would enable cell mass retention, which would yield substantial cost benefits. Aseptically separating and recycling productive biocatalyst for multiple batches can have a significant impact on the effective process yield, as the average substrate consumed per cycle for generating cell mass is greatly reduced. Effective cell mass retention requires a robust production host that is genetically stable and can withstand the high shear forces encountered in the downstream separations equipment (e.g. microfiltration or centrifugation). The need for aseptic cell mass separations equipment does increase capital and operating costs compared to non-sterile systems. This cost, however, should be significantly less than the cost savings from the higher effective process yield and removal of the cell lysis process step.
- 4. Product excretion will most likely also lower broth viscosity, enhancing oxygen transfer efficiency. In addition, oxygen transfer capacity will be increased due to higher oxygen solubility in the hydrocarbon phase.

## Strain Selection

Strain selection will greatly influence bioreactor design, so bioreactor design/costs should guide strain selection rather than the other way around. For example, a thermotolerant yeast can dramatically increase the efficiency of bioreactor cooling, reducing associated costs (see also Bioreactor Cooling, pp16-18). On this specific point, a modification that increases yeast thermotolerance has been discovered recently; see Casepta et al. (14). Sensitivities to carbon dioxide levels and oxygen gradients can influence the choice of fermentor aspect ratios and the practical limitations of the fermentor volume. Selecting a strain that has demonstrated robust performance under these conditions will allow for larger fermentors and realization of the associated cost advantages. Genetic stability is another important consideration as more generations of cell mass propagation are required at scale. This aspect is even more important if enhanced modes of fermentor operation, such as semi-continuous or continuous production, are employed due to the associated increased tendencies for genetic degeneration in extended cultivation.

The ability to utilize glycerol as a fermentation substrate should also be considered. Glycerol is a byproduct of the chemical process used to convert TAGs to usable biodiesel fuel. This represents a significant cost savings opportunity for the process, as the hydrocarbon fuel yield could be increased by ~5%. Otherwise, there will be a large volume of glycerol to dispose as waste, adding to the fuel production cost.

Another important consideration for strain selection is the potential to capture value from spent cells as a co-product. By selling the cell mass as a co-product, production costs can be substantially decreased. Solazyme, for example, is currently seeking regulatory approval for applications of a co-product cell mass in animal feed. More information on the use of genetically modified microbes in animal feed can be obtained from the Association of American Feed Control Officials (15). The person responsible for yeast products is:

Alan Harrison Director, Feed and Milk Programs University of Kentucky Division of Regulatory Services Room 103, Regulatory Services Building Lexington, KY 40546-0275 United States Email: alan.harrison@uky.edu Phone: (859) 257-5887

## Bioreactor Type

There are numerous advantages to employing bubble column type reactors for fermentationbased production processes. Bubble column reactors have excellent heat and mass transfer characteristics, making them suitable for a wide range of process conditions. Additionally, the design simplicity and lack of moving parts in bubble columns greatly reduces the capital, operating, and maintenance costs associated with more complex stirred tank reactors. The mechanical simplicity and lack of agitator shaft and impellers also improves vessel cleanability and sterilizability, which reduces the risk of contamination and greatly improves process

reliability. Bubble column reactors are also known to provide superior performance with shear sensitive microbes, as power is distributed more evenly throughout the broth, reducing the microbe's exposure to high shear forces (16-20).

Perhaps the most significant advantage to employing bubble column reactors instead of stirred tank reactors is the upfront capital cost savings. Based on Genomatica's experience with vessel fabrication vendors, stirred tank reactor costs can be anywhere from 20-30% higher than bubble columns of similar volume. Uninstalled equipment cost estimates based on vendor quotations for 660 m 3 bubble column reactors are in the $2.0-2.2 MM range, whereas stirred tank reactors are $2.5-2.7 MM. Assuming an installation factor of 2.6 and considering a facility with 50 production vessels, this equates to a total installed capital cost savings of about $67 MM and annual fixed cost savings of about $6.3 MM. The latter includes all plant labor, supervision, overhead, insurance, and taxes.

There are a few disadvantages of note for bubble column reactors. The most obvious disadvantage is that broth mixing is coupled with aeration, which means that the aeration rate cannot be changed without also changing the rate of broth mixing (see Figure 2 below). To maintain a constant rate of broth mixing, the level of aerobicity can be adjusted without changing the total aeration rate by manipulating the composition of the sparge air via dilution with another gas, such as nitrogen or carbon dioxide (17). However, the cost of producing pure nitrogen would likely outweigh the cost savings associated with bubble columns, and the addition of carbon dioxide to the inlet sparge gas would likely be detrimental to the performance of the production microbe. Stirred tank reactors offer more flexibility in that both agitation and aeration can be adjusted to modulate oxygen transfer rate (OTR) while maintaining a constant rate of mixing.

Figure 2: Impact of superficial gas velocity on oxygen transfer rate and mixing time for bubble columns

<!-- image -->

- 1 1,000 m 3 bubble column gassed with air, vessel aspect ratio L/D = 4, broth temperature T = 35 o C, top pressure Ptop = 0.34 atm,g, broth viscosity µ = 0.72 cP (H2O at 35 o C), assuming O2 depletion = 0.55%/m, US* used for kLa calculation, log mean concentration driving force (C*-CL) used for OTR calculation. US* is the US corrected for operating temperature and average pressure (mid broth). The log mean concentration driving force is calculated as ((C*-CL)out - (C*-CL)in) / ln((C*-CL)out / (C*CL)in).

The coupling of aeration and mixing ultimately limits the practical application of bubble columns to aerobic fermentation processes with minimum levels of aerobicity around 15 mol/m 3 /hr. Processes requiring anaerobicity or low levels of oxygenation (<15 mol/m 3 /hr) would result in inadequate mixing and significant broth heterogeneity, unless an external broth recycle loop was added. There are also upper limits to the levels of oxygenation that can be achieved in bubble column reactors. The maximum achievable oxygen transfer rate is limited by the maximum operating superficial gas velocity, as liquid entrainment in the gas phase occurs with gas velocities above 0.3 m/s (17). Oxygen enrichment is another strategy that may be employed to increase oxygen transfer rates; however, the cost benefits should be carefully evaluated, including also an accounting for the effects of further elevated pCO2.

Another important consideration is the impact of broth physical properties on mass transfer characteristics. Temperature, pressure, and viscosity have a significant impact on the maximum achievable oxygen transfer rate (see Figure 3 and Figure 4 below). Increasing broth temperature and operating pressure increase OTR capacity, while increasing broth viscosity decreases OTR capacity. These effects highlight the importance of understanding process requirements and operating ranges in order to select the proper process equipment. For instance, if the process is expected to have a broth viscosity >2 cP and requires oxygen transfer rates >150 mol/m 3 /hr, then a stirred tank type reactor should be selected rather than a bubble column to ensure sufficient levels of oxygenation can be achieved.

Figure 3: Effect of temperature and pressure on oxygen transfer rate capacity in bubble columns

<!-- image -->

- 1 Maximum achievable OTR for 1,000 m 3 bubble column gassed with air, L/D = 4, T = 35 o C, µ = 0.72 cP (H2O at 35 o C), US = 0.3 m/s, O2 depletion = 0.55%/m, US* used for kLa calculation, log mean concentration driving force used for OTR calculation.
- 2 Maximum achievable OTR for 1,000 m 3 bubble column gassed with air, L/D = 4, µ(T) data for H2O used, Ptop = 0.34 atm, US = 0.3 m/s, O2 depletion = 0.55%/m, US* used for kLa calculation, log mean concentration driving force used for OTR calculation.

Figure 4: Effect of broth viscosity on oxygen transfer rate capacity for bubble columns and impact of temperature on viscosity (21)

<!-- image -->

<!-- image -->

- 1 Maximum achievable OTR for 1,000 m 3 bubble column gassed with air, L/D = 4, T = 35 o C, Ptop = 0.34 atm, US = 0.3 m/s, O2 depletion = 0.55%/m, US* used for kLa calculation, log mean concentration driving force used for OTR calculation.

Another challenge associated with bubble column reactors is the difficulty in simulating the industrial process at lab scale (process scale-down), as the hydrodynamics of bubble columns are largely scale-dependent (17). Column geometry and hydrostatic pressure have a significant impact on mass transfer and broth mixing. It is important to note, however, that the industrial scale conditions can be modeled and simulated at lab scale using various methodologies, including oscillation control algorithms and multi-compartment reactor configurations. These studies are best conducted using stirred tank reactors because they provide full flexibility in mimicking aeration rate (vvm), kLa, and mixing time.

For the large-scale submerged aerobic cultivation of oleaginous yeast, Genomatica recommends the use of bubble column reactors for the cost savings and operational advantages outlined above, provided that broth viscosity is <2 cP at ≥35 o C. It is recommended that more data be collected in order to refine model assumptions and to verify bubble columns are sufficient for the anticipated process requirements. It is particularly important to generate broth viscosity data for high cell density oleaginous yeast, recognizing that viscosity is also impacted by fermentation temperature. Considering the impact current assumptions have on reactor design, both reactor types should be included in the model. This flexibility will allow NREL to leverage the modeling capabilities developed during this assignment for future projects, as stirred tanks might prove beneficial for other process designs (e.g., fermentation processes with OTR <15 mol/m 3 /hr or >150 mol/m 3 /hr). The addition of stirred tank reactors to the current model should be easily accomplished with the addition of a few literature correlations for mass transfer and mixing (see references 3-4 for more details).

## Bioreactor Scale

NREL's current process design assumes a maximum vessel volume of 500 m 3 for an aerobic process. Genomatica believes that this can be increased based on internal fermentor modeling

work, discussions with vendors and consultants, and existing commercial-scale aerobic production fermentors used by other companies (see Table 2 below for a partial list of commercial-scale reactors known to Genomatica). The largest installed aerobic stirred tank reactors known to Genomatica are 1,000 m 3 . These reactors were installed at Italprotein's facility in Sarroch, Italy, in the 1970s for single-cell protein production from alkanes, but are no longer operating. The largest installed bubble columns are also 1,000 m 3 . These reactors were designed, built, and operated by Pfizer for citric acid production at their Southport, North Carolina facility (including fermentation of alkanes to citric acid by oleaginous yeast in the 1970s). The site was later purchased by ADM and is still operating today.

Table 2: List of Aerobic Commercial-Scale Fermentors

| Company            | Location              | Reactor Type   | Volume (m 3 )   |
|--------------------|-----------------------|----------------|-----------------|
| Fermic             | Lebrija, Mexico       | Stirred Tank   | 190             |
| Novozymes          | Ottawa, Canada        | Bubble Column  | 220             |
| Tate & Lyle        | Decatur, Illinois     | Bubble Column  | 227             |
| ADM                | Clinton, Iowa         | Stirred Tank   | 500             |
| Cargill            | Eddyville, Iowa       | Bubble Column  | 500             |
| Cargill            | Uberlandia, Brazil    | Bubble Column  | 500             |
| Nutrasweet         | Augusta, Georgia      | Bubble Column  | 520             |
| Dupont-Tate & Lyle | Loudon, Tennessee     | Bubble Column  | 600             |
| Solazyme           | Moema, Brazil         | Stirred Tank   | 600             |
| Evonik             | Castro, Brazil        | Stirred Tank   | 700             |
| Jungbunzlauer      | Pernhofen, Austria    | Bubble Column  | 750             |
| Jungbunzlauer      | Port Colborne, Canada | Bubble Column  | 750             |
| Italprotein        | Sarroch, Italy        | Stirred Tank   | 1,000           |
| ADM                | Southport, NC         | Bubble Column  | 1,000           |

Genomatica's fermentor modeling work and input from fermentor fabricators suggest that even larger vessel volumes can be employed for aerobic processes using bubble column reactors. Considering the cost implications of building larger vessels (see Figure 5 below), it is advantageous to maximize fermentor volume to within practical limits. Ultimately, the maximum volume for aerobic production reactors depends on process requirements for oxygen transfer, heat transfer, the production host's sensitivity to scale-dependent parameters, and production scheduling considerations (i.e., <4 fed-batch fermentors imposes inefficiencies in supporting utilities). Scale-dependent parameters include hydrostatic pressure, partial pressure of dissolved gases (e.g., CO2), and broth heterogeneity (gradients in oxygen transfer rates, dissolved oxygen concentration, pH, temperature, and substrate concentration). Increasing reactor volume typically amplifies the severity of these scale-dependent parameters (see Figure 6 below), which points to the importance of selecting a robust production host (insensitive to fluctuations) for maximizing vessel volume and minimizing cost. This also highlights the need for developing detailed process models to assess the combined effects of all parameters that impact capital and operating costs. Building an integrated fermentor-microbe model, as described above, provides insight into how

fermentor volume and geometry impact various process parameters and indicates where process sensitivities exist. Linking the kinetics of the host microbe's metabolism to the reactor model allows for calculation of characteristic times for important process parameters, which provides useful information regarding the scale-dependent parameters outlined above. This information can then be used to assess risk and determine the practical limitations of the production fermentor volume and in relation to candidate host strain characteristics.

Figure 6: Impact of fermentor volume on broth gradients and mixing time for bubble columns

<!-- image -->

<!-- image -->

- 1 Uninstalled vessel costs estimated using a 2012 vendor quotation of $1.9MM for a 666 m 3 bubble column reactor assuming a scaling factor of 0.6 and adjusting to 2015 costs using the Chemical Engineering Plant Construction Index (CEPCI). Vessel cost accounts for an aseptic jacketed bubble column and its associated internals.
- 2 Total Installed Fermentor Capital (TIFC) costs estimated assuming total plant fermentation rate of 0.4 g/L/hr (25,000 m 3 total capacity) vs. 2.0 g/L/hr (5,000 m 3 total capacity), a scaling factor of 0.6, and an installation factor of 2.6. TIFC includes the vessel cost and installation costs (concrete, steel, piping, valves, construction labor and supervision, etc.) for all the fermentors. TIFC does not include seed fermentor costs or supporting utility costs (e.g., air compressor, air filtration, cooling pumps, cooling towers). Material of construction is assumed to be SS316 (SS304 would be about 20% less). Quotes for the fermentors were obtained from Enerfab (Cincinnati, OH), a well-recognized fabricator/supplier of large-scale, industrial fermentors (including bubble columns).

Figure 5: Impact of fermentor volume on equipment cost and total fermentor capital for bubble columns

<!-- image -->

<!-- image -->

- 1 Vessel L/D fixed at 4, µ = 0.72 cP (H2O at 35 o C), T = 35 o C, Ptop = 0.34 atm,g, O2 depletion = 0.55%/m, US* used for kLa calculation, log mean concentration driving force used for OTR calculation.

In addition to shaping the initial process design, the process model should be refined and updated as the project progresses to validate and improve the process design and to provide critical feedback to strain development. Furthermore, the model can be used to design process scaledown experiments to proactively evaluate process performance and de-risk the scale-up process. Any performance issues identified through scale-down experimentation can then be addressed via process or strain engineering ahead of commercialization, even after the commercial design has been locked in (23).

## Bioreactor Cooling Design

Reactor cooling methodology is an important design consideration that is tied to process oxygenation requirements and fermentor scale and geometry. The metabolic heat released during aerobic fermentation is a function of oxygen consumption, as the catabolism of sugars by microbes is exothermic. Heat removal capacity is a function of heat transfer coefficient, heat transfer area, cooling fluid flow rate, and temperature differential between the broth and reactor coolant (delta T). Removal of excess heat is required to maintain broth temperature at the optimal set point. If heat removal is insufficient, broth temperature will rise, which may result in enzyme degradation, cell death, and significant production losses. It is important to know the rate of heat generation during fermentation, the effect of fermentation temperature on performance, and the feasible range of fermentor operating temperatures in order to employ a cooling system that provides sufficient cooling capacity.

It is generally accepted that the heat evolution rate during aerobic fermentation is directly proportional to the oxygen consumption rate of the microbe. The metabolic heat generated can be estimated using the following relation (3,24):

Equation 5:  Qmet = 460 * OUR

Where Qmet is the rate of metabolic heat generation in kJ/m 3 /hr and OUR is the oxygen uptake rate in mol O2/m 3 /hr. This linear relationship allows the heat release to be estimated based on the oxygen uptake rate profile of the production process. Heat generated via agitation (for stirred tank reactors) and heat removed via evaporative cooling due to aeration should also be considered, though often these contributions to the heat balance are negligible compared to the metabolic heat load.

The three most common methods for fermentor heat removal are wall cooling via vessel jacket, internal cooling via banks of coils, and external loop cooling via pumping broth through a heat exchanger. There are advantages and disadvantages to each methodology that must be considered when deciding which system(s) to employ at scale.

Jacketed wall cooling capacity is constrained by the scale and geometry of the fermentor, which impacts the surface area available for heat transfer. Increasing reactor volume typically reduces the heat removal capacity per unit volume due to reduction in the heat transfer surface area to volume ratio and/or because of the need for increased wall thickness to compensate for higher hydrostatic pressures (which reduces the heat transfer coefficient). Because of this, wall cooling typically requires larger temperature differentials between the broth and cooling medium. Larger delta T typically requires a chiller, which increases both capital and operating costs. The primary advantage of wall cooling over internal coils and external loops is that it poses no risk of

contamination, which increases process reliability. Another advantage is that the addition of a jacket has a modest impact on equipment costs.

Internal cooling coils provide higher heat transfer coefficients and more surface area compared to wall cooling, which increases the cooling capacity. The increase in surface area may allow for smaller temperature differentials between the broth and cooling medium and may eliminate the need for a chiller. This depends on the metabolic heat load generated by the process and also seasonal temperature variation (i.e., chilled water may only be needed in warm weather with cooling tower water being sufficient in cold weather). The major disadvantage of internal cooling coils is the increased risk of contamination, which ultimately impacts process reliability. Internal cooling coils will experience pin-hole leaks and stress fractures due to repeated expansion and contraction cycles during sterilization procedures and the corrosive effects of some fermentation media. These leaks allow non-sterile cooling medium to enter the fermentor and contaminate the broth, as the pressure inside the coil is typically higher than the pressure in the broth. The installation of coil banks inside the fermentor also impacts vessel cleanability. The coils introduce blinds spots and provide crevices where contaminants may accumulate. The coil banks may also negatively impact broth mixing and mass transfer, which ultimately impacts process performance.

External loop cooling can provide even higher heat transfer coefficients and more surface area than internal coils, as the size and number of external heat exchangers can be adjusted as necessary. Provided delta T is sufficient (fermentation temperature ≥ 35 o C), this allows for cooling tower water to be used as the cooling medium and eliminates the need for a chiller, which results in capital and operating cost savings. Because external cooling loops decouple cooling capacity from reactor scale and geometry, larger vessel volumes may be used. Larger vessels also yield significant capital cost advantages. One disadvantage of external cooling loops is the addition of a centrifugal pump, heat exchanger, and extra flanged connections that pose contamination risks. The aseptic design and maintenance of the external loop equipment are an important consideration to ensure process reliability. Heat exchanger gasket materials should be carefully chosen for material compatibility and robustness. The centrifugal broth pump should have double mechanical seals that are sterilized with steam and operated with sterile steam condensate. The loop should also be designed to drain completely during CIP/SIP procedures to facilitate cleaning and sterilization. Furthermore, the operating pressure in the loop should be set high enough to ensure any leaks flow out of the sterile boundary. In addition to sterility concerns, the impact of temperature differential, higher shear forces, and anoxia in the external loop on the health and performance of the production microbe must be considered. For example, exposing the cells in the loop to colder temperatures for longer residence times may result in cold shock and negatively impact strain performance. The high broth pumping rate also exposes the cells to higher shear forces, which may result in cell lysis and loss of productive cell mass. On the other hand, the high pumping rate will actually increase the oxygen mass transfer coefficient (kLa). Anoxia in the cooling loop can be avoided if sufficient gas bubbles are entrained in the circulating broth and the loop residence time is properly managed. Failure to properly design the loop in the case of oxygen-sensitive microbes may negatively impact metabolism.

The use of external cooling loops will likely be necessary to achieve the lowest capital and operating costs. Considering the risks outlined above, Genomatica recommends performing lab and pilot studies to test the impact of loop conditions (temperature differential, residence time,

and oxygenation) on the growth and production of the host microbe to aid in the design of the loop system. If any significant performance deviations are observed then strain engineering solutions may also be considered. Genomatica has in-house capabilities for external loop scaledown testing that NREL could leverage during the process development phase of the project. Additionally, there are contract facilities available that have external loop reactors at pilot and demonstration scales that could be used to demonstrate process performance and facilitate process scale-up. For instance, ARD (Pomacle, France) has a 180 m 3 stirred tank reactor with aseptic external cooling loop that was used during the scale-up and demonstration of BioAmber's succinic acid production process.

It is also important to note that there are several examples of commercial scale production fermentors operating today that employ external cooling loops. For example, Amyris' production facility in Brotas, Brazil employs bubble column fermentors with external cooling loops for yeast production of farnesene. The heat exchangers and cooling loop return piping can be seen at the bottom of the fermentors in Figure 7 below.

Figure 7: Amyris' facility in Brotas, Brazil uses bubble columns with external cooling loops (22). Source: Amyris, Inc.

<!-- image -->

## Bioreactor Operating Mode

There are several different operating modes that may be employed for fermentation-based production processes, including batch, fed-batch, semi-continuous (also known as fill-and-draw), and continuous. Klaas van't Riet and Johannes Tramper's Basic Bioreactor Design may be referenced for further detail regarding these different processing strategies (3). Briefly, semicontinuous fill-and-draw operation involves harvesting a percentage of culture from the end of a production batch for downstream processing, while leaving behind a portion of the culture to commence the next production stage (forgoing cleaning and sterilization procedures). Fresh,

sterile, pre-conditioned media and substrate are aseptically added to the remaining culture to begin the next production cycle. For continuous operation, fermentation broth is continuously harvested from the vessel for downstream process, while sterile media and substrate are continuously fed to the vessel to maintain a constant volume.

Operating the fermentation process in semi-continuous or continuous mode can increase the effective reactor productivity, and these modes should be evaluated in addition to fed-batch operation. Implementing these modes of operation can have a significant impact on plant capacity or the volume and number of fermentors required to achieve target plant capacity, which ultimately impacts production costs. Secondary benefits of these operational modes include reduction in total time dedicated to vessel turnaround, reduced physical stress on equipment due to less frequent sterilization cycles, reduction in the number of seed fermentations, reduction in the number of seed vessels required, and reduction in operator involvement and operator-related errors. One could also argue the reduction in operator involvement inherently reduces the risk of contamination and improves process reliability. However, in (semi)continuous operation there is more opportunity for contamination to develop due to extended process time. In that sense, contamination events in a (semi)continuous mode can be more problematic than in short-cycle batch mode.

Although the benefits of these operational modes are significant, there are some key process and design considerations that must be addressed in order for these operational modes to work effectively. For semi-continuous (fill-and-draw) and continuous operations, a separate aseptic day vessel may be required for media conditioning (adjusting to target pH, temperature, and concentration) prior to charging into a fermentor with active culture. This procedure is done to avoid shocking or killing the live cells. Alternatively, media conditioning can be done in-line between the sterilizer and fermentation distribution header via injection of sterile water for dilution and base for pH adjustment, followed by a static mixer for blending. An in-line heat exchanger can be used to reduce the media temperature to the target range. In-line conditioning comes with inherent operational risks. For instance, if equipment failure or operator error results in unconditioned media deactivating live culture, then significant production delays can occur while new seed is generated. On the other hand, in-line conditioning leads to significant cost savings by eliminating the need for large aseptic day vessels.

In addition to process considerations, there are some key features of the production host microbe that must be considered for (semi)continuous operational modes. Due to the extended processing time, additional propagation of the production microbe is required. Therefore, the host strain must be genetically stable for the anticipated number of generations expected at scale, as any instability may result in loss of production. Genome stability can be assessed using multi-stage flask propagation followed by whole genome sequencing. For semi-continuous fill-and-draw operation, the host microbe must be robust under repeated substrate depletion cycles, as the broth must be completely depleted of substrate prior to harvest to avoid yield losses. For continuous operation, the host microbe must perform well under substrate-limited conditions, as broth is continuously withdrawn from the fermentor. Alternatively, substrate could be separated downstream and recycled back to the process; however, this mode of operation would most likely increase production costs.

## Seed Train Design

The seed train is used to propagate cell mass for the inoculation of production fermentors, and there are several important design details that must be considered. The scale and number of seed fermentors are determined by the scale and number of production fermentors; the target final cell mass concentration in the seed fermentor; the target starting cell mass concentration in the production fermentor; the mode of operation of the production fermentor; the mode of operation of the seed fermento;, oxygen and heat transfer limitations in the seed fermentor; the specific growth rate of the production microbe; and the cell mass yield on oxygen of the production microbe.

From a production standpoint, it is advantageous to maximize the use of seed fermentor capacity and produce as much biocatalyst as possible during the time allotted for the seed fermentation phase. Front loading more cell mass into the production fermentor reduces the time required for cell mass generation during the early stages of the production fermentation, which can have a significant impact on the productivity of the process. For instance, doubling the starting cell mass concentration in the production fermentor eliminates one doubling from the early aerobic growth phase, which can shave several hours off of the production fermentation time depending on the microbe growth rate (see Figure 8 below). A higher starting cell mass concentration in the production fermentor requires a larger seed fermentor (larger volumetric transfer into production fermentor) or a higher final cell density in the seed culture (which also requires higher oxygen and heat transfer capabilities in the seed fermentor). Either way, more cell mass must be generated, requiring more seed propagation time.

## Doubling Time vs. Growth Rate

Seed Time vs. Growth Rate 1

<!-- image -->

Figure 8: Impact of microbe growth rate on seed fermentation time

<!-- image -->

- 1 Seed working volume = 80 m 3 , inoculated from single flask, 20 doublings to achieve target final biomass = 16 g dcw/L.

The growth rate of the production microbe is an important factor that must be considered in the design of the seed train, especially if the total seed propagation time exceeds the total production fermentation time (including fermentor turnaround). Figure 8 above demonstrates the impact of microbe growth rate on seed fermentation times for a 100 m 3 seed vessel used to inoculate a 1,000 m 3 production vessel. In order to maximize utilization and avoid downtime of the production fermentors, the longest seed propagation phase must always be shorter than the

production phase. For slow growing production strains, this means a multi-stage seed propagation approach is likely required in which cell mass is scaled up using multiple seed fermentors in a staggered train. Staggering of seed stages allows for turnaround activities, including cleaning, sterilization, and media charging and conditioning procedures, to be conducted concurrent to seed growth. The downside of multiple seed stages is the additional capital and operating costs for extra vessels, and the inherent process risks associated with additional process steps and transfers (i.e., increased operational complexity). Consequently, a microbe selected for rapid growth during the seed stages will reduce complexity and cost by minimizing the number of seed stages and fermentors.

One useful operating strategy to circumvent seed limitations is to use a semi-continuous (filland-draw) operational mode for the seed process. Fill-and-draw operation involves removing a percentage of the inoculum at the end of the seed propagation phase for inoculation of the production reactor, while leaving behind a portion of the seed to inoculate the next seed stage (forgoing cleaning and sterilization procedures). Fresh, sterile, pre-conditioned media is aseptically added to the remaining inoculum in the seed vessel to begin the next seed stage. This seed stage, which is typically much shorter due to a higher starting cell mass concentration, is subsequently used to inoculate the next production fermentor. This mode of operation requires pre-conditioning of sterile media prior to addition to the residual inoculum in the seed vessel. Fill-and-draw operations can be repeated numerous times, allowing a single seed fermentor to inoculate multiple production fermentors using a staggered batch schedule. It is important to note that the total number of generations must be considered when implementing fill-and-draw seed operations to ensure genetic stability of the production microbe throughout the process. Laboratory experiments should be conducted to simulate the total number of generations and demonstrate sustained biocatalyst productivity for the desired number of fill-and-draw cycles.

Fill-and-draw seed operation is advantageous because it typically reduces the total number of seed fermentors required for inoculation of production fermentors, reducing capital costs. It also reduces the fraction of operational time dedicated to seed fermentor turnaround and the total number of CIP and SIP cycles, reducing operating costs and increasing cell mass production capacity. Conversely, fill-and-draw seed operations increase susceptibility to contamination due to increased system complexity and more transfer operations. There is also an increased risk of production loss in the event of a seed contamination as multiple production fermentors are inoculated from a single seed vessel.

The design considerations outlined above for bioreactor type and cooling methodology also apply for the design of the seed train. The primary driver for the seed reactor type and cooling methodology selections is the required oxygen transfer rate, which is driven by the target final cell mass concentration and the cell mass yield on oxygen. Broth physical properties, including temperature, pressure, and viscosity, must also be considered as these impact the heat and mass transfer calculations.

## Recommendations

Based on the feedback provided above, Genomatica recommends making the following changes to NREL's current model:

## Model:

- · Use compartment model approach
- · Add mass transfer calculations for stirred tank reactors
- · Integrate black-box kinetic model for oleaginous yeast
- · Add calculations for characteristic times and gradients

## Strain:

- · Thermotolerant yeast (≥35 o C)
- · Maximum specific growth rate ≥0.3 hr -1
- · Product excretion
- · Specific productivity ≥0.058 mmol product/g dcw/hr (≥0.05 g product/g dcw/hr)
- · Ability to co-utilize recycled glycerol with biomass feedstock

## Bioreactors:

- · 8 x 2,000 m 3 production fermentors 1
- · 2 x 200 m 3 seed fermentors 1
- · Bubble column type reactors (seed and production) 2
- · External loop cooling with cooling tower water

## Process:

- · Peak volumetric OUR of 100 mol/m 3 /hr in production fermentors 2
- · Peak volumetric OUR of 150 mol/m 3 /hr in seed fermentors 2
- · Fermentation temperature ≥35 o C
- · Semi-continuous operation for production fermentors (minimum 5 cycles)
- · Cell mass retention (minimum 80% per cycle)

## References

- 1. National Renewable Energy Laboratory, Statement of Work, 'Consultancy on LargeScale Submerged Aerobic Cultivation Process Design,' Dec 21, 2015.
- 2. D. Humbird, R. Davis, J.D. McMillan, Aeration Costs in Stirred-Tank and Bubble Column Bioreactors, Biochemical Engineering Journal, submitted.
- 3. K. van't Riet, J. Tramper, in Basic Bioreactor Design , New York: Marcel Dekker, Inc., 1991, ch. 2.3, pp. 245-250, 294.
- 4. K. van't Riet, R. G. J. M. van der Laans, 'Mixing in bioreactor vessels,' in Comprehensive Biotechnology , 2 nd ed., Amsterdam, Netherlands: Elsevier, 2011, ch. 2.07, pp. 63-80.
- 5. Online source: https://en.wikipedia.org/wiki/Monod\_equation
- 6. J. J. Heijnen, 'The process reaction for bioprocess design: a thermodynamic approach,' presented at the Advanced Course Bioprocess Design, Delft, Netherlands, May 2014.
- 7. J. J. Heijnen, J. A. Roels, A. H. Stouthamer, 'Application of balancing methods in modeling the penicillin fermentation,' Biotechnology and Bioengineering , vol. 21, pp. 2175-2201, 1979.
- 8. J. J. Heijnen, 'Impact of thermodynamic principles in systems biology,' Advanced Biochemical Engineering and Biotechnology , vol. 121, pp. 139-162, 2010.
- 9. H. F. Cueto-Rojas, 'Thermodynamics-based design of microbial cell factories for anaerobic product formation,' Trends in Biotechnology , vol. 33, pp. 534-546, 2015.
- 10. W. M. Van Gulik et al., 'Application of metabolic flux analysis for the identification of metabolic bottlenecks in the biosynthesis of penicillin -G,' Biotechnology and Bioengineering , vol. 68, pp. 602-618, 2000.
- 11. W. M. Van Gulik et al., 'Energetics of growth and penicillin production in a highproducing strain of Penicillium chrysogenum,' Biotechnology and Bioengineering , vol. 72, pp. 185-193, 2001.
- 12. Online source: http://biotechnologycourses.nl/courses/bioprocess-design-course/
- 13. C. Ratledge, 'The role of malic enzyme as the provider of NADPH in oleaginous microorganisms: a reappraisal and unsolved problems,' Biotechnology Letters , vol. 36, pp. 1557-1568, 2014.
- 14. L. Casepta et al. 'Altered sterol composition renders yeast thermotolerant,' Science , vol. 346, pp. 75-78, 2014.
- 15. Online source: http://www.aafco.org/
- 16. S. P. Sigurdson, C. W. Robinson, in Developments in Industrial Microbiology , vol. 18, pp. 529-547, 1977.
- 17. J. C. Merchuk et al., 'Why use bubble-column bioreactors?,' Trends in Biotechnology , vol. 12, pp. 501-509, 1994.
- 18. N. Kantarci et al., 'Bubble column reactors,' Process Biochemistry , vol. 40, pp. 22632283, 2005.
- 19. K. Schugerl, 'Comparison of different bioreactor performances,' Bioprocess Engineering , vol. 9, pp. 215-223, 1993.
- 20. J. J. Heijnen, K. van't Riet, 'Mass transfer, mixing and heat transfer phenomena in low viscosity bubble column reactors,' The Chemical Engineering Journal , vol. 23, pp. B21B42, 1984.
- 21. Online source: http://www.viscopedia.com/viscosity-tables/substances/water/

- 22. Online source: http://www.fool.com/investing/general/2014/01/18/5-unbelievable-butreal-technologies-made-possible.aspx
- 23. J. J. Heijnen, 'Scale up/Scale down,' presented at the Advanced Course Bioprocess Design, Delft, Netherlands, May 2014.
- 24. P. M. Doran.  Bioprocess Engineering Principles, 2 nd ed.,United Kingdom: Elsevier, 2013, ch. 2, pp. 160-161.