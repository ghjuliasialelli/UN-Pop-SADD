import re
import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None 
##############################################################################################################
# HELPER FUNCTIONS 

def get_bounds(cat) :
    if '+' in cat : lw, up = cat[:-1], np.inf
    else: lw, up = cat.split('-')
    return lw, up

def wrap_bounds(cats) :
    lw_bds, up_bds = [], []
    for cat in cats :
        lw, up = get_bounds(cat)
        lw_bds.append(lw)
        up_bds.append(up)
    return lw_bds, up_bds

def can_be_aggregated(age_label, age_cats) :
    """
    Determines whether the age_label can be obtained from aggregated age categories in age_cats.
    e.g. 65+ can be obtained from aggregating all categories above 65-69 (included)
    """
    lw_bds, up_bds = wrap_bounds(age_cats)
    age_lw_bd, age_up_bd = get_bounds(age_label)
    try : 
        lw_idx = lw_bds.index(age_lw_bd)
        up_idx = up_bds.index(age_up_bd)
        return age_cats[lw_idx : up_idx + 1]
    except : return []

##############################################################################################################
# CORE EXECUTION PROCEDURE

def execute_generation(age_labels, file_name = 'Population_Age_Sex_2020.xlsx') :

    # Load the Population by age and sex (in thousands) data file - PopAgeSex
    pop_age_sex = pd.read_excel('Datasets/PopulationAgeSex.xlsx', sheet_name = 'Data', skiprows = 1).dropna(subset = ['Sex'])
    age_cats = [col for col in pop_age_sex.columns if not re.search('[a-zA-Z]', col)]
    pop_age_sex['Total'] = pop_age_sex[age_cats].sum(axis = 1)

    # Load the Percentage of female/male populations by broad age groups (PercFemalePop/PercMalePop)
    perc_female_pop = pd.read_excel('Datasets/PercFemalePop.xlsx', sheet_name = 'Data', skiprows = 1).dropna(subset = ['Sex'])
    perc_male_pop = pd.read_excel('Datasets/PercMalePop.xlsx', sheet_name = 'Data', skiprows = 1).dropna(subset = ['Sex'])
    broad_age_groups = [col for col in perc_female_pop.columns if not re.search('[a-zA-Z]', col)]

    # Process the data
    # populate the result dataframe with the Location and Sex columns of PopAgeSex
    res_df = pop_age_sex[['Location', 'Sex']]
    # iterate over the age labels we're interested in
    for age_label in age_labels : 
        # if the age label exists in the PopAgeSex age categories, then we can just extract the SADD population data
        if age_label in age_cats : 
            sex_pop = pop_age_sex[age_label]
        # else, if the age label exists in the PercFemalePop/PercMalePop age categories, we need to perform some extra steps
        elif age_label in broad_age_groups :
            sex_pops = []
            # for each of PercFemalePop/PercMalePop, we multiply the SADD population data from PopAgeSex by the percentage
            # data from PercFemalePop/PercMalePop (and divide by 100) to obtain SADD population data (in thousands)
            for sex, sex_data in zip(['Female', 'Male'], [perc_female_pop, perc_male_pop]) :
                sex_pops.append(pop_age_sex[pop_age_sex['Sex'] == sex]['Total'] * sex_data[age_label].values / 100.)
            sex_pop = pd.concat(sex_pops).sort_index(kind = 'merge')
        else : 
            # else, we check if the age label can be obtained from aggregating PopAgeSex age categories 
            age_cats_to_agg = can_be_aggregated(age_label, age_cats)
            # if so, we just sum the matching columns and extract the SADD population data
            if age_cats_to_agg : 
                sex_pop = pop_age_sex[age_cats_to_agg].sum(axis = 1)
            # if not, we raise an Exception
            else :
                raise Exception('Age label {} cannot be infered from the UN Population Data.'.format(age_label))
        res_df[age_label] = sex_pop
    # because the SADD data is expressed in terms of population, we need to apply an extra step to get percentages
    total = pd.Series(pop_age_sex[['Location', 'Total']].groupby(by = ['Location'], sort = False).sum().values.flatten())
    total_pop = pd.concat([total, total]).sort_index(kind = 'merge')
    # we divide each SADD population data by the total in the country and multiply by 100 to obtain SADD percentage data
    res_df[age_labels] = res_df[age_labels].divide(total_pop.values, axis = 0) * 100


    ##############################################################################################################
    # POST-PROCESSING FOR FORMATTING PURPOSES

    df = res_df.copy()
    geo_df = pd.read_excel('Datasets/Geoentities _FR_ES_AR_18052021.xlsx', sheet_name='in')

    # Get all countries in the UN Pop. Data
    df_countries = np.unique(df['Location'].values)
    # the strings need to be stripped because the UN Excel file has extra white-space
    res = np.array([country.strip() for country in df_countries])

    # Creation of a mapping from UN Pop. Data country name to: [iso3, idmc_short_name, GRID_geographical_group]
    mapping = dict()

    # Scan the `idmc_full_name` column of the reference document for matching country names 
    geo_countries = geo_df['idmc_full_name'].values
    inter = np.intersect1d(geo_countries, res)
    diff = np.setdiff1d(res, geo_countries)
    for country in inter : 
        iso3 = geo_df[geo_df['idmc_full_name'] == country]['iso3'].values[0]
        idmc_name = geo_df[geo_df['idmc_full_name'] == country]['idmc_short_name'].values[0]
        grid_region = geo_df[geo_df['idmc_full_name'] == country]['GRID_geographical_group'].values[0]
        mapping[country] = [iso3, idmc_name, grid_region]

    # Scan the `idmc_short_name` column of the reference document for matching country names 
    res = diff # we only look for countries which we didn't find in the previous step
    geo_countries = geo_df['idmc_short_name'].values 
    inter = np.intersect1d(geo_countries, res) 
    diff = np.setdiff1d(res, geo_countries) 
    for country in inter : 
        iso3 = geo_df[geo_df['idmc_short_name'] == country]['iso3'].values[0]
        grid_region = geo_df[geo_df['idmc_short_name'] == country]['GRID_geographical_group'].values[0]
        mapping[country] = [iso3, country, grid_region]

    # The remaining countries need to be handled manually
    # diff = ['China, Hong Kong SAR', 'China, Macao SAR', 'China, Taiwan Province of China',
    #         "Dem. People's Republic of Korea", 'Micronesia (Fed. States of)']
    # note : 'Channel Islands' was discarded because not present in the reference file
    diff = diff[diff != 'Channel Islands']
    df = df[df['Location'].str.contains('Channel Islands') == False]
    manual_diff = ['China, Hong Kong SAR', 'China, Macao SAR', 'China, Taiwan Province of China', "Dem. People's Republic of Korea", 'Micronesia (Fed. States of)']
    manual_iso = ['HKG', 'MAC', 'TWN', 'PRK', 'FSM']
    for country, code in zip(manual_diff, manual_iso): 	
        idmc_name = geo_df[geo_df['iso3'] == code]['idmc_short_name'].values[0]
        grid_region = geo_df[geo_df['iso3'] == code]['GRID_geographical_group'].values[0]
        mapping[country] = [code, idmc_name, grid_region]


    # Populating the result dataframe

    # Basic helper functions to apply to the UN Pop. Data `Location` (ie. country name) column
    def get_iso(name): return mapping[name][0]
    def get_idmc_name(name): return mapping[name][1]
    def get_grid_region(name): return mapping[name][2]

    res_df['Location'] = res_df['Location'].apply(lambda x : x.strip())
    res_df = res_df[res_df['Location'].isin(mapping.keys())]
    res_df['iso3'] = res_df['Location'].apply(get_iso)
    res_df['idmc_short_name'] = res_df['Location'].apply(get_idmc_name)
    res_df['GRID_geographical_group'] = res_df['Location'].apply(get_grid_region)
    res_df.drop(['Location'], axis = 1, inplace = True)

    # We also add a `Total` value for disaggregation by-sex 
    agg_dict = dict()
    agg_dict['Sex'] = lambda x: 'Total'
    for age in age_labels: agg_dict[age] = np.sum
    total_df = res_df.groupby(['iso3', 'idmc_short_name', 'GRID_geographical_group'], as_index = False).agg(agg_dict)
    result_df = pd.concat([res_df, total_df]).sort_values(by = 'idmc_short_name')

    # Save the resulting file
    result_df.to_excel(file_name, index = False)


if __name__ == "__main__" :
    # Age labels to be used for the disaggregation
    age_labels = ['0-4', '0-17', '5-14', '15-24', '25-64', '65+', '0+'] + ['0-1', '5-11', '12-14', '12-16', '15-17']
    execute_generation(age_labels)
