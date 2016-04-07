import statistician as stat

conf = stat.load_configuration()
datapath = conf['DATA']['path']
data = stat.DataSet.load_all(datapath)

print(data)