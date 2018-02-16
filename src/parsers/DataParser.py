# This will parse the data from the files Tiep gave Nando.
import pandas
import numpy
import matplotlib.pyplot as plt

df = pandas.read_excel('../../resources/input/data/H1_Dishwasher.xlsx', parse_dates=['start time', 'end time'], index_col='start time')

print(df)
print('-------------------------------------------\n-------------------------------------------\n')

df['unknown'].plot()
plt.show()
