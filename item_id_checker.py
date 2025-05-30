# Script to check if an ID number is in use for Trails of Cold Steel 3, 4, Reverie and Tokyo Xanadu eX+.
#
# Usage: Place in the root directory of the game (same folder that bin and data folders are in)
#        and run.
#
# Note:  For TXe, all the t_item.tbl files must be extracted first.  Use txe_file_extract.py from
#        https://github.com/eArmada8/ed8_inject/releases and run the following command:
#            python txe_file_extract.py -a System.bra t_item
#        prior to using this script.
#
# GitHub eArmada8/ed8_dlc_tables

import struct, os, glob, sys

def read_null_terminated_string(f):
    null_term_string = f.read(1)
    while null_term_string[-1] != 0:
        null_term_string += f.read(1)
    return(null_term_string[:-1].decode('utf-8'))

def read_id_numbers(table):
    item_numbers = []
    with open(table, 'rb') as f:
        total_entries, num_sections = struct.unpack("<hi",f.read(6))
        section_data = []
        for i in range(num_sections):
            section = {'name': read_null_terminated_string(f),\
                'num_items': struct.unpack("<i", f.read(4))[0]}
            section_data.append(section)
        for i in range(len(section_data)):
            for j in range(section_data[i]['num_items']):
                entry_type = read_null_terminated_string(f)
                block_size, = struct.unpack("<h", f.read(2))
                item_num, = struct.unpack("<h", f.read(2))
                item_numbers.append(item_num)
                f.seek(block_size-2,1)
    return(item_numbers)

def get_all_id_numbers():
    if os.path.exists('data/text/'):
        folder_prefix = 'data/'
    elif os.path.exists('text/'): #Tokyo Xanadu eX+ mode
        folder_prefix = ''
    else:
        input("No master item table found, is this script in the root game folder?")
        return False
    if os.path.exists(folder_prefix+'text/dat_us/t_item.tbl'):
        item_tables = [folder_prefix+'text/dat_us/t_item.tbl']
    else:
        item_tables = glob.glob(folder_prefix+'text/**/t_item_en.tbl', recursive = True)
    if len(item_tables) < 1:
        item_tables = glob.glob(folder_prefix+'text/**/t_item.tbl', recursive = True)
        if len(item_tables) < 1:
            input("No master item table found, is this script in the root game folder?")
        else:
            item_tables = [item_tables[0]]
    else:
        item_tables = [item_tables[0]]
    #In reading DLC tables, default to English, otherwise the first option available (usually dat)
    if os.path.exists (folder_prefix+'text_dlc'): #CS2 mode
        dlc_folder_prefix = folder_prefix+'text_dlc/'
        dat_name = 'dat_us'
    else:
        dlc_folder_prefix = folder_prefix+'dlc/'
        dats = [x.replace('\\','/').split('/')[-1] for x in glob.glob(glob.glob(folder_prefix+'dlc/text/*')[0]+'/*')]
        if 'dat_en' in dats:
            dat_name = 'dat_en'
        else:
            dat_name = dats[0]
    item_tables.extend(sorted(glob.glob(dlc_folder_prefix+'**/{0}/t_item.tbl'.format(dat_name), recursive = True)))
    item_tables = [x.replace('\\','/') for x in item_tables]
    if os.path.exists('dev/'):
        item_tables_dev = [x.replace('\\','/') for x in sorted(glob.glob('dev/'+dlc_folder_prefix+'text/**/{0}/t_item.tbl'.format(dat_name), recursive = True))]
        item_tables = ['dev/'+x if os.path.exists('dev/'+x) else x for x in item_tables]
        item_tables.extend([x for x in item_tables_dev if x not in item_tables])
    all_item_numbers = {}
    all_dlc_item_numbers = {}
    for i in range(len(item_tables)):
        print("Checking {0}...".format(item_tables[i]))
        all_item_numbers.update({x:item_tables[i] for x in read_id_numbers(item_tables[i])})
        if i > 0:
            all_dlc_item_numbers.update({x:item_tables[i] for x in read_id_numbers(item_tables[i])})
    dlc_available = [x for x in range(min(all_dlc_item_numbers.keys()), max(all_item_numbers.keys())) if x not in all_item_numbers.keys()]
    if len(dlc_available) > 10:
        print("The next 10 available id numbers are {0}".format(dlc_available[0:10]))
    else:
        print("The next {0} available id numbers are {1}".format(len(dlc_available), dlc_available))
    return(all_item_numbers)

def check_id_number(all_item_numbers, number = -1):
    while number == -1:
        print("The current range of ID numbers is {0} to {1}.".format(min(all_item_numbers.keys()), max(all_item_numbers.keys())))
        number_input = input("What number would you like to check? ")
        try:
            number = int(number_input)
        except ValueError:
            print("Invalid Entry!")
    return(number in all_item_numbers.keys())

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    all_item_numbers = get_all_id_numbers()
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('id_num', help="ID Number to check.")
        args = parser.parse_args()
        if check_id_number(all_item_numbers, int(args.id_num)):
            print("Item ID {0} is in {1}!".format(int(args.id_num), all_item_numbers[number]))
        else:
            print("Item ID {0} does not exist!".format(int(args.id_num)))
    else:
        number = -1
        while number == -1:
            print("The current range of ID numbers is {0} to {1}.".format(min(all_item_numbers), max(all_item_numbers)))
            number_input = input("What number would you like to check? (Press enter to quit) ")   
            if number_input == '':
                break
            else:
                try:
                    number = int(number_input)
                    if check_id_number(all_item_numbers, number):
                        print("Item ID {0} is in {1}!".format(number, all_item_numbers[number]))
                    else:
                        print("Item ID {0} does not exist!".format(number))
                    number = -1
                except ValueError:
                    print("Invalid Entry!")