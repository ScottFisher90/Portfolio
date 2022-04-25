#import libraries
import codecademylib3_seaborn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#import and inspect csv data
data = pd.read_csv("country_data.csv")
print(data.head())

#isolate life expectancy column, find, and inspect quantrtiles
life_expectancy = data['Life Expectancy']
life_expectancy_quartiles = np.quantile(life_expectancy, [.25, .5, .75])
print(life_expectancy_quartiles)

#inspect histogram of life expectancy
#plt.hist(life_expectancy)
#plt.show()

#isolate gdp column, and split high and low gdp countries about the median of the of gdp
gdp = data['GDP']
median_gdp = np.median(gdp)
print(median_gdp)
low_gdp = data[data['GDP'] <= median_gdp]
high_gdp = data[data['GDP'] > median_gdp]

#examine the quartiles of the high and low gdp life expectancies
low_gdp_quartiles =  np.quantile(low_gdp['Life Expectancy'], [.25, .5, .75])
print(low_gdp_quartiles)
high_gdp_quantiles = np.quantile(high_gdp['Life Expectancy'], [.25, .5, .75])
print(high_gdp_quantiles)

#assemble final plot
plt.hist(high_gdp["Life Expectancy"], alpha = 0.5, label = "High GDP", bins=30)
plt.hist(low_gdp["Life Expectancy"], alpha = 0.5, label = "Low GDP", bins=30)
plt.xlabel("Age")
plt.ylabel("Number of Countries")
plt.title("Life Expectancy")
plt.legend()
plt.show()
