import pandas as pd

def wals(column, filename):
	return (pd
		.read_csv(filename, sep='\t', header=5)
		['wals code,name,latitude,longitude,genus,family,description'.split(',')]
		.rename(columns={'description':column, 'wals code':'code'})
	)

tables = [
	('Vso',   'wals/verb-subject-object.tsv'),
	('Vso2',  'wals/verb-subject-object-alternatives.tsv'),
	('Vom',   'wals/verb-object-modifier.tsv'),
	('Vson',  'wals/negation-verb-subject-object.tsv'),
	('Vson2', 'wals/negation-verb-subject-object-nonstandard.tsv'),
	('Vn',    'wals/negation-verb.tsv'),
	('Vsoq',  'wals/question-of-polarity-marker-position.tsv'),
	('Vsow',  'wals/question-of-content-marker-position.tsv'),
	('Vsow2', 'wals/question-of-content-nonstandard-order.tsv'),
	('Np', 'wals/noun-adposition.tsv'),
	('Nr', 'wals/noun-relative.tsv'),
	('Ng', 'wals/noun-genitive.tsv'),
	('Nd', 'wals/noun-demonstrative.tsv'),
	('Nn', 'wals/noun-numeral.tsv'),
	('Na', 'wals/noun-adjective.tsv'),
]

df = wals(*tables[0])
for i,(column,filename) in enumerate(tables[1:]):
	df = df.merge(
		wals(column, filename)[['code',column]], 
		how='outer', on='code', suffixes=(None,None))

df.to_csv('wals-merged.tsv', sep='\t')

df = df.loc[df.name.str.len()>0]

df.Vso = df.Vso.str.replace('No dominant order','*')
df.Vso = df.Vso.str.replace('SOV','soV')
df.Vso = df.Vso.str.replace('SVO','sVo')
df.Vso = df.Vso.str.replace('VSO','Vso')
df.Vso = df.Vso.str.replace('VOS','Vos')
df.Vso = df.Vso.str.replace('OVS','oVs')
df.Vso = df.Vso.str.replace('OSV','osV')

df.Vso2 = df.Vso2.str.replace('No dominant order','')
df.Vso2 = df.Vso2.str.replace('SOV or SVO','soVo')
df.Vso2 = df.Vso2.str.replace('SOV or VOS','soVos')
df.Vso2 = df.Vso2.str.replace('SOV or VSO','soVso')
df.Vso2 = df.Vso2.str.replace('SOV or OVS','soVs')
df.Vso2 = df.Vso2.str.replace('SVO or VSO','sVso')
df.Vso2 = df.Vso2.str.replace('VSO or VOS','Vsos')
df.Vso2 = df.Vso2.str.replace('SVO or VOS','sVos')

df.Vom = df.Vom.str.replace('No dominant order','')
df.Vom = df.Vom.str.replace('O','o')
df.Vom = df.Vom.str.replace('X','m')

df.Vson = df.Vson.str.replace('More than one position','')
df.Vson = df.Vson.str.replace('MorphNeg','')
df.Vson = df.Vson.str.replace('ObligDoubleNeg','')
df.Vson = df.Vson.str.replace('OptDoubleNeg','')
df.Vson = df.Vson.str.replace('OptSingleNeg','')
df.Vson = df.Vson.str.replace('Other','')
df.Vson = df.Vson.str.replace('S','s')
df.Vson = df.Vson.str.replace('O','o')
df.Vson = df.Vson.str.replace('(Neg)','n')
df.Vson = df.Vson.str.replace('Neg','n')

