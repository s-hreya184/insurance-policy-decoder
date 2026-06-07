import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("customer.csv")

plt.bar(df['CustomerID'], df['Age'], color = 'blue')
plt.show()

numeric1 = df.select_dtypes(include = ["int64" , "float64"]).columns[0]

numeric_cols = df[numeric1]

print("\nMaximum : \n", numeric_cols.max())
print("\nMinimum : \n", numeric_cols.min())
print("\nMean : \n", numeric_cols.mean())
print("\nMedian : \n", numeric_cols.median())
print("\nMode : \n", numeric_cols.mode().iloc[0])
print("\nStandard Deviation : \n", numeric_cols.std())
print("\nVariance : \n", numeric_cols.var())
print("\nSkewness : \n", numeric_cols.skew())



print("\nFirst 5 rows : \n", df.head())
print("\nLast 5 rows : \n", df.tail())
print("\nSize : ", df.size)
print("\nColumn Info : \n", df.info())

n = int(input("\nEnter row to search :"))
print("\nUsing loc : ", df.loc[n])

print("\nUsing iloc : ", df.iloc[-1])

print("\nColumns : ", df.columns)

cols = input("Enter columns : ").split(",")

subset = df[cols]

print("\nSubset : ")
print(subset)








        