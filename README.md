## Disaggregation of [UN Population Data](https://population.un.org/wpp/DataQuery/) by broad age groups and sex. Example application to 2020 Conflict stock data.

### Motivation and Methodology
Although relatively little Sex and Age Disaggregated Data (SADD) is available for displacement associated with conflict or disasters, one way to estimate it is to use SADD available at the national level. The United Nations ([United Nations, Department of Economic and Social Affairs, Population Division (2019). World Population Prospects 2019](https://population.un.org/wpp/DataQuery/)) provides such data. Using this data, one has access to the percentage of the population by broad age groups and sex, for each country. Then, for each country for which IDMC has access to displacement data, one can multiply the UN SADD by the total number of IDPs to obtain an estimate of SADD for displacement. Note that this analysis uses national-level statistics derived from census data, that may not reflect how different groups (e.g., men and women, or different age groups) are affected by conflict or disaster displacement situations. You can find more information about the methodology [here](https://github.com/ghjuliasialelli/UN-Pop-SADD/blob/main/Resources/Methodology.pdf).

### Files: 
#### used to obtain the disaggregated data :
- `automatic_generation.py` : script to generate `Population_Age_Sex_2020.xlsx`. 
- `Population_Age_Sex_2020.xlsx` : final result of the disaggregation by broad age groups and sex.
- `Datasets/` : folder containing the files needed to obtain `Population_Age_Sex_2020.xlsx`. 
- `disaggregation.ipynb` : tutorial to generate the result file.
#### used to apply the disaggregated data : 
- `End of 2020 conflict stock by age.xlsx` : example Conflict stock data.
- `age_sex_population_example.ipynb` : tutorial on how to apply the disaggregated data to the 2020 Conflict stock data. 

### Execution
- Click [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ghjuliasialelli/UN-Pop-SADD/HEAD?labpath=disaggregation.ipynb) to generate a disaggregation using the age labels of your choice. 
- To see an example of how to apply the disaggregated population data to stock data, see `age_sex_population_example.ipynb`.