df.Vn = df.Vn.str.replace('ObligDoubleNeg','nVnꜝ')
df.Vn = df.Vn.str.replace('OptDoubleNeg','nVnˀ')
df.Vn = df.Vn.str.replace('OptTripleNeg','V¹⁰')
df.Vn = df.Vn.str.replace('Type 1','NegV')
df.Vn = df.Vn.str.replace('Type 2','VNeg')
df.Vn = df.Vn.str.replace('Type 3','[Neg-V]')
df.Vn = df.Vn.str.replace('Type 4','[V-Neg]')
df.Vn = df.Vn.str.replace('[V-Neg]','Vⁿ')
df.Vn = df.Vn.str.replace('[Neg-V]','ⁿV')
df.Vn = df.Vn.str.replace('VNeg','Vn')
df.Vn = df.Vn.str.replace('NegV','nV')
df.Vn = df.Vn.str.replace('S','s')
df.Vn = df.Vn.str.replace('O','o')
df.Vn = df.Vn.str.replace('(Neg)','n')
df.Vn = df.Vn.str.replace('Neg','n')
df.Vn = df.Vn.str.replace('Negative Tone','\u1de0')
df.Vn = df.Vn.str.replace('nV / Vn','nVn')
df.Vn = df.Vn.str.replace('nV / ⁿV','nⁿV')
df.Vn = df.Vn.str.replace('nV / Vⁿ','nVⁿ')
df.Vn = df.Vn.str.replace('Vn / ⁿV','ⁿVn')
df.Vn = df.Vn.str.replace('Vn / Vⁿ','Vⁿn')
df.Vn = df.Vn.str.replace('ⁿV / Vⁿ','ⁿVⁿ')

df.Vsoq = df.Vsoq.str.replace('Initial','qS')
df.Vsoq = df.Vsoq.str.replace('Final','Sq')
df.Vsoq = df.Vsoq.str.replace('In either of two positions','')
df.Vsoq = df.Vsoq.str.replace('No question particle','')
df.Vsoq = df.Vsoq.str.replace('Second position','')
df.Vsoq = df.Vsoq.str.replace('Other position','')

df.Vsow = df.Vsow.str.replace('Initial interrogative phrase','wS')
df.Vsow = df.Vsow.str.replace('Not initial interrogative phrase','S')
df.Vsow = df.Vsow.str.replace('Mixed','')

df.Nr = df.Nr.str.replace('Mixed','rNr')
df.Nr = df.Nr.str.replace('Adjoined',' N³')
df.Nr = df.Nr.str.replace('Internally headed',' N⁵')
df.Nr = df.Nr.str.replace('Doubly headed',' N⁹')
df.Nr = df.Nr.str.replace('Correlative',' N⁸')
df.Nr = df.Nr.str.replace('Relative clause-Noun','rN ')
df.Nr = df.Nr.str.replace('Noun-Relative clause',' Nr')

df.Ng = df.Ng.str.replace('No dominant order','gNg')
df.Ng = df.Ng.str.replace('Genitive-Noun','gN ')
df.Ng = df.Ng.str.replace('Noun-Genitive',' Ng')

df.Nn = df.Nn.str.replace('No dominant order','#N#')
df.Nn = df.Nn.str.replace('Numeral only modifies verb',' N⁶')
df.Nn = df.Nn.str.replace('Numeral-Noun','#N ')
df.Nn = df.Nn.str.replace('Noun-Numeral',' N#')

df.Na = df.Na.str.replace('No dominant order','aNa')
df.Na = df.Na.str.replace('Adjective-Noun','aN ')
df.Na = df.Na.str.replace('Noun-Adjective',' Na')
df.Na = df.Na.str.replace('Only internally-headed relative clauses','N⁷')

df.Nd = df.Nd.str.replace('Mixed','dNd')
df.Nd = df.Nd.str.replace('Demonstrative prefix','ᵈN ')
df.Nd = df.Nd.str.replace('Demonstrative suffix',' Nᵈ')
df.Nd = df.Nd.str.replace('Demonstrative-Noun','dN ')
df.Nd = df.Nd.str.replace('Noun-Demonstrative',' Nd')
df.Nd = df.Nd.str.replace('Demonstrative before and after N','dNdꜝ')

df.Np = df.Np.str.replace('No adpositions',' N ')
df.Np = df.Np.str.replace('No dominant order','pNp')
df.Np = df.Np.str.replace('Postpositions',' Np')
df.Np = df.Np.str.replace('Prepositions','pN ')
df.Np = df.Np.str.replace('Inpositions','pNp⁴')

