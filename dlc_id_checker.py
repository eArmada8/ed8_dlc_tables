# Script to check if an ID number is in use for Trails of Cold Steel 3, 4, Reverie and Tokyo Xanadu eX+.
#
# Usage: Place in the root directory of the game (same folder that bin and data folders are in)
#        and run.
#
# Note:  For TXe, all the t_item.tbl files must be extracted first.  Use txe_file_extract.py from
#        https://github.com/eArmada8/ed8_inject/releases and run the following command:
#            python txe_file_extract.py -a System.bra t_dlc
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
    dlc_tables = glob.glob('data/dlc/**/t_dlc.tbl', recursive = True) \
        + glob.glob('data/text_dlc/**/t_dlc.tbl', recursive = True) \
        + glob.glob('text/**/t_dlc.tbl', recursive = True) \
        + glob.glob('dlc/**/t_dlc.tbl', recursive = True)
    dlc_tables = [x.replace('\\','/') for x in dlc_tables]
    if os.path.exists('dev/'):
        dlc_tables_dev = [x.replace('\\','/') for x in glob.glob('dev/**/t_dlc.tbl', recursive = True)]
        dlc_tables = ['dev/'+x if os.path.exists('dev/'+x) else x for x in dlc_tables]
        dlc_tables.extend([x for x in dlc_tables_dev if not x in dlc_tables])
    all_dlc_numbers = []
    for i in range(len(dlc_tables)):
        print("Checking {0}...".format(dlc_tables[i]))
        all_dlc_numbers.extend(read_id_numbers(dlc_tables[i]))
    return(sorted(list(set(all_dlc_numbers))))

def check_id_number(all_dlc_numbers, number = -1):
    while number == -1:
        print("The current range of ID numbers is {0} to {1}.".format(min(all_dlc_numbers), max(all_dlc_numbers)))
        number_input = input("What number would you like to check? ")
        try:
            number = int(number_input)
        except ValueError:
            print("Invalid Entry!")
    return(number in all_dlc_numbers)

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    all_dlc_numbers = get_all_id_numbers()
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('id_num', help="ID Number to check.")
        args = parser.parse_args()
        if check_id_number(all_dlc_numbers, int(args.id_num)):
            print("Item ID {0} already exists!".format(int(args.id_num)))
        else:
            print("Item ID {0} does not exist!".format(int(args.id_num)))
    else:
        number = -1
        while number == -1:
            print("The current range of ID numbers is {0} to {1}.".format(min(all_dlc_numbers), max(all_dlc_numbers)))
            number_input = input("What number would you like to check? (Press enter to quit) ")   
            if number_input == '':
                break
            else:
                try:
                    number = int(number_input)
                    if check_id_number(all_dlc_numbers, number):
                        print("Item ID {0} already exists!".format(number))
                    else:
                        print("Item ID {0} does not exist!".format(number))
                    number = -1
                except ValueError:
                    print("Invalid Entry!")