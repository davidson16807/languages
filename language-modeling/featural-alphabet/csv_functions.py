
def csv_tuples(filename, stripped=' \t\r\n'):
	result = []
	with open(filename) as file:
		for line in file.readlines():
			if not line.strip().startswith('#') and not len(line.strip()) < 1:
				cells = [column.strip(stripped) for column in line.split('\t') ]
				if len(cells) > 1:
					result.append((cells[0], cells[1]))
	return result

def csv_dict(filename, columns, keys):
	result = {}
	with open(filename) as file:
		for line in file.readlines():
			if not line.strip().startswith('#') and not len(line.strip()) < 1:
				cells = [column.strip(' \t\r\n*?') for column in line.split('\t') ]
				row = {columns[i]:cells[i] for i, cell in enumerate(cells) if i < len(columns)}
				value = {column:row[column] for column in row if column not in keys}
				result[tuple(row[key] for key in keys)] = value if len(value) > 1 else list(value.values())[0]
	return result

def dict_function(dict_, sentinel='', fallback=None):
	def result(*keys):
		keys_tuple = tuple(keys)
		return (
			dict_[keys_tuple] if keys_tuple in dict_ else 
			fallback(*keys) if fallback else 
			sentinel
		)
	return result

def curried_dict_function(dict_, sentinel='', fallback=None):
	def result(*keys):
		keys_tuple = tuple(keys)
		result = lambda attribute: dict_[keys_tuple][attribute]
		return (
			result if keys_tuple in dict_ else 
			fallback if fallback else 
			lambda *x:sentinel
		)
	return result
