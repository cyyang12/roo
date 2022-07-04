
import requests
  
FIND_ROO_ROOT = 'https://findrulesoforigin.org/api'
URL_ROO_LIST_ALL = FIND_ROO_ROOT + "/getftalist"
URL_FTA_META = FIND_ROO_ROOT + "/getftareportingctrystatus"
URL_FTA_INFO = FIND_ROO_ROOT + "/getftaroo"

def json_req_with_param(url, params):
  r = requests.get(url = url, params = params)
  return r.json()

def roo_only_list():
  data = json_req_with_param(URL_ROO_LIST_ALL, {'showall': True })
  roo_available_list = list(filter(lambda d: d['RooAvailable'] == True, data))
  print(len(data))
  print(len(roo_available_list))
  return roo_available_list

def get_one_fta_metadata(ftaID):
  data = json_req_with_param(URL_FTA_META, {'ftaid': ftaID })
  return list(map(lambda c: c['COUNTRYID'], data))

def get_one_fta_detail(reporter, partner, productCode):
  data = json_req_with_param(URL_FTA_INFO, {'reporter': reporter, 'partner': partner, 'product': productCode })
  print(data)

roo_list = roo_only_list()

# get_one_fta_detail(842, 124, 87032101)

l = get_one_fta_metadata(978)
print(l)