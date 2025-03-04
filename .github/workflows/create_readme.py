import re
import collections
import csv
print('-Creating README')


def pad_column(title: str, longest: int, factor=1.575):
    padding = ' ' * int(((longest-len(str(title)))) / 2 * factor)
    return padding + title.replace(' ',' ') + padding

def write_printed(part_data) -> str:
    stl = '[STL](./Printed%20Parts/STL/'+str(part_data['cad_name'])+'.stl)'
    step = '[STEP](./Printed%20Parts/STEP/'+str(part_data['cad_name'])+'.step)'
    time = str(part_data['note'].split('[t:')[1].split('|')[0])
    weight = str(part_data['note'].split('|w:')[1].split('|')[0])

    return '| '+str(part_data['cad_name']) + ' | '+stl+' | '+step+' | '+str(part_data['amount'])+' | '+time+' | '+weight+' |\n'

def short_urls(text:str):
    urls = re.findall(r'(https?://[^\s]+)', text)
    for url in list(set(urls)):
        text = text.replace(url, '[link]('+url+')')
    return text

def write_mechanical(part_data) -> str:
    note = short_urls(str(part_data['note']))

    part_name = '['+str(part_data['cad_name'])+'](./Mechanical%20Parts/'+str(part_data['cad_name'])+'.stl)'
    link = ('[link]('+str(part_data['link'])+')') if str(part_data['link']) not in ['','---'] else ''

    #add alt link to link
    if part_data['alt_link'] not in ['','---']:
        link += ' / [link]('+str(part_data['alt_link'])+')'

    return '| '+part_name+' | '+str(part_data['amount'])+' | '+link+' | '+str(part_data['pcs'])+' | '+str(part_data['price'])+' | '+str(note)+' |\n'

def isfloat(num):
    try: float(num)
    except ValueError: return False
    return True

