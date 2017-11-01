import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
color = sns.color_palette()

print("please wait. importing...")
data = pd.read_excel("retail_dataset.xlsx")

print("importing finished.")

data['Total_Price'] = data['Quantity']*data['UnitPrice']

data = data[data.Quantity > 0]
data = data[data.UnitPrice > 0]
data = data[data.iloc[:, :] != '']

data['date'] = data['InvoiceDate'].dt.date.astype(str)
data['date'].replace(regex=True,inplace=True,to_replace=r'-',value=r'')
data['date'] = data['date'].map(lambda x: str(x)[:-2])
data.date = pd.to_numeric(data.date, errors='coerce')



Cust_country=data[['CustomerID', 'Country']].drop_duplicates()
Cust_country_count=Cust_country.groupby(['Country'])['CustomerID'].aggregate('count').reset_index().sort_values(by='CustomerID', ascending=0)


country=list(Cust_country_count['Country'])
Cust_id=list(Cust_country_count['CustomerID'])
plt.figure(figsize=(12,8))
sns.barplot(country, Cust_id, alpha=0.8, color=color[2])
plt.xticks(rotation='60')
plt.show()

#this shows that UK has the hightest number of customers followed by germany and france.

#RFM

#recency

Cust_date_UK=data[data['Country']=="United Kingdom"]
Cust_date_UK=Cust_date_UK[['CustomerID','date']].drop_duplicates()

def recency(row):
    if row['date'] > 201110:
        val = 5
    elif row['date'] <= 201110 and row['date'] > 201108:
        val = 4
    elif row['date'] <= 201108 and row['date'] > 201106:
        val = 3
    elif row['date'] <= 201106 and row['date'] > 201104:
        val = 2
    else:
        val = 1
    return val


Cust_date_UK['Recency_Flag'] = Cust_date_UK.apply(recency, axis=1)
Cust_date_UK = Cust_date_UK.groupby("CustomerID",as_index=False)["Recency_Flag"].max()

plt.figure(figsize=(12,8))
sns.countplot(x="Recency_Flag", data=Cust_date_UK, color=color[1])
plt.ylabel('Count', fontsize=15)
plt.xlabel('Recency_Flag', fontsize=15)
plt.xticks(rotation='vertical')
plt.title("Frequency of Recency_Flag", fontsize=20)
plt.show()

#frequency

Cust_freq=data[['Country','InvoiceNo','CustomerID']].drop_duplicates()
#Calculating the count of unique purchase for each customer
Cust_freq_count=Cust_freq.groupby(["Country","CustomerID"])["InvoiceNo"].aggregate("count").reset_index().sort_values(by='InvoiceNo', ascending=0)
Cust_freq_count_UK=Cust_freq_count[Cust_freq_count['Country']=="United Kingdom"]
unique_invoice=Cust_freq_count_UK[['InvoiceNo']].drop_duplicates()
# Dividing in 5 equal parts
unique_invoice['Frequency_Band'] = pd.qcut(unique_invoice['InvoiceNo'], 5)
unique_invoice=unique_invoice[['Frequency_Band']].drop_duplicates()


def frequency(row):
    if row['InvoiceNo'] <= 13:
        val = 1
    elif row['InvoiceNo'] > 13 and row['InvoiceNo'] <= 25:
        val = 2
    elif row['InvoiceNo'] > 25 and row['InvoiceNo'] <= 38:
        val = 3
    elif row['InvoiceNo'] > 38 and row['InvoiceNo'] <= 55:
        val = 4
    else:
        val = 5
    return val


Cust_freq_count_UK['Freq_Flag'] = Cust_freq_count_UK.apply(frequency, axis=1)
plt.figure(figsize=(12,8))
sns.countplot(x="Freq_Flag", data=Cust_freq_count_UK, color=color[1])
plt.ylabel('Count', fontsize=15)
plt.xlabel('Freq_Flag', fontsize=15)
plt.xticks(rotation='vertical')
plt.title("Frequency of Freq_Flag", fontsize=20)
plt.show()


#monetary


#Calculating the Sum of total monetary purchase for each customer
Cust_monetary = data.groupby(["Country","CustomerID"])["Total_Price"].aggregate("sum").reset_index().sort_values(by='Total_Price', ascending=0)
Cust_monetary_UK=Cust_monetary[Cust_monetary['Country']=="United Kingdom"]
unique_price=Cust_monetary_UK[['Total_Price']].drop_duplicates()
unique_price=unique_price[unique_price['Total_Price'] > 0]
unique_price['monetary_Band'] = pd.qcut(unique_price['Total_Price'], 5)
unique_price=unique_price[['monetary_Band']].drop_duplicates()

def monetary(row):
    if row['Total_Price'] <= 243:
        val = 1
    elif row['Total_Price'] > 243 and row['Total_Price'] <= 463:
        val = 2
    elif row['Total_Price'] > 463 and row['Total_Price'] <= 892:
        val = 3
    elif row['Total_Price'] > 892 and row['Total_Price'] <= 1932:
        val = 4
    else:
        val = 5
    return val

Cust_monetary_UK['Monetary_Flag'] = Cust_monetary_UK.apply(monetary, axis=1)

plt.figure(figsize=(12,8))
sns.countplot(x="Monetary_Flag", data=Cust_monetary_UK, color=color[1])
plt.ylabel('Count', fontsize=15)
plt.xlabel('Monetary_flag', fontsize=15)
plt.xticks(rotation='vertical')
plt.title("Frequency of Monetary_flag", fontsize=20)
plt.show()

#finding rfm

Cust_UK_All=pd.merge(Cust_date_UK,Cust_freq_count_UK[['CustomerID','Freq_Flag']],on=['CustomerID'],how='left')
Cust_UK_All=pd.merge(Cust_UK_All,Cust_monetary_UK[['CustomerID','Monetary_Flag']],on=['CustomerID'],how='left')

#finding finding final score i.e sum of all flags

recency_weight = 5
frequency_weight = 4
monetary_weight = 3

Cust_UK_All['score'] = recency_weight*Cust_UK_All['Recency_Flag'] + frequency_weight*Cust_UK_All['Freq_Flag'] + monetary_weight*Cust_UK_All['Monetary_Flag'];


Cust_UK_All = Cust_UK_All.sort_values(by='score', ascending=0)
print(Cust_UK_All)