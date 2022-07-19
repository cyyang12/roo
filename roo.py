
import requests
import json
import csv
import os.path
import os

FIND_ROO_ROOT = 'https://findrulesoforigin.org/api'
URL_ROO_LIST_ALL = FIND_ROO_ROOT + "/getftalist"
URL_FTA_META = FIND_ROO_ROOT + "/getftareportingctrystatus"
URL_FTA_INFO = FIND_ROO_ROOT + "/getftaroo"
URL_FTA_DETAIL = FIND_ROO_ROOT + "/getftaroodetail"

def json_req_with_param(url, params):
  r = requests.get(url = url, params = params)
  return r.json()

def roo_only_list():
  data = json_req_with_param(URL_ROO_LIST_ALL, {'showall': True })
  # filter on RooAvailable is true only
  roo_available_fta_list = list(filter(lambda d: d['RooAvailable'] == True, data))
  # roo_available_fta_list = list(map(lambda d: d['FtaName'], data))
  return roo_available_fta_list

def get_one_fta_member(ftaID):
  data = json_req_with_param(URL_FTA_META, {'ftaid': ftaID })
  return data

# given a list of fta object (containing FtaId), then fetch by each FtaId to get its member info and save to a JSON file
# member info format example
# {"COUNTRYID": 458, "ISO2CODE": "MY", "COUNTRYNAME": "Malaysia", "STATUSDATE": "01.01.2008", "STATUSRANK": 3, "STATUSID": 7, "STATUSDESC": "In force"}
def save_all_fta_members_in_json(fta_list):
  i = 0
  for fta in fta_list:
    ftaID = fta['FtaId']
    fta_member = get_one_fta_member(fta['FtaId'])
    print(fta_member)
    with open("data/fta_meta/{0}.json".format(ftaID), 'w') as outfile:
      json.dump(fta_member, outfile)
    i += 1
    # print(i)

def prepare_base_fta_with_member_info_rows(fta_info):
  ftaID = fta_info['FtaId']
  ftaName = fta_info['FtaName']
  ftaYear = fta_info['FtaYear']
  ftaStatus = fta_info['StatusDesc']
  ftaRooAvailable = fta_info['RooAvailable']
  with open("data/fta_meta/{0}.json".format(ftaID), 'r') as json_file:
    fta_members = json.load(json_file)
  rows = []
  for member in fta_members:
    row = {
      'ftaID': ftaID,
      'ftaYear': ftaYear,
      'ftaStatus': ftaStatus, 
      'ftaName': ftaName,
      'ftaRooAvailable': ftaRooAvailable,
      'iso2Code': member['ISO2CODE'],
      'countryName': member['COUNTRYNAME'],
      'statusDate': member['STATUSDATE'],
      'statusRank': member['STATUSRANK'],
      'statusID': member['STATUSID'],
      'statusDesc': member['STATUSDESC'],
      'countryID': member['COUNTRYID']
    }
    rows.append(row)
  return rows

def prepare_fta_list_with_member_info():
  with open("data/fta_list.json", 'r') as json_file:
    fta_list = json.load(json_file)
  all_rows = []

  for fta in fta_list:
    rows = prepare_base_fta_with_member_info_rows(fta)
    all_rows = all_rows + rows
    # break

  with open('countries.csv', 'w', encoding='UTF8', newline='') as f:
    fieldnames = ['ftaID', 'ftaYear', 'ftaName', 'ftaStatus', 'ftaRooAvailable', 'iso2Code', 'countryName', 'statusDate', 'statusRank', 'statusID', 'statusDesc', 'countryID']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_rows)

def get_fta_detail_by_id_and_partners(ftaID, reporter, partner, productCode, rank, isActive):
  try:
    data = json_req_with_param(URL_FTA_DETAIL, {'reporter': reporter, 'partner': partner, 'product': productCode, 'ftaId': ftaID, 'isActive': isActive, 'statusRank': rank })
    print(URL_FTA_DETAIL, reporter, partner, productCode, ftaID, isActive, rank)
    return data, data['FtaRooDetailInfo'] != None
  except:
    return None, False