df.Vso = df.Vso.str.cat(df.Vso2, na_rep='')
df.Vso = df.Vso.str.replace('* ',' ')
df.Vso = df.Vso.str.replace('*s','s')
df.Vso = df.Vso.str.replace('*V','V')
df.Vso = df.Vso.str.replace('*o','o')

df.Vson2 = df.Vson2.str.cat(df.Vson2, na_rep='')
df.Vson2 = df.Vson2.str.replace('[Neg-V]','ⁿV')
df.Vson2 = df.Vson2.str.replace('[V-Neg]','Vⁿ')
df.Vson2 = df.Vson2.str.replace('(Neg)','n')
df.Vson2 = df.Vson2.str.replace('Neg','n')
df.Vson2 = df.Vson2.str.replace('S','s')
df.Vson2 = df.Vson2.str.replace('O','o')

df['Vsom'] = df.Vso
df.Vsom = df.Vsom.str.cat(df.Vom, na_rep='', sep=' ')
df.Vsom = df.Vsom.str.replace('Vso Vom','Vsom')
df.Vsom = df.Vsom.str.replace('Vos Vom','Voms')
df.Vsom = df.Vsom.str.replace('Von Vom','Vomn')
df.Vsom = df.Vsom.str.replace('so Vom','som')
df.Vsom = df.Vsom.str.replace('Vs oVm','Vms²')
df.Vsom = df.Vsom.str.replace('Vo Vom','Vom')
df.Vsom = df.Vsom.str.replace('oV moV','moV')
df.Vsom = df.Vsom.str.replace('oV omV','omV')
df.Vsom = df.Vsom.str.replace('oV oVm','oVm')
df.Vsom = df.Vsom.str.replace('* o','*o')

def guard(x,fallback):
	return x if x and type(x)==str else fallback

def maybe(x,f):
	return f(x) if x and type(x)==str else x

df['Vson'] = [
	guard(row['Vson2'],
		guard(row['Vson'],
			guard(row['Vso'],'')
				.replace('V',
					guard(
						maybe(row['Vn'],lambda x:x+'¹'),
					'V')
					.replace('ⁿV¹','ⁿV')
					.replace('Vⁿ¹','Vⁿ')
				)
		)
	).split(' but ')[-1]
	for row in df.to_dict('records')
]

df['Vsoq'] = [
	guard(row['Vsoq'], '')
		.replace('S', guard(row['Vso'],'S').strip())
	for row in df.to_dict('records')
]

df['Vsow'] = [
	guard(row['Vsow'], '')
		.replace('S', 
			guard(row['Vsow2'], 
				guard(row['Vso'],'S')).strip()
		)
	for row in df.to_dict('records')
]

df['Nprgdna'] = [
	('N'
		.replace('N', guard(row['Np'],' N '))
		.replace('N', guard(row['Nr'],' N '))
		.replace('N', guard(row['Nd'],' N '))
		.replace('N', guard(row['Ng'],' N '))
		.replace('N', guard(row['Nn'],' N '))
		.replace('N', guard(row['Na'],' N '))
	)
	for row in df.to_dict('records')
]
df = df.drop(['N'+c for c in 'prgdna'],axis=1)

df['pattern'] = ''
df.loc[df.family=='Indo-European', 'pattern'] = 'MT'
df.loc[df.family=='Uralic', 'pattern'] = 'MT'
df.loc[df.family=='Yukaghir', 'pattern'] = 'MT'
df.loc[df.family=='Tungusic', 'pattern'] = 'MT'
df.loc[df.family=='Altaic', 'pattern'] = 'MT'
df.loc[df.family=='Kartvelian', 'pattern'] = 'MT'
df.loc[df.family=='Chukotko-Kamchatkan', 'pattern'] = 'MT'

