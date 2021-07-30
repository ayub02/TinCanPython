import requests
import json
from examples.resources import lrs_properties
from requests_toolbelt.multipart import decoder

# Headers and url for POST request
auth = (lrs_properties.username, lrs_properties.password)
custom_boundary = "abcABC0123'()+_,-./:=?"
headers = {'X-Experience-API-Version': '1.0.1', 'Content-Type': "multipart/mixed; boundary={}".format(custom_boundary)}
url = lrs_properties.endpoint + 'statements?'

# Defining statement and attachment as files with content-type and headers
files = {
    'randomField1': ('randomFilename1', lrs_properties.statement.to_json(), 'application/json'),
    'randomField2': ('randomFilename2', lrs_properties.attachments_json, 'application/json',
                     {'Content-Transfer-Encoding': 'binary', 'X-Experience-API-Hash': lrs_properties.sha256_attachments})}

# Sending POST request with custom header
print('Saving statement with attachment')
requests.packages.urllib3.filepost.choose_boundary = lambda: custom_boundary
response = requests.post(url, headers=headers, files=files, auth=auth)

# Printing response to POST request
print('Response code: ', response.status_code)
print('Response: ', response.text)
print('Header: ', response.request.headers)
print('Request: \n', response.request.body.decode('utf-8'))
if response.status_code == 200:
    returned_id = response.text[2:-2]
    print('Id of saved statement: ', returned_id)

    # Fetching statement based on ID
    print('\nFetching statement based on ID')
    headers = {'X-Experience-API-Version': '1.0.1'}
    url = 'https://cloud.scorm.com/lrs/GKR3IAMSC1/statements?statementId={}&related_activities=True&related_agents=True&limit=1&attachments=True'.format(
        returned_id)
    response = requests.get(url, headers=headers, auth=auth)
    # Printing response to GET request
    print('Response code: ', response.status_code)

    multipart_data = decoder.MultipartDecoder.from_response(response)
    response_headers = []
    response_data = []
    for part in multipart_data.parts:
        response_headers.append({key.decode(): val.decode() for key, val in dict(part.headers).items()})
        response_data.append(json.loads(part.text))
        print('\nHeader: ', response_headers[-1])
        print('Text: ', response_data[-1])