# if id_str is less than 3 digit, ex, 76
# amend zero to the front to make it 3 digit, ex, 076
def id_fill(id_str):
  str_len = len(str(id_str))
  if str_len < 3:
    return (3 - str_len) * '0' + str(id_str)
  return str(id_str)

country_id_to_code_map = { '1011': '100','1013': '191','1001': '196', '1002': '203','1003': '233', '1004': '348','1005': '428','1006': '440','1007': '470','1008': '616','1012': '642','1009': '703','1010': '705','1014': '826' }

def down_fta_details_finding_lowest_rank_for_every_pairing_countries(ftaID, ftaStatus):
  with open("data/fta_meta/{0}.json".format(ftaID), 'r') as json_file:
    fta_members = json.load(json_file)

  print(fta_members)
  mystic_ftas = []

  status_rank = 0
  # reporter_country = fta_members[len(fta_members) - 1]
  # reporter_country_code = 'all'
  isActive = ftaStatus

  # num_rank = fta_members[0]['STATUSRANK']
  max_rank = fta_members[0]['STATUSRANK']
  for member in fta_members:
    if member['STATUSRANK'] > max_rank:
      max_rank = member['STATUSRANK']
  num_rank = max_rank

  count = len(fta_members) * (len(fta_members) - 1) / 2 * num_rank
  print(count)
  # return count

  # m = len(fta_members) - 1
  # while m >= 0:
  # for i in range(len(fta_members) - 2, -1, -1):
    # m -= 1
  for m in range(0, len(fta_members) - 1):
    for n in range(m + 1, len(fta_members)):
      # print(m, n)
      partner_country = fta_members[n]
      # print(partner_country)
      partner_country_code = id_fill(partner_country['COUNTRYID'])

      # id code mapping

      if partner_country_code in country_id_to_code_map:
        partner_country_code = country_id_to_code_map[partner_country_code]

      # if partner_country_code == '1014':
      #   partner_country_code = '826'

      reporter_country = fta_members[m]
      # print(partner_country)
      reporter_country_code = id_fill(reporter_country['COUNTRYID'])

      # id code mapping
      # if reporter_country_code == '1014':
      #   reporter_country_code = '826'

      if reporter_country_code in country_id_to_code_map:
        reporter_country_code = country_id_to_code_map[reporter_country_code]

      # status_rank = partner_country['STATUSRANK']
      status_rank = max_rank
      productCode = 8703900000

      has_at_least_one_found = False
      while status_rank >= 1:
        print(partner_country_code, reporter_country_code, status_rank, max_rank, m, n, len(fta_members) - 1)

        fta_details, hasRoo = get_fta_detail_by_id_and_partners(ftaID, reporter_country_code ,partner_country_code, productCode, status_rank, isActive)
        
        # when the first time found a valid fta detail page
        # write to disk and skip checkinng for the rest of participating countries
        # print(fta_details)
        if hasRoo == True:
          print('******************* found! *********************')
          has_at_least_one_found = True
        
        fta_details['members_found'] = [reporter_country_code, partner_country_code, status_rank, productCode]
        with open("data/fta_detail_multi_full/{0}_{1}_{2}_{3}_{4}.json".format(ftaID, reporter_country_code, partner_country_code, status_rank, productCode), 'w') as outfile:
          json.dump(fta_details, outfile)
          # break

        status_rank -= 1

      if not has_at_least_one_found:
        mystic_ftas.append("{0}_{1}_{2}".format(ftaID, reporter_country_code, partner_country_code))
  return mystic_ftas