df.loc[df.family=='Arawakan', 'pattern'] = 'NM'
df.loc[df.family=='Pano-Tacanan', 'pattern'] = 'NM'
df.loc[df.family=='Hokan', 'pattern'] = 'NM'
df.loc[df.family=='Penutian', 'pattern'] = 'NM'
df.loc[df.family=='Kiowa-Tanoan', 'pattern'] = 'NM'
df.loc[df.family=='Uto-Aztecan', 'pattern'] = 'NM'
df.loc[df.family=='Araucanian', 'pattern'] = 'NM'
df.loc[df.family=='Misumalpan', 'pattern'] = 'NM'
df.loc[df.family=='Chibchan', 'pattern'] = 'NM'
df.loc[df.family=='Chapacura-Wanham', 'pattern'] = 'NM'
df.loc[df.family=='Matacoan', 'pattern'] = 'NM'
df.loc[df.family=='Yuman', 'pattern'] = 'NM'
df.loc[df.family=='Maiduan', 'pattern'] = 'NM'
df.loc[df.family=='Mixe-Zoquean', 'pattern'] = 'NM'
df.loc[df.family=='Chibchan', 'pattern'] = 'NM'
df.loc[df.family=='Sahaptian', 'pattern'] = 'NM'
df.loc[df.family=='Wintuan', 'pattern'] = 'NM'
df.loc[df.family=='Karankawa', 'pattern'] = 'NM'
df.loc[df.family=='Aymaran', 'pattern'] = 'NM'
df.loc[df.family=='Puelche', 'pattern'] = 'NM'
df.loc[df.family=='Uru-Chipaya', 'pattern'] = 'NM'
df.loc[df.family=='Huavean', 'pattern'] = 'NM'
df.loc[df.family=='Mixe-Zoque', 'pattern'] = 'NM'

df.loc[df.family=='Sino-Tibetan', 'pattern'] = 'NN'
df.loc[df.family=='Japanese', 'pattern'] = 'NN'
df.loc[df.family=='Korean', 'pattern'] = 'NN'

# df.loc[df.family=='Tai-Kadai', 'pattern'] = 'Austro-Thai'
# df.loc[df.family=='Austronesian', 'pattern'] = 'Austro-Thai'

# df.loc[df.family=='Yeniseian', 'pattern'] = 'Dene-Yeniseian'
# df.loc[df.family=='Na-Dene', 'pattern'] = 'Dene-Yeniseian'



# excludes Vson2 Vso2 Vom Vn
df = df['latitude longitude code name pattern family genus Vso Vsom Vson Vsoq Vsow Nprgdna'.split()]
df = df.sort_values('pattern family genus name'.split())

df.value_counts('Vso Nprgdna'.split()).to_csv('wals-frequencies.tsv', sep='\t')

summary_filename = 'wals-summary.tsv'
df.to_csv(summary_filename, sep='\t')
with open(summary_filename, 'a') as file:
	file.write('''
		Symbols indicate valid positions
		  in a clause or phrase, unless as noted below.
		The order of words on the same side of a noun in a noun phrase
		  is not cataloged, we present in order: prgd#aNa#dgrp
	S	sentence
	V	verb
	s	subject noun phrase
	o	object noun phrase
	n	negative
	ⁿ	negative affix on verb
	◌ᷠ	negative tone on verb
	q 	marker of polarity question
	w 	interrogative phrase (who, what, where. etc.) of content question
	N	noun
	p	preposition/postposition
	r	relative clause
	g	genitive noun phrase
	d	demonstrative
	ᵈ	morphological demonstrative
	#	numeral
	a	adjective
	*	no dominant order
	ꜝ	second demonstrative or negation is required
	ˀ 	second negation is optional
	¹	the placement of negative between subject/object is uncataloged
	²	the placement between modifier and subject is uncataloged
	³	"adjoined", see WALS
	⁴	"inposition", see WALS
	⁵	internally headed
	⁶	numeral only modifies verb
	⁷	no adjectives, only relative clauses
	⁸	"correlative", see WALS
	⁹	"doubly headed", see WALS
	¹⁰	optional triple negative, see WALS
''')
