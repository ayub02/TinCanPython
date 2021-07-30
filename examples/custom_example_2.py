import requests
from requests_toolbelt.multipart import decoder
import re
from requests_toolbelt import MultipartEncoder
import json
import hashlib
import uuid
from tincan import (
    RemoteLRS,
    Statement,
    Agent,
    Verb,
    Activity,
    LanguageMap,
    ActivityDefinition,
    Attachment
)

plain_text = 'here is a simple attachment'
sha256_of_plain_text = (hashlib.sha256(plain_text.encode())).hexdigest()   # SHA256

actor = Agent(
    name='Space',
    mbox='mailto:tincanpython@tincanapi.com',
)
verb = Verb(
    id='http://adlnet.gov/expapi/verbs/experienced',
    display=LanguageMap({'en-US': 'experienced'}),
)
Object = Activity(
    id='http://tincanapi.com/TinCanPython/Example/0',
    definition=ActivityDefinition(
        name=LanguageMap({'en-US': 'TinCanPython Library'}),
        description=LanguageMap({'en-US': 'Use of, or interaction with, the TinCanPython Library'}),
    ),
)
attachment = Attachment(
    usage_type='http://id.tincanapi.com/attachment/supporting_media',
    display={"en-US": "supporting media"},
    description={"en-US": "A media file that supports the experience. For example a video that shows the experience "
                          "taking place"},
    contentType='text/plain; charset=ascii',
    length=len(plain_text),
    sha2=sha256_of_plain_text
)

statement = Statement(
    actor=actor,
    verb=verb,
    object=Object,
    attachments=attachment
)
print(statement.to_json())
headers = {'X-Experience-API-Version': '1.0.1', 'Content-Type': "multipart/mixed; boundary='abcABC0123()+_,-./:=?'"}
auth = ('nFKvuMZ8od9UHjRfezg', 'o8Bpo5NkSGvYoRcTcx8')
files = {
    'key1': ('val1', statement.to_json(), 'application/json'),
    'key2': ('val2', plain_text, 'text/plain', {'Content-Transfer-Encoding': 'binary',
                                                'X-Experience-API-Hash': sha256_of_plain_text})

}

m = MultipartEncoder(files, boundary="abcABC0123'()+_,-./:=?")
# _data = '--abcABC0123\'()+_,-./:=?\r\nContent-Type: application/json\r\n\r\n{"version": "1.0.3", "actor": {"objectType": "Agent", "name": "Latest", "mbox": "mailto:tincanpython@tincanapi.com"}, "verb": {"id": "http://adlnet.gov/expapi/verbs/experienced", "display": {"en-US": "experienced"}}, "object": {"id": "http://tincanapi.com/TinCanPython/Example/0", "objectType": "Activity", "definition": {"name": {"en-US": "TinCanPython Library"}, "description": {"en-US": "Use of, or interaction with, the TinCanPython Library"}}}, "attachments": [{"usageType": "http://id.tincanapi.com/attachment/supporting_media", "display": {"en-US": "supporting media"}, "contentType": "text/plain; charset=ascii", "length": 27, "sha2": "495395e777cd98da653df9615d09c0fd6bb2f8d4788394cd53c56a3bfdcd848a", "description": {"en-US": "A media file that supports the experience. For example a video that shows the experience taking place"}}]}\r\n--abcABC0123\'()+_,-./:=?\r\nContent-Type: text/plain\r\nContent-Transfer-Encoding: binary\r\nX-Experience-API-Hash: 495395e777cd98da653df9615d09c0fd6bb2f8d4788394cd53c56a3bfdcd848a\r\n\r\nhere is a simple attachment\r\n--abcABC0123\'()+_,-./:=?--\r\n'.encode()

data = m.to_string()
data_str = data.decode('UTF-8')
# print('type of data', type(data), 'data', data)
# print('type of data_str', type(data_str), 'data_str', data_str)
my_list = data_str.split("\r\n")
my_str = ''
for i, val in enumerate(my_list):
    if 'Content-Disposition' not in val:
        if i == 0:
            my_str = val
        else:
            my_str = my_str + "\r\n" + val

print('my_str', my_str.encode('UTF-8'))

req = requests.post('https://cloud.scorm.com/lrs/GKR3IAMSC1/statements?',
                    headers={'X-Experience-API-Version': '1.0.1',
                             'Content-Type': "multipart/mixed; boundary=abcABC0123'()+_,-./:=?"},
                    data=my_str.encode('UTF-8'), auth=auth)

print(req.status_code)
print(req.text)
s = (re.search("\".*\"", req.text)).span()
returned_id = req.text[s[0]+1:s[1]-1]

# lrs = RemoteLRS(
#     version="1.0.1",
#     endpoint="https://cloud.scorm.com/lrs/GKR3IAMSC1/",
#     username="nFKvuMZ8od9UHjRfezg",
#     password="o8Bpo5NkSGvYoRcTcx8",
# )

# response = lrs.retrieve_statement(returned_id)
# print(returned_id)
# query = {
#     "statementId": returned_id,
#     "related_activities": True,
#     "related_agents": True,
#     "limit": 1,
#     "attachments": True,
# }

# print("querying statements...")
# response = lrs.query_statements(query)
#
# if not response.success:
#     raise ValueError("statement could not be retrieved")
# print('response:', response.data)
#

# headers = {'X-Experience-API-Version': '1.0.1', 'Authorization': 'Basic bkZLdnVNWjhvZDlVSGpSZmV6ZzpvOEJwbzVOa1NHdllvUmNUY3g4'}
# url = 'https://cloud.scorm.com/lrs/GKR3IAMSC1/statements?statementId=c4f7bcdf-91b6-4b98-93a0-efc40d87e7e0&related_activities=True&related_agents=True&limit=1&attachments=True'
# response = requests.get(url, headers=headers)
#
# multipart_data = decoder.MultipartDecoder.from_response(response)
# for part in multipart_data.parts:
#     print(part.headers)
#     print(part.text)  # Alternatively, part.text if you want unicode