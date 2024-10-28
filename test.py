from sklearn.preprocessing import MinMaxScaler

allglyphdata = [[0.5,1,1.5,2],[0.5,1,1.5,2],[0.5,1,1.5,2],[0.5,1,1.5,2],[0.5,1,1.5,2],[0.5,1,1.5,2],[0.5,1,1.5,2],[0.5,1,1.5,2],[0.5,1,1.5,2]]
scaler = MinMaxScaler(feature_range=(0,2))
scaler.fit(allglyphdata)
scaled_data = scaler.transform(allglyphdata)

print(allglyphdata)