def load_table( table_name):
    table = {}
    with open( table_name, encoding="utf-8") as table_file:
        for line in table_file:
            arabic_letter, latin_letter = line.split()
            table[ arabic_letter ] = latin_letter
    return table

def transliterate( line, table):
    char_list = list( line)
    for i, char in enumerate( char_list):
        if char in table:
            char_list[ i ] = table[ char ]
    return "".join( char_list)


input_name = "transliteration_input.txt"
output_name = "transliteration_output.txt"
table_name = "transliteration_table.txt"
table = load_table( table_name)
with open( input_name, encoding="utf-8") as input_file, \
        open( output_name, 'w', encoding="utf-8") as output_file:
    for line in input_file:
        line = line.rstrip( '\n')
        line = transliterate( line, table)
        print( line, file=output_file)