import pandas as pd

proto_indo_european_vocabulary = pd.read_csv('data/vocabulary/proto-indo-european/oxford-lexicon.tsv', sep='\t')
english_buck_table = pd.read_csv('data/buck-tables/english.tsv', sep='\t')
english_buck_table['0'] = english_buck_table['English'].str.split('|').str[0]
english_buck_table['1'] = english_buck_table['English'].str.split('|').str[1]
english_buck_table['2'] = english_buck_table['English'].str.split('|').str[2]
merged0 = pd.merge(english_buck_table.filter(items=['Id','0']), proto_indo_european_vocabulary, how='left', left_on='0', right_on='English').drop(columns=['English','0'])
merged1 = pd.merge(english_buck_table.filter(items=['Id','1']), proto_indo_european_vocabulary, how='left', left_on='1', right_on='English').drop(columns=['English','1'])
merged2 = pd.merge(english_buck_table.filter(items=['Id','2']), proto_indo_european_vocabulary, how='left', left_on='2', right_on='English').drop(columns=['English','2'])
print(merged0.keys())
merged01 = pd.merge(merged0, merged1, how='left', on='Id')
merged123 = pd.merge(merged01, merged2, how='left', on='Id')
print(merged123.keys())
merged = pd.merge(english_buck_table.filter(['Id','English','Part']), merged123, how='left', on='Id')
dialects = ['Common','Northwest','West Central','Graeco Aryan','Eastern','Central']
for dialect in dialects:
	merged[dialect] = merged[f'{dialect}_x'].astype(str) + '|' + merged[f'{dialect}_y'].astype(str) + '|' + merged[f'{dialect}'].astype(str)
	merged[dialect] = merged[dialect].str.replace('\|?nan\|?','')
merged = merged.filter(items=['Id','English','Part',*dialects])
merged.to_csv('data/buck-tables/proto-indo-european.tsv', sep='\t')