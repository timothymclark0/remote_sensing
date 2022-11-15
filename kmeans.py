#hi
import numpy as np
import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns 



dataset = pd.read_csv('Mall_Customers.csv')
print(dataset.head())
print(dataset.shape)
#sns.distplot(dataset['Annual Income (k$)'],kde=False,bins=50)
#sns.regplot(x='Annual Income (k$)', y="Spending Score (1-100)", data=dataset)
#plt.show()
#input()

hival = dataset.filter(["Annual Income (k$)", "Spending Score (1-100)"],axis = 1)
print(hival.head())

km_model = KMeans(n_clusters=4)