# pairing with reporter country as 'all', then trying with all other partner country
# stop at the first find
def down_one_fta_detail_one_to_all(ftaID, ftaStatus):
  with open("data/fta_meta/{0}.json".format(ftaID), 'r') as json_file:
    fta_members = json.load(json_file)

  print(fta_members)

  status_rank = 0
  reporter_country = fta_members[len(fta_members) - 1]
  reporter_country_code = 'all'
  isActive = ftaStatus

  m = len(fta_members) - 1
  while m >= 0:
  # for i in range(len(fta_members) - 2, -1, -1):
    m -= 1
    # print(m)
    partner_country = fta_members[m]
    # print(partner_country)
    partner_country_code = id_fill(partner_country['COUNTRYID'])

    # id code mapping
    if partner_country_code == '1014':
      partner_country_code = '826'

    status_rank = partner_country['STATUSRANK']
    fta_details, hasRoo = get_fta_detail_by_id_and_partners(ftaID, partner_country_code, reporter_country_code , 870321, status_rank, isActive)
    
    # when the first time found a valid fta detail page
    # write to disk and skip checkinng for the rest of participating countries
    # print(fta_details)
    if hasRoo == True:
      print('******************* found! *********************')
      fta_details['members_found'] = [reporter_country_code, partner_country_code]
      with open("data/fta_detail/{0}.json".format(ftaID), 'w') as outfile:
        json.dump(fta_details, outfile)
      break

# read participating countries from meta file
# then the paring with the last country to every other country for once
def down_one_fta_detail(ftaID, ftaStatus):
  with open("data/fta_meta/{0}.json".format(ftaID), 'r') as json_file:
    fta_members = json.load(json_file)

  # print(fta_members)

  status_rank = 0
  reporter_country = fta_members[len(fta_members) - 1]
  reporter_country_code = id_fill(reporter_country['COUNTRYID'])
  isActive = ftaStatus

  m = len(fta_members) - 1
  while m > 0:
  # for i in range(len(fta_members) - 2, -1, -1):
    m -= 1
    print(m)
    partner_country = fta_members[m]
    # print(partner_country)
    partner_country_code = id_fill(partner_country['COUNTRYID'])
    status_rank = partner_country['STATUSRANK']
    fta_details, hasRoo = get_fta_detail_by_id_and_partners(ftaID, reporter_country_code, partner_country_code, 870321, status_rank, isActive)
    
    # when the first time found a valid fta detail page
    # write to disk and skip checkinng for the rest of participating countries
    # print(fta_details)
    if hasRoo == True:
      fta_details['members_found'] = [reporter_country_code, partner_country_code]
      with open("data/fta_detail/{0}.json".format(ftaID), 'w') as outfile:
        json.dump(fta_details, outfile)
      break

def try_to_download_fta_details():
  # take only ROO available and status is in force or inactive
  with open("data/fta_list.json", 'r') as json_file:
    fta_list = json.load(json_file)
    fta_list = list(filter(lambda f: f['RooAvailable'] == True and (f['StatusDesc'] == 'Inactive'), fta_list))
    # fta_list = list(filter(lambda f: f['RooAvailable'] == True and (f['StatusDesc'] == 'In force' or f['StatusDesc'] == 'Inactive'), fta_list))
  
  # get ftas for given IDs
  # with open("FtaId.json", 'r') as json_file:
  #   fta_list = list(map(lambda fta: {'FtaId': fta, 'StatusDesc': 'In force'}, json.load(json_file)))

  # print(fta_list)
  # return
  # print(len(fta_list))
  # return

  # with open("data/missing.json", 'r') as json_file:
  #   fta_list = json.load(json_file)

  done = ["47","48","68","94","100","1044","852","118","136","139","150","153","158","1077","124","197","199","259","281","285","326","337","342","356","371","379","381","387","464","465","961","873","605","633","647","648","653","969","872","899"]

  i = 0
  total_missing = []
  for fta in fta_list:
    print(fta, i)
    ftaID = fta['FtaId']
    ftaStatus = fta['StatusDesc'] == 'In force'

    if str(ftaID) in done:
      continue

    missing = down_fta_details_finding_lowest_rank_for_every_pairing_countries(ftaID, ftaStatus)
    total_missing += missing
    # down_one_fta_detail_one_to_all(ftaID, ftaStatus) 
    i += 1
  print(total_missing)

