
class SeparatedValuesFileParsing:
    def __init__(self, comment='#', delimeter='\t', padding=' \t\r\n'):
        self.comment = comment
        self.delimeter = delimeter
        self.padding = padding
    def rows(self, filename):
        rows_ = []
        with open(filename) as file:
            for line in file.readlines():
                if self.comment is not None and line.startswith(self.comment):
                    continue
                elif len(line.strip()) < 1:
                    continue
                rows_.append([column.strip(self.padding) for column in line.split(self.delimeter)])
        return rows_
