
class RowAnnotation:
    def __init__(self, header_column_names):
        self.header_column_names = header_column_names
    def annotate(self, rows):
        annotations = []
        for row in rows:
            dict_row = dict(zip(self.header_column_names, row))
            annotations.append((dict_row, dict_row))
        return annotations

class CellAnnotation:
    '''
    `CellAnnotation` instances represent a system for storing tabular data 
    that comes up naturally in things like conjugation or declension tables.

    A table has a given number of header rows and header columns.
    When a predifined keyword occurs within the cell contents of a header row or column, 
     the row or column associated with that header is marked as having that keyword 
     for an associated attribute.
    Keywords are indicated by keys within `keyword_to_attribute`.
    Keywords that are not known at the time of execution may be 
     indicated using `header_column_id_to_attribute`, 
     which marks all cell contents of a given column as keywords for a given attribute.

    As an example, if a header row is marked 'green', and 'green' is a type of 'color',
     then `keyword_to_attribute` may store 'green':'color' as a key:value pair.
    Anytime 'green' is listed in a header row or column, 
     all contents of the row or column associated with that header cell 
     will be marked as having the color 'green'.

    `CellAnnotation` converts tables that are written in this manner between 
    two reprepresentations: 
    The first representation is a list of rows, where rows are lists of cell contents.
    The second representation is a list where each element is a tuple,
     (annotation,cell), where 'cell' is the contents of a cell within the table,
     and 'annotations' is a dict of attribute:keyword associated with a cell.
    '''
    def __init__(self, 
            keyword_to_attribute, 
            header_row_id_to_attribute, header_column_id_to_attribute,
            default_attributes):
        self.keyword_to_attribute = keyword_to_attribute
        self.header_column_id_to_attribute = header_column_id_to_attribute
        self.header_row_id_to_attribute = header_row_id_to_attribute
        self.default_attributes = default_attributes
    def annotate(self, rows, header_row_count=None, header_column_count=None):
        header_row_count = header_row_count if header_row_count is not None else len(self.header_row_id_to_attribute)
        header_column_count = header_column_count if header_column_count is not None else len(self.header_column_id_to_attribute)
        column_count = max([len(row) for row in rows])
        column_base_attributes = [{} for i in range(column_count)]
        header_rows = rows[:header_row_count]
        nonheader_rows = rows[header_row_count:]
        for i, row in enumerate(header_rows):
            for j, cell in enumerate(row):
                if i in self.header_row_id_to_attribute:
                    column_base_attributes[j][self.header_row_id_to_attribute[i]] = cell
                if cell in self.keyword_to_attribute:
                    column_base_attributes[j][self.keyword_to_attribute[cell]] = cell
        annotations = []
        for row in nonheader_rows:
            row_base_attributes = {}
            if len(row) >= header_column_count:
                for i in range(0,header_column_count):
                    cell = row[i]
                    if i in self.header_column_id_to_attribute:
                        row_base_attributes[self.header_column_id_to_attribute[i]] = cell
                    if cell in self.keyword_to_attribute:
                        row_base_attributes[self.keyword_to_attribute[cell]] = cell
                for i in range(header_column_count,len(row)):
                    cell = row[i]
                    # if cell and column_base_attributes[i]:
                    if cell and row_base_attributes and column_base_attributes[i]:
                        annotation = {}
                        annotation.update(self.default_attributes)
                        annotation.update(row_base_attributes)
                        annotation.update(column_base_attributes[i])
                        annotations.append((annotation,cell))
        return annotations
