# Short script to generate a set of dlc tables for custom costumes in
# Trails of Cold Steel II / III / IV / into Reverie and Tokyo Xanadu eX+.
# Uses the decoded t_name.tbl from tbled.
#
# GitHub eArmada8/ed8_dlc_tables

import os, csv, json, struct, glob, random

class dlc_table_maker:
    def __init__ (self):
        random.seed()
        self.random_number = round(random.random()*888+2000)
        self.dlc_details = self.get_dlc_details()
        self.name_dict = self.get_names({2:'ed82xseed.csv', 3:'ed83nisa.csv',\
            4:'ed84nisa.csv', 5:'ed85nisa.csv', 18:'txe_names.csv'}[self.dlc_details['game_type']])
        self.packages = self.get_pkg_details()
        self.package_list = list(self.packages.keys())
        self.transform_counter = 0

    def get_dlc_details (self):
        if os.path.exists('dlc.json'):
            with open('dlc.json', 'r') as f:
                dlc_details = json.loads(f.read())
        else:
            dlc_details = {}
        while 'game_type' not in dlc_details.keys() or dlc_details['game_type'] not in [2,3,4,5,18]:
            item_type_raw = input("Which game? [2=CS2, 3=CS3, 4=CS4, 5=NISA Reverie, 18=TXe, leave blank for 4] ")
            if item_type_raw == '':
                dlc_details['game_type'] = 4
            else:
                try:
                    dlc_details['game_type'] = int(item_type_raw)
                    if dlc_details['game_type'] not in [2,3,4,5,18]:
                        print("Invalid entry!")
                except ValueError:
                    print("Invalid entry!")
        while 'dlc_id' not in dlc_details.keys():
            dlc_id_raw = input("DLC ID number: ")
            try:
                dlc_details['dlc_id'] = int(dlc_id_raw)
            except ValueError:
                print("Invalid entry!")
        while 'dlc_sort_id' not in dlc_details.keys():
            dlc_details['dlc_sort_id'] = self.random_number
        while 'dlc_name' not in dlc_details.keys() or dlc_details['dlc_name'] == '':
            dlc_details['dlc_name'] = str(input("DLC Name: ")).encode('utf-8').decode('utf-8')
        while 'dlc_desc' not in dlc_details.keys() or dlc_details['dlc_desc'] == '':
            dlc_details['dlc_desc'] = str(input("DLC Description: ")).encode('utf-8').decode('utf-8')
        with open('dlc.json', "wb") as f:
            f.write(json.dumps(dlc_details, indent=4).encode("utf-8"))
        return(dlc_details)

    #Takes NameTableData.csv from tbled
    def get_names (self, tablename = 'ed84nisa.csv'):
        import csv
        name_dict = {}
        with open(tablename, encoding='utf-8') as csvfile:
            names = csv.reader(csvfile, delimiter=',')
            for row in names:
                #if not row[0] == 'character' and not row[0] == '65535':
                if not row[0] == 'character' and int(row[0]) < 200 and len(row[2].split("_")) == 2:
                    if row[2] not in name_dict.keys():
                        name_dict[row[2]] = {'chr_id': int(row[0]), 'chr_name': row[1]}
        return(name_dict)

    def get_items_from_jsons (self):
        items = {}
        jsons = glob.glob('*.pkg.json')
        for i in range(len(jsons)):
            with open(jsons[i], 'r') as f:
                pkg_details = json.loads(f.read())
            if 'item_id' in pkg_details.keys():
                items[pkg_details['item_id']] = pkg_details
        return(items)

    def get_chr_id (self, pkg_name):
        try:
            base_name = "_".join(pkg_name.split('.')[0].split("_")[0:2])
            if base_name[:2] == 'FC':
                base_name = base_name[1:]
            return(self.name_dict[base_name]['chr_id'])
        except KeyError:
            return 0x1FFFFFFF # This number is meaningless, just used to catch errors

    def get_chr_name (self, chr_id):
        try:
            return([x['chr_name'] for x in self.name_dict.values() if x['chr_id'] == chr_id][0])
        except KeyError:
            return ''

    def get_pkg_details (self):
        packages = sorted(list(set([x.split('.json')[0] for x in glob.glob('*.pkg*')])))
        unique_chars = list(set([self.get_chr_id(x) for x in packages if self.get_chr_id(x) != 0x1FFFFFFF]))
        existing_items = self.get_items_from_jsons()
        pkg_dict = {}
        for i in range(len(packages)):
            print("\nProcessing {0}...\n".format(packages[i]))
            if os.path.exists(packages[i] + '.json'):
                with open(packages[i] + '.json', 'r') as f:
                    pkg_details = json.loads(f.read())
            else:
                pkg_details = {}
            while 'item_id' not in pkg_details.keys():
                print("Note: If you want two attachments to be grouped, give them the same item ID.")
                item_id_raw = input("Item ID number for {0}: ".format(packages[i]))
                try:
                    pkg_details['item_id'] = int(item_id_raw)
                    if pkg_details['item_id'] in list(existing_items.keys()):
                        pkg_details['item_type'] = existing_items[pkg_details['item_id']]['item_type']
                        pkg_details['item_quantity'] = existing_items[pkg_details['item_id']]['item_quantity']
                        #pkg_details['chr_id'] = existing_items[pkg_details['item_id']]['chr_id']
                        pkg_details['item_name'] = existing_items[pkg_details['item_id']]['item_name']
                        pkg_details['item_desc'] = existing_items[pkg_details['item_id']]['item_desc']
                except ValueError:
                    print("Invalid entry!")
            while 'item_type' not in pkg_details.keys() or pkg_details['item_type'] not in [193,194,195,454]:
                print("Item type: [193=costume, 194=attachment, 195=hair color, 454=ARCUS cover, leave blank for 193]")
                item_type_raw = input("Item type for {0}: ".format(packages[i]))
                if item_type_raw == '':
                    print("No entry given, setting item type to default of 193.")
                    pkg_details['item_type'] = 193
                else:
                    try:
                        pkg_details['item_type'] = int(item_type_raw)
                        if pkg_details['item_type'] not in [193,194,195,454]:
                            print("Invalid entry!")
                        if pkg_details['item_type'] == 454:
                            if len(packages[i].split('I_3D_ARC_C')) > 1:
                                try:
                                    pkg_details['target_type'] = int(packages[i].split('I_3D_ARC_C')[1].split('.')[0])
                                    if not pkg_details['target_type'] in range(256):
                                        print("Item type 454 was specified, but xxx in I_3D_ARC_Cxxx.pkg must be between 000 and 255!")
                                        pkg_details['item_type'] = 0
                                        pkg_details['target_type'] = 0
                                except ValueError:
                                    print("Item type 454 was specified, but the pkg name must be I_3D_ARC_Cxxx.pkg!")
                                    pkg_details['item_type'] = 0
                            else:
                                print("Item type 454 was specified, but the pkg name must be I_3D_ARC_Cxxx.pkg!")
                                pkg_details['item_type'] = 0
                    except ValueError:
                        print("Invalid entry!")
            while 'target_type' not in pkg_details.keys() or pkg_details['target_type'] == '':
                pkg_details['target_type'] = 0
            while 'attach_point' not in pkg_details.keys() or pkg_details['attach_point'] == '':
                if pkg_details['item_type'] == 194:
                    pkg_details['attach_point'] = str(input("Attach point for {0}: (e.g. head_point - check .inf file for valid options)  ".format(packages[i]))).encode('utf-8').decode('utf-8')
                else:
                    pkg_details['attach_point'] = 'null'
            while 'chr_id' not in pkg_details.keys() or pkg_details['chr_id'] == 0x1FFFFFFF:
                pkg_details['chr_id'] = self.get_chr_id(packages[i])
                if pkg_details['chr_id'] == 0x1FFFFFFF: #Non-costume
                    print("Item Select Character Restriction: Please choose a character for {0}: ".format(packages[i]))
                    print("-1. Any character")
                    for j in range(len(unique_chars)):
                        print("{0}. {1}".format(unique_chars[j], self.get_chr_name(unique_chars[j])))
                    print("(Any number <65536 is accepted, see {0} for other options)".format({3:'ed83nisa.csv', 4:'ed84nisa.csv', 5:'ed85nisa.csv', 18:'txe_names.csv'}[self.dlc_details['game_type']]))
                    chr_id_raw = input("Character restriction for {0}: ".format(packages[i]))
                    try:
                        if int(chr_id_raw) == -1:
                            pkg_details['chr_id'] = 0xFFFF
                        else:
                            if int(chr_id_raw) < 0x10000:
                                pkg_details['chr_id'] = int(chr_id_raw)
                            else:
                                print("Invalid entry!")
                    except ValueError:
                        print("Invalid entry!")
            if pkg_details['chr_id'] < 1000 and 'chr_id_a' not in pkg_details:
                pkg_details['chr_id_a'] = pkg_details['chr_id']
            while 'chr_id_a' not in pkg_details.keys() or pkg_details['chr_id_a'] == 0x1FFFFFFF:
                pkg_details['chr_id_a'] = self.get_chr_id(packages[i])
                if pkg_details['chr_id_a'] == 0x1FFFFFFF: #Non-costume
                    print("Attachment Character Restriction: Please choose a character for {0}: ".format(packages[i]))
                    print("-1. Any character")
                    for j in range(len(unique_chars)):
                        print("{0}. {1}".format(unique_chars[j], self.get_chr_name(unique_chars[j])))
                    print("(Any number <65536 is accepted, see {0} for other options)".format({3:'ed83nisa.csv', 4:'ed84nisa.csv', 5:'ed85nisa.csv', 18:'txe_names.csv'}[self.dlc_details['game_type']]))
                    chr_id_raw = input("Character restriction for {0}: ".format(packages[i]))
                    try:
                        if int(chr_id_raw) == -1:
                            pkg_details['chr_id_a'] = 0xFFFF
                        else:
                            if int(chr_id_raw) < 0x10000:
                                pkg_details['chr_id_a'] = int(chr_id_raw)
                            else:
                                print("Invalid entry!")
                    except ValueError:
                        print("Invalid entry!")
            while 'item_sort_id' not in pkg_details.keys():
                pkg_details['item_sort_id'] = self.random_number + {2:0, 3:0, 4:3000, 5:10000, 18: 2000}[self.dlc_details['game_type']]
                self.random_number += 1
            while 'item_name' not in pkg_details.keys() or pkg_details['item_name'] == '':
                pkg_details['item_name'] = str(input("Item Name for {0}: ".format(packages[i]))).encode('utf-8').decode('utf-8')
            while 'item_desc' not in pkg_details.keys() or pkg_details['item_desc'] == '':
                pkg_details['item_desc'] = str(input("Item Description for {0}: ".format(packages[i]))).encode('utf-8').decode('utf-8')
            while 'item_cs4rev_scraft_cutin' not in pkg_details.keys() or pkg_details['item_cs4rev_scraft_cutin'] == '':
                pkg_details['item_cs4rev_scraft_cutin'] = 0
            while 'rev_voice_flag' not in pkg_details.keys() or pkg_details['rev_voice_flag'] == '':
                pkg_details['rev_voice_flag'] = 0
            while 'item_quantity' not in pkg_details.keys():
                item_quant_raw = input("How many should be included in the DLC? [Leave blank for 1] ".format(packages[i]))
                if item_quant_raw == '':
                    pkg_details['item_quantity'] = 1
                else:
                    try:
                        pkg_details['item_quantity'] = min(max(int(item_quant_raw),1),99)
                    except ValueError:
                        print("Invalid entry!")
            while 'flags' not in pkg_details.keys():
                if pkg_details['item_type'] == 454:
                    pkg_details['flags'] = 'S1'
                elif pkg_details['chr_id'] != 0xFFFF and pkg_details['item_quantity'] < 99:
                    pkg_details['flags'] = 'S{}'.format(pkg_details['item_quantity'])
                else:
                    pkg_details['flags'] = '0'
            if not pkg_details['attach_point'] == 'null': #and 'attach_transform_data' not in pkg_details:
                if os.path.exists(packages[i][:-4] + '.transform.csv'):
                    with open(packages[i][:-4] + '.transform.csv', encoding='utf-8') as csvfile:
                        transform_data = [row for row in csv.reader(csvfile, delimiter=',')]
                        pkg_details['attach_transform_data'] = [dict(zip(transform_data[0],x)) for x in transform_data[1:]]
            pkg_dict[packages[i]] = pkg_details
            if pkg_details['item_id'] not in list(existing_items.keys()):
                existing_items[pkg_details['item_id']] = pkg_details
            with open(packages[i] + '.json', "wb") as f:
                f.write(json.dumps(pkg_details, indent=4).encode("utf-8"))
        return(pkg_dict)

    def make_tbl_header (self, item_count, name, second_name = ''):
        if len(second_name) > 0:
            #CS3/TXe requires both item and item_q in every item table for some reason, even if there is no item_q
            return(struct.pack("<HI", item_count, 2) + name.encode() + b'\x00' + struct.pack("<I", item_count)\
                 + second_name.encode() + b'\x00' + struct.pack("<I", 0)) #Second quantity set to 0
        else:
            return(struct.pack("<HI", item_count, 1) + name.encode() + b'\x00' + struct.pack("<I", item_count))

    def make_item_entry (self, pkg_name):
        item_tbl_entry = struct.pack("<2H", self.packages[pkg_name]['item_id'], self.packages[pkg_name]['chr_id'])
        item_tbl_entry += self.packages[pkg_name]['flags'].encode() + b'\x00'
        if self.dlc_details['game_type'] == 5: #NISA Reverie
            item_tbl_entry += struct.pack("<2H", 0, self.packages[pkg_name]['item_type'])
            item_tbl_entry += struct.pack("<B4H", *[0]*5)
            item_tbl_entry += struct.pack("<B", self.packages[pkg_name]['target_type'])
            item_tbl_entry += struct.pack("<B59H", *[0]*60)
            # The first two numbers are constant and same as CS4, the second two seem random, maybe sorting or a timestamp?
            item_tbl_entry += struct.pack("<4H", 99, 0, self.packages[pkg_name]['item_sort_id'], 32)
        elif self.dlc_details['game_type'] == 3: #CS3
            item_tbl_entry += struct.pack("<H", self.packages[pkg_name]['item_type'])
            item_tbl_entry += struct.pack("<4H", *[0]*4)
            item_tbl_entry += struct.pack("<B", self.packages[pkg_name]['target_type'])
            item_tbl_entry += struct.pack("<B55H", *[0]*56)
            item_tbl_entry += struct.pack("<BHH", 99, self.packages[pkg_name]['item_sort_id'], 0) # Second number is sort, third number may also be sort?
        elif self.dlc_details['game_type'] == 2: #CS2
            item_tbl_entry += struct.pack("<B", self.packages[pkg_name]['item_type'])
            item_tbl_entry += struct.pack("<B", 0)
            item_tbl_entry += struct.pack("<B", self.packages[pkg_name]['target_type'])
            item_tbl_entry += struct.pack("<26H", *[0]*26)
            item_tbl_entry += struct.pack("<B2H", 99, self.packages[pkg_name]['item_sort_id'], self.dlc_details['dlc_id'])
        elif self.dlc_details['game_type'] == 18: #TXe
            item_tbl_entry += struct.pack("<H", self.packages[pkg_name]['item_type'])
            item_tbl_entry += struct.pack("<27H", *[0]*27)
            item_tbl_entry += struct.pack("<3H", 99, self.packages[pkg_name]['item_sort_id'], self.dlc_details['dlc_id'])
        else: #Defaults to Cold Steel IV
            item_tbl_entry += struct.pack("<2H", 0, self.packages[pkg_name]['item_type'])
            item_tbl_entry += struct.pack("<4H", *[0]*4)
            item_tbl_entry += struct.pack("<B", self.packages[pkg_name]['target_type'])
            item_tbl_entry += struct.pack("<B65H", *[0]*66)
            item_tbl_entry += struct.pack("<3H", 99, self.packages[pkg_name]['item_sort_id'], self.dlc_details['dlc_id'])
        item_tbl_entry += self.packages[pkg_name]['item_name'].encode('utf-8') + b'\x00'
        item_tbl_entry += self.packages[pkg_name]['item_desc'].encode('utf-8') + b'\x00'
        if self.dlc_details['game_type'] == 5: #NISA Reverie
            pass
        elif self.dlc_details['game_type'] == 18: #TXe
            item_tbl_entry += struct.pack("<2IB", *[0]*3)
        else: #Defaults to Cold Steel II/III/IV
            item_tbl_entry += struct.pack("<2I", 0, 0)
        return(b'item\x00' + struct.pack("<H",len(item_tbl_entry)) + item_tbl_entry)

    def make_attach_entry (self, pkg_name):
        attach_tbl_entry = struct.pack("<3HI", self.packages[pkg_name]['chr_id_a'],\
            {193:5, 194:67, 195: 9, 454: 5}[self.packages[pkg_name]['item_type']], 0, self.packages[pkg_name]['item_id'])
        if self.dlc_details['game_type'] in [2,3]: #CS2/CS3
            attach_tbl_entry += struct.pack("<6H", *[0]*6)
        elif self.dlc_details['game_type'] == 18: #TXe
            attach_tbl_entry += struct.pack("<4I", 0,0,0,255)
        else: #Defaults to Cold Steel IV / Reverie
            voice_flag = self.packages[pkg_name]['rev_voice_flag'] if self.dlc_details['game_type'] == 5 else 0
            attach_tbl_entry += struct.pack("<4iH", 0, 0, voice_flag, self.packages[pkg_name]['item_cs4rev_scraft_cutin'], 48)
        attach_tbl_entry += pkg_name.split('.')[0].encode() + b'\x00' #Split is to remove the .pkg
        attach_tbl_entry += self.packages[pkg_name]['attach_point'].encode() + b'\x00'
        return(b'AttachTableData\x00' + struct.pack("<H",len(attach_tbl_entry)) + attach_tbl_entry)

    def make_attach_transform_entries (self, pkg_name):
        transform_entries = b''
        for entry in self.packages[pkg_name]['attach_transform_data']:
            attach_transform_entry = struct.pack("<H", int(entry['char_id']))
            if self.dlc_details['game_type'] == 5: #Reverie
                attach_transform_entry += entry['costume_id'].encode('utf-8') + b'\x00'
            attach_transform_entry += pkg_name.split('.pkg')[0].encode('utf-8') + b'\x00'
            attach_transform_entry += entry['translate'].encode('utf-8') + b'\x00'
            attach_transform_entry += entry['rotate'].encode('utf-8') + b'\x00'
            attach_transform_entry += entry['scale'].encode('utf-8') + b'\x00'
            transform_entries += b'AttachTransformData\x00' + struct.pack("<H",len(attach_transform_entry)) + attach_transform_entry
            self.transform_counter += 1
        return(transform_entries)

    def make_dlc_entry (self):
        if self.dlc_details['game_type'] in [2, 18]: #CS2/TXe
            dlc_tbl_entry = struct.pack("<H", self.dlc_details['dlc_id'])
        else:
            dlc_tbl_entry = struct.pack("<2H", self.dlc_details['dlc_id'], self.dlc_details['dlc_sort_id'])
        if self.dlc_details['game_type'] == 3: #CS3
            dlc_tbl_entry += struct.pack("<2H", *[0]*2)
        elif self.dlc_details['game_type'] in [2, 18]: #CS2/TXe
            # I have no idea if there is a sort ID here, every entry I examined had the same values
            dlc_tbl_entry += struct.pack("<2HI", 65535, 100, 0)
            if self.dlc_details['game_type'] == 2:
                dlc_tbl_entry += struct.pack("<H", 0)
        else: #Defaults to Cold Steel IV / Reverie
            dlc_tbl_entry += struct.pack("<8H", *[0]*8)
        dlc_tbl_entry += self.dlc_details['dlc_name'].encode('utf-8') + b'\x00'
        dlc_tbl_entry += self.dlc_details['dlc_desc'].encode('utf-8') + b'\x00'
        items_added = []
        for i in range(len(self.package_list)):
            if self.packages[self.package_list[i]]['item_id'] not in items_added:
                dlc_tbl_entry += struct.pack("<2H", self.packages[self.package_list[i]]['item_id'],\
                    self.packages[self.package_list[i]]['item_quantity']) # Second number is quantity
                items_added.append(self.packages[self.package_list[i]]['item_id'])
        if 20 - len(items_added) > 0:
            for i in range(20 - len(items_added)):
                dlc_tbl_entry += struct.pack("<2H", 9999, 0)
        return(b'dlc\x00' + struct.pack("<H",len(dlc_tbl_entry)) + dlc_tbl_entry)

    def make_item_tbl (self, write_table = True):
        items_added = []
        item_tbl = bytes()
        for i in range(len(self.package_list)):
            if self.packages[self.package_list[i]]['item_id'] not in items_added:
                item_tbl += self.make_item_entry(self.package_list[i])
                items_added.append(self.packages[self.package_list[i]]['item_id'])
        if self.dlc_details['game_type'] in [3,18]:
            item_tbl = self.make_tbl_header(len(items_added), 'item', 'item_q') + item_tbl
        else:
            item_tbl = self.make_tbl_header(len(items_added), 'item') + item_tbl
        if write_table == True:
            with open("t_item.tbl","wb") as f:
                f.write(item_tbl)
        return(item_tbl)

    def make_attach_tbl (self, write_table = True):
        self.transform_counter = 0
        table_counter = len(self.package_list)
        attach_tbl_data = b''
        for i in range(len(self.package_list)):
            attach_tbl_data += self.make_attach_entry(self.package_list[i])
            if not self.packages[self.package_list[i]]['attach_point'] == 'null'\
                    and self.dlc_details['game_type'] in [4,5]\
                    and 'attach_transform_data' in self.packages[self.package_list[i]]\
                    and len(self.packages[self.package_list[i]]['attach_transform_data']) > 0:
                attach_tbl_data += self.make_attach_transform_entries(self.package_list[i])
        attach_tbl = struct.pack("<HI", table_counter+self.transform_counter, {2:1,3:1,4:2,5:2,18:1}[self.dlc_details['game_type']])
        attach_tbl += 'AttachTableData'.encode() + b'\x00' + struct.pack("<I", table_counter)
        if self.dlc_details['game_type'] in [4,5]:
            attach_tbl += 'AttachTransformData'.encode() + b'\x00' + struct.pack("<I", self.transform_counter)
        attach_tbl += attach_tbl_data
        if write_table == True:
            with open("t_attach.tbl","wb") as f:
                f.write(attach_tbl)
        return(attach_tbl)

    def make_dlc_tbl (self, write_table = True):
        dlc_tbl = self.make_tbl_header(1, 'dlc')
        dlc_tbl += self.make_dlc_entry() # I think we can put more than one entry
        if write_table == True:
            with open("t_dlc.tbl","wb") as f:
                f.write(dlc_tbl)
        return(dlc_tbl)

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    dlc_table_maker = dlc_table_maker()
    dlc_table_maker.make_item_tbl()
    dlc_table_maker.make_attach_tbl()
    dlc_table_maker.make_dlc_tbl()
