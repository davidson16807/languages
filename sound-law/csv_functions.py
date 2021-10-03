import collections

def tuples_from_csv(filename, delimeter='\t', padding=' \t\r\n'):
	result = []
	with open(filename) as file:
		for line in file.readlines():
			if not line.strip().startswith('#') and not len(line.strip()) < 1:
				result.append([column.strip(padding) for column in line.split(delimeter) ])
	return result

def lines_from_file(filename):
	result = []
	with open(filename) as file:
		for line in file.readlines():
			if not line.strip().startswith('#') and not len(line.strip()) < 1:
				result.append(line.strip())
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

def setdict_from_tuples(tuples, columns, keys, values=None):
	result = collections.defaultdict(set)
	for cells in tuples:
		if len(columns) <= len(cells):
			row = {columns[i]:cells[i] for i, cell in enumerate(cells) if i < len(columns)}
			value_columns = values if values else [column for column in row if column not in keys]
			value = {column:row[column] for column in value_columns}
			value = value if len(value) > 1 else list(value.values())[0]
			keys_tuple = tuple(row[key] for key in keys) if len(keys)>1 else row[keys[0]]
			result[keys_tuple].add(value)
	return result

def listdict_from_tuples(tuples, columns, keys, values=None):
	result = collections.defaultdict(list)
	for cells in tuples:
		row = {columns[i]:cells[i] for i, cell in enumerate(cells) if i < len(columns)}
		value_columns = values if values else [column for column in row if column not in keys]
		value = {column:row[column] for column in value_columns}
		value = value if len(value) > 1 else list(value.values())[0]
		keys_tuple = tuple(row[key] for key in keys) if len(keys)>1 else row[keys[0]]
		result[keys_tuple].append(value)
	return result

# deprecated, use dict_from_tuples(lists_from_csv) instead
def csv_dict(filename, columns, keys):
	return dict_from_tuples(tuples_from_csv(filename), columns, keys)

def function_from_dict(dict_, sentinel='', fallback=None):
	def result(*keys):
		keys_tuple = tuple(keys) if len(keys) > 1 else keys[0]
		return (
			dict_[keys_tuple] if keys_tuple in dict_ else 
			fallback(*keys) if fallback else 
			sentinel
		)
	return result

def curried_function_from_dict(dict_, sentinel='', fallback=None):
	def result(*keys):
		keys_tuple = tuple(keys)
		result = lambda attribute: dict_[keys_tuple][attribute]
		return (
			result if keys_tuple in dict_ else 
			fallback if fallback else 
			lambda *x:sentinel
		)
	return result

def subdomain_image_function_from_dict(dict_):
	def result(keys): 
		return [ dict_[key] for key in keys if key in dict_ ]
	return result

def subdomain_image_function_from_multidict(multidict):
	def result(keys): 
		return [ value for key in keys for value in multidict[key] ]
	return result