def spell():
  with open("data/fta_list.json", 'r') as json_file:
    fta_list = json.load(json_file)
  fta_list = list(filter(lambda f: f['RooAvailable'] == True and (f['StatusDesc'] == 'In force' or f['StatusDesc'] == 'Inactive'), fta_list))

  missinng_fta = []
  for fta in fta_list:
    ftaID = fta['FtaId']
    ftaStatus = fta['StatusDesc'] == 'In force'
    if not os.path.exists("data/fta_detail/{0}.json".format(ftaID)):
      with open("data/fta_meta/{0}.json".format(ftaID), 'r') as json_file:
        fta_members = json.load(json_file)
        print(ftaID, ftaStatus, len(fta_members))
        missinng_fta.append({'FtaId': ftaID, 'StatusDesc': fta['StatusDesc']})

  # return
  with open("data/missing.json", 'w') as outfile:
    json.dump(missinng_fta, outfile)

# spell()
# exit()
# magic()

# try_to_download_fta_details()
# exit()

name_set = set()

def parse_long_fta_detail_file_name(filename):
  segs = filename.split('.json')[0].split('_')
  return { 'ftaID': segs[0], 'reporter': segs[1], 'partner': segs[2], 'rank': segs[3], 'productCode': segs[4] }

def fta_info_extract_one(file, segs):
  ftaID = segs['ftaID']
  with open("data/fta_detail_multi_full/{0}".format(file), 'r') as json_file:
    fta_detail = json.load(json_file)

  # print(fta_detail)
  ftaRooDetails = fta_detail['FtaRooDetails']
  ftaRooDetailInfo = fta_detail['FtaRooDetailInfo']
  ftaProvisions = fta_detail['FtaProvisions']

  row = {}
  row['reporter'] = segs['reporter']
  row['partner'] = segs['partner']
  row['rank'] = segs['rank']
  row['productCode'] = segs['productCode']
  row['FtaId'] = ftaID

  if ftaRooDetails == None:
    return row

  row['FtaCode'] = ftaRooDetails['FtaCode']
  row['FtaName'] = ftaRooDetails['FtaName']
  row['FtaStatusDesc'] = ftaRooDetails['FtaStatusDesc']
  row['FtaStatusDate'] = ftaRooDetails['FtaStatusDate']
  row['FtaType'] = ftaRooDetails['Type']
  row['FtaScope'] = ftaRooDetails['Scope']

  for duty in ftaRooDetails['Duties']:
    row[duty['Name']] = duty['percentage']

  i = 0
  for rooData in ftaRooDetailInfo['RooData']:
    keyNameRooCode = 'RooCode' + '_' + str(i)
    row[keyNameRooCode] = rooData['RooCode']
    keyNameRooText = 'RooText' + '_' + str(i)
    row[keyNameRooText] = rooData['RooText']
    keyNameProductAffected = 'ProductAffected' + '_' + str(i)
    row[keyNameProductAffected] = rooData['ProductAffected']
    i += 1

  for rooProvision in ftaProvisions['RooProvision']:
    row['Roo_' + rooProvision['ProvisionAbbrev']] = rooProvision['ProvisionValue']
  
  for cooProvision in ftaProvisions['CooProvision']:
    row['Coo_' + cooProvision['ProvisionAbbrev']] = cooProvision['ProvisionValue']

  name_set.update(list(row.keys()))
  # print(row)
  return row

# try_to_download_fta_details()

# fta_info_extract_one(828)
# exit()

files = os.listdir('./data/fta_detail_multi_full')
print(files)

# for file in files:
#   segs = parse_long_fta_detail_file_name(file)
#   print(segs)


# with open("data/fta_list.json", 'r') as json_file:
#   fta_list = json.load(json_file)
#   fta_list = list(filter(lambda f: f['RooAvailable'] == True and (f['StatusDesc'] == 'In force' or f['StatusDesc'] == 'Inactive'), fta_list))

rows = [fta_info_extract_one(file, parse_long_fta_detail_file_name(file)) for file in files]

with open('ftas_extended_full_without_early_40.csv', 'w', encoding='UTF8', newline='') as f:
  writer = csv.DictWriter(f, fieldnames=name_set)
  writer.writeheader()
  writer.writerows(rows)