def ceildiv(a, b):
    return -(a // -b)

def calc_prices(total_prices, part):
    if part['type'] == 'printed': return

    price = str(part['price']).replace(',','.').replace('€','')
    if not isfloat(price): return
    price = float(price)

    category = str(part['category']).upper()

    if category == '': category = 'OTHER'

    #register category
    if category not in total_prices:
        total_prices[category] = {
            "extra": 0,
            "real_price": 0,
            "exact_price": 0
        }

    if part['type'] == 'category_info':
        total_prices[category]['extra'] = price
        return

    if not isfloat(part['pcs']): return

    real_price = price * ceildiv(int(part['amount']), int(part['pcs']))
    exact_price = int(part['amount']) * price / int(part['pcs'])

    total_prices[category]['real_price'] = round(total_prices[category]['real_price'] + real_price, 2)
    total_prices[category]['exact_price'] = round(total_prices[category]['exact_price'] + exact_price, 2)

# read csv
csv_data = {}
try:
    with open('./Parts/bom.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            name = row['cad_name']

            if row['cad_name'] == '' and row['type'] == 'category_info':
                name = row['category'] + row['type']

            csv_data[name] = row
except:
    print('No bom.csv found!')

categories = {}

#gather max lengths for each column
column_lengths = {'printed': {}, 'mechanical': {}}
for part in csv_data:
    part_data = csv_data[part]

    #skip empty row
    if part_data['type'] in ['','category_info'] : continue

    for column in part_data.keys():

        #register all columns
        if column not in column_lengths[part_data['type']]:
            column_lengths[part_data['type']][column] = 0

        #skip '---'
        #if part_data[column] == '---': continue

        column_length = len(str(part_data[column]))

        #detect url in note
        #if column == 'note':
        urls = re.findall(r'(https?://[^\s]+)', str(part_data[column])) #get all urls in note as list
        for url in urls: column_length = column_length - len(str(url)) + 4  #length of real url gets replaced with displayed 'link' message length
        
        #add alt_link length to link
        if column == 'link' and part_data['alt_link'] != '---':
            column_length += 7

        if column_lengths[part_data['type']][column] < column_length:
            column_lengths[part_data['type']][column] = column_length

    #add category if not exists {'category_name':'printed/mechanical'}
    if part_data['category'] not in categories and part_data['category'] != '':
        categories[part_data['category']] = part_data['type']

categories = collections.OrderedDict(
    sorted(categories.items()))  # sort cats


#create table strings
printed_table = ''
mechanical_table = ''

#create table header strings
printed_header = '|'+pad_column('Part Name', column_lengths['printed']['cad_name'], 2.4)+'| STL | STEP |'+pad_column('Amount', column_lengths['printed']['amount'])+'| Print Time | Used filament (g)|\n| --- | --- | --- | --- | --- | --- |\n'
mechanical_header = '|'+pad_column('Part Name', column_lengths['mechanical']['cad_name'], 2.4)+'|'+pad_column('CAD', column_lengths['mechanical']['amount'])+'| '+pad_column('Link', column_lengths['mechanical']['link'])+'|'+pad_column('PCS', column_lengths['mechanical']['pcs'])+' |'+pad_column('Price', column_lengths['mechanical']['price'], 2.5)+'|'+pad_column('Note', column_lengths['mechanical']['note'])+'|\n| --- | --- | :---: | :---: | :---: | :--- |\n'

#create category title + table header
for category in categories:

    if categories[category] == 'printed':

        category_info_note = ''
        for part in csv_data:
            if csv_data[part]['type'] == 'category_info' and csv_data[part]['category'] == category:
                category_info_note = short_urls(str(csv_data[part]['note'])).replace(';',',')
                if category_info_note != '': category_info_note +='\n'
                break

        printed_table += '\n### '+str(category).upper()+':\n' + category_info_note + printed_header

    if categories[category] == 'mechanical':

        category_info_note = ''
        for part in csv_data:
            if csv_data[part]['type'] == 'category_info' and csv_data[part]['category'] == category:
                category_info_note = short_urls(str(csv_data[part]['note'])).replace(';',',')
                if category_info_note != '': category_info_note +='\n'
                break

        mechanical_table += '\n### ' + \
            str(category).upper()+':\n' + category_info_note + mechanical_header


    #create table strings for parts with category
    for part in csv_data:
        part_data = csv_data[part]

        #skip if no category
        if part_data['category'] != category: continue

        if part_data['type'] == 'printed':
            printed_table += write_printed(part_data)

        elif part_data['type'] == 'mechanical':
            mechanical_table += write_mechanical(part_data)

# set header for parts without category
if 'printed' in categories.values():
    printed_table += '\n' + printed_header
else:
    printed_table = '\n' + printed_header
if 'mechanical' in categories.values():
    mechanical_table += '\n' + mechanical_header
else:
    mechanical_table = '\n' + mechanical_header

total_prices = {}

#create table strings for parts without category
for part in csv_data:
    part_data = csv_data[part]

    calc_prices(total_prices, part_data)

    #skip if has category
    if part_data['category'] != '': continue

    if part_data['type'] == 'printed':
        printed_table += write_printed(part_data)

    elif part_data['type'] == 'mechanical':
        mechanical_table += write_mechanical(part_data)

#create total prices table
total_prices_table = '| Category | Total | Exact Price |\n| --- | --- | --- |\n'

total_real_price, total_exact_price = 0, 0
for category in total_prices:
    real_price = str(total_prices[category]['real_price']).replace('.',',')+'€'
    exact_price = str(total_prices[category]['exact_price']).replace('.',',')+'€'

    if total_prices[category]['extra'] != 0:
        extra = str(total_prices[category]['extra']).replace('.',',')+'€'
        real_price += '<br>+' + extra
        exact_price += '<br>+' + extra

        #add extra to each for total
        total_prices[category]['real_price'] = round(total_prices[category]['real_price'] + total_prices[category]['extra'], 2)
        total_prices[category]['exact_price'] = round(total_prices[category]['exact_price'] + total_prices[category]['extra'], 2)
    
    total_real_price = round(total_real_price + total_prices[category]['real_price'], 2)
    total_exact_price = round(total_exact_price + total_prices[category]['exact_price'], 2)

    total_prices_table += '| '+str(category)+' | '+real_price+' | '+exact_price+' |\n'

total_prices_table += '| | | |\n| Total | '+str(total_real_price).replace('.',',')+'€ | '+str(total_exact_price).replace('.',',')+'€ |'

# README update
lines = None
with open('./Parts/README.md', "r", encoding='utf-8') as f:
    lines = f.readlines()

lines_iter = iter(lines)
with open('./Parts/README.md', "w", encoding='utf-8') as f:

    line = next(lines_iter)

    # Fing begining of printed table
    while '## [Printed Parts]' not in line:
        f.write(line)
        line = next(lines_iter)
    f.write(line)

    # write printed table
    for x in printed_table:
        f.write(x)

    # find end of table
    while line[:2] != '``':
        line = next(lines_iter)
    f.write('\n')

    # Fing begining of mechanical table
    while '##' not in line and 'Mechanical Parts' not in line:
        f.write(line)
        line = next(lines_iter)
    f.write(line)

    # write mechanical table
    for x in mechanical_table:
        f.write(x)

    # find end of table
    while line[:2] != '``':
        line = next(lines_iter)
    f.write('\n')

    # Fing begining of total table
    while '##' not in line and 'Total' not in line:
        f.write(line)
        line = next(lines_iter)
    f.write(line)
    
    # write total table
    for x in total_prices_table:
        f.write(x)
    
    # find end of table
    while line[:2] != '> ':
        line = next(lines_iter)
    f.write('\n\n')

    while line:
        f.write(line)
        line = next(lines_iter, False)