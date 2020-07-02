import pandas as pd

df = pd.read_excel('Recommended prices.xlsx')

pivotica = df.pivot_table(index=['Manufacturer', 'Model', 'Memory', 'Company', 'Tariff Name'], columns=['Timestamp'],
                          values='Final HS price')

pivotica.to_excel("pivot.xlsx")
