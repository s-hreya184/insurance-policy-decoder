import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("customer.csv")

#bar plot
plt.bar(df['CustomerID'], df['Age'], color = 'green')
plt.xlabel("Customer ID")
plt.ylabel("Age of Customer")
plt.title("Customer ID vs Age")
plt.show()

# 1] Line Plot
plt.plot(df['CustomerID'], df['Age'], marker= 'o', color = 'green')
plt.xlabel("Customer ID")
plt.ylabel("Age")
plt.title("Line Plot - Customer ID vs Age")
plt.show()


# 2] Scatter Plot
plt.scatter(df['CustomerID'], df['Age'], color='red')
plt.xlabel("Customer ID")
plt.ylabel("Age")
plt.title("Scatter Plot - Customer ID vs Age")
plt.show()


# 3] Histogram
plt.hist(df['Age'], bins=5, color='orange', edgecolor='black')
plt.xlabel("Age")
plt.ylabel("Frequency")
plt.title("Histogram of Ages")
plt.show()

# 4] Pie Chart
age_group = df['Age'].value_counts()

plt.pie(age_group, label = age_group.index, autopct = '%1.1%%')
plt.title("Pie Chart of Age Distribution")
plt.show()

#display first 5 rows
print("\nFirst 5 rows : ")
print(df.head())

#display size of the dataset
print("\nSize of the dataset: ")
print(df.shape)

#display last 5 rows
print("\nLast 5 rows : ")
print(df.tail())

#display column names
print("\nColumns : ")
print(df.columns)

#display column information 
print("\nColumn Information : ")
print(df.info())

#display row information using loc
row_number = int(input("\nEnter a number : "))
print("\nRow information using loc: ")
print(df.loc[row_number])

#display last row using iloc
print("\nRow information using iloc : ")
print(df.iloc[-1])

#create a subset of columns
print("\nDisplay columns: ")
print(list(df.columns))

cols = input("\nEnter columns of your choice seperated by comma : ").split(",")

subset = df[cols]

print("\nSubset of the dataset: ")
print(subset)

#find maximum value
numeric_cols = df.select_dtypes(include = ['int64', 'float64'])

max_val = numeric_cols.max()
print("\nMaximum values : ")
print(max_val)

min_val = numeric_cols.min()
print("\nMinimum values : ")
print(min_val)

mean = numeric_cols.mean()
median = numeric_cols.median()
mode = numeric_cols.mode().iloc[0]

print("\nMean: ")
print(mean)
print("\nMedian : ")
print(median)
print("\nMode : ")
print(mode)

std_var = numeric_cols.std()
var = numeric_cols.var()

print("\nStandard deviation : ")
print(std_var)
print("\nVariance : ")
print(var)

skew = numeric_cols.skew()
print("\nSkewness of the dataset : ")
print(skew)
