

left      = lambda person: f'''<span style="position:relative; left:0.4em; top:0.2em;">{person}</span>'''
center    = lambda person: f'''{person}'''
right     = lambda person: f'''<span style="position:relative; right:0.4em; top:0.2em;">{person}</span>'''

inclusive   = lambda person: f'''<span style="position:relative; left:0.2em;">{person}</span>'''

lowered = lambda hand, face: f'''<span style="font-size: 50%; display: inline-block; width:0; position:relative; left:0.3em; top:0.8em;">{hand}</span>{face}'''
raised = lambda hand, face: f'''<span style="font-size: 50%; display: inline-block; width:0; position:relative; right:0.6em; bottom:0.7em;">{hand}</span>{face}'''
overhead = lambda hand, face: f'''<span style="display: inline-block; width:0; position:relative; bottom:0.8em;">{hand}</span>{face}'''
chestlevel = lambda hand, face: f'''<span style="font-size: 50%; display: inline-block; width:0; position:relative; right:0.7em; top:0em;">{hand}</span>{face}'''

mirror = lambda emoji: f'''<span style="display: inline-block; transform: scale(-1,1)">{emoji}</span>'''
flip = lambda emoji: f'''<span style="display: inline-block; transform: scale(1,-1)">{emoji}</span>'''

singular  = lambda a: a
dual      = lambda a,b: f'''{left(a)}{center(b)}'''
plural    = lambda a,b,c: f'''{left(a)}{center(b)}{right(c)}'''

first   = lambda person: f'{person}🏽'
second  = lambda person: f'{person}🏾'
third   = lambda person: f'{person}🏼'

present = lambda scene: f'''{scene}'''
past    = lambda scene: f'''<span style="filter: sepia(0.8)  drop-shadow(0px 0px 5px black)">{scene}</span>'''
future  = lambda scene: f'''<span style="filter: blur(0.6px) drop-shadow(0px 0px 5px black)">{scene}</span>'''

imperfect  = lambda scene: f'''{scene}<progress style="width: 1em;" max="10" value="7"></progress>'''
perfect  = lambda scene: f'''{scene}<progress style="width: 1em;" max="10" value="10"></progress>'''
aortist  = lambda scene: f'''{scene}'''
perfect_progressive = lambda scene: f'''<span style="filter: sepia(0.3) drop-shadow(0px 0px 2px black)">{scene}<progress style="width: 1em;" max="10" value="10"></progress></span>'''

affirmative = lambda scene: f'''<div><span style="border-radius: 0.5em; padding: 0.3em; background:#ddd; ">{scene}</span></div>'''
negative = lambda scene: f'''<div><span style="border-radius: 0.5em; padding: 0.3em; background: linear-gradient(to left top, #ddd 47%, red 48%, red 52%, #ddd 53%); border-style: solid; border-color:red; border-width:6px;">{scene}</span></div>'''

speech = lambda content, audience, speaker: f'''{content}<sub>{audience}</sub><sup style="color:#ddd;">◥</sup><sub>{speaker}</sub>'''
thought = lambda content, audience, speaker: f'''{content}<sub>{audience}</sub><span style="color:#ddd;">•<sub>•</sub></span><sub>{speaker}</sub>'''
quote = lambda content, audience, speaker: f'''{content}<sup style="padding-left: 0.5em; color:#ddd;">◤</sup><sub>{audience}{speaker}</sub>'''

depiction = lambda content: f'''<div style="font-size:3em; padding: 0.5em;">{content}</div>'''

scene = plural(first('🧍'),first('🧍'),first('🧍'))+plural(third('👨'),third('🧑'),third('🧑'))+inclusive(second('👨'))+dual(first('🧑'),first('👩'))
scene = dual(lowered(first('🙏'), first('👨')), first('👨'))
scene = dual(raised(first('✋'), first('👨')), first('👨'))
scene = dual(chestlevel(first('🤞'), first('💁')), first('👨'))
scene = dual(overhead(first('🙌'), first('👨')), first('👨'))

scene = depiction(
	speech(
		affirmative(past('🧍<span style="font-size:70%">→🔧🔧</span>')),
		plural(third('👨'),third('🧑'),third('🧑')),
		dual(lowered(first('🙏'), first('👨')), first('👨')),
	)
)
scene = depiction(
	speech(
		negative(past('🧍<span style="font-size:70%">→🔧🔧</span>')),
		'',
		dual(lowered(first('🙏'), first('👨')), first('👨')),
	)
)
scene = depiction(
	speech(
		affirmative(future(third('🧍'))),
		second('👨'),
		dual(raised(first('✋'), first('👨')), first('👨'))
	)
)

scene = depiction(
	speech(
		negative(future(third('🧍'))),
		second('👨'),
		dual(raised('?', first('🙍')), first('🙍'))
	)
)

scene = depiction(
	thought(
		affirmative(present(perfect_progressive(third('🧍')))),
		second('👨'),
		# dual(chestlevel(mirror(first('👍')), first('👨')), first('👨'))
		dual(chestlevel((first('✋')), first('🙍')), first('👨'))
		# dual(chestlevel((first('💪')), first('👨')), first('👨'))
	)
)

print(scene)

def tuples_from_csv(filename, delimeter='\t', padding=' \t\r\n'):
	result = []
	with open(filename) as file:
		for line in file.readlines():
			if not line.strip().startswith('#') and not len(line.strip()) < 1:
				result.append([column.strip(padding) for column in line.split(delimeter) ])
	return result

def dict_from_tuples(tuples, columns, keys, values=None):
	result = {}
	for cells in tuples:
		row = {columns[i]:cells[i] for i, cell in enumerate(cells) if i < len(columns)}
		value_columns = values if values else [column for column in row if column not in keys]
		value = {column:row[column] for column in value_columns}
		value = value if len(value) > 1 else list(value.values())[0]
		key = row[keys[0]]
		keys_tuple = tuple(row[key] for key in keys) if len(keys)>1 else row[keys[0]]
		if keys_tuple not in result:
			result[keys_tuple] = value
	return result

mood_list = tuples_from_csv('english/mood-templates.tsv')
mood_lookup = dict_from_tuples(
	mood_list, 
	['mood', 'alternative', 'prephrase', 'presubject', 'postsubject', 
	 'adjective', 'conjugation', 'postphrase', 'explanation'],
	['mood']
)

# verb = 'read'
# for mood_row in mood_list:
# 	mood_name = mood_row[0]
# 	presubject = conjugate(mood_lookup[mood_name]['presubject'], conjugation_key)
# 	postsubject = conjugate(mood_lookup[mood_name]['postsubject'], conjugation_key)
# 	conjugation_key = ('3', 'singular', 'present', mood_lookup[mood_name]['conjugation'])
# 	conjugation = verb if presubject or postsubject else conjugate(verb, conjugation_key) 
# 	text = f'''{prephrase} {presubject} {subject} {postsubject} {conjugation} {postphrase}'''
# 	print(mood)
'''
mood_list = tuples_from_csv('english/conjugations.tsv')
'''