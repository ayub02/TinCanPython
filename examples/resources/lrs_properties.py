"""
Contains user-specific information for testing.
"""
import json
import hashlib
from tincan import (
    RemoteLRS,
    Statement,
    Agent,
    Verb,
    Activity,
    Attachment,
    Context,
    Result,
    Score,
    LanguageMap,
    ActivityDefinition,
    StateDocument,
    context_activities,
)


def interactionTypeMap(_response_type, _input_type):
    if _response_type == 'stringresponse' and _input_type == 'textline':
        return 'fill-in'
    elif _response_type == 'optionresponse' and _input_type == 'optioninput' or \
            _response_type == 'choiceresponse' and _input_type == 'checkboxgroup' or \
            _response_type == 'multiplechoiceresponse' and _input_type == 'choicegroup':
        return 'choice'
    elif _response_type == 'numericalresponse' and _input_type == 'formulaequationinput':
        return 'numeric'
    return 'other'


endpoint = "https://cloud.scorm.com/lrs/GKR3IAMSC1/"
version = "1.0.1"
username = "nFKvuMZ8od9UHjRfezg"
password = "o8Bpo5NkSGvYoRcTcx8"

file_path = 'problem_check(server).json'
with open(file_path) as f:
    event = json.load(f)

actor = Agent(
    objectType='Agent',
    openid='https://openedx.org/users/user-v1/32e08e30-f8ae-4ce2-94a8-c2bfe38a70cb',
)

verb = Verb(
    id='http://adlnet.gov/expapi/verbs/answered',
    display=LanguageMap({'en-US': 'answered'}),
)

course = Activity(
    id=event['context']['course_id']
)
context_activities = context_activities.ContextActivities(
    parent=course
)
context = Context(
    context_activities=context_activities
)

score = Score(
    scaled=event['data']['grade']/event['data']['max_grade'],
    raw=event['data']['grade'],
    min=0,
    max=event['data']['max_grade'],
)

Objects = []
Results = []
for key, val in event['data']['submission'].items():
    Object = Activity(
        id=event['data']['problem_id'],
        definition=ActivityDefinition(
            description=LanguageMap({'en-US': val['question']}),
            type='http://adlnet.gov/expapi/activities/cmi.interaction',
            interactionType=interactionTypeMap(val['response_type'], val['input_type']),
        ),
    )
    result = Result(
        success=True if event['data']['success'] == 'correct' else False,
        response=val['answer'],
        score=score,
    )
    Objects.append(json.loads(Object.to_json()))
    Results.append(json.loads(result.to_json()))

attachments = {
    'objects': Objects,
    'results': Results
}
attachments_json = json.dumps(attachments)
sha256_attachments = (hashlib.sha256(attachments_json.encode())).hexdigest()

attachment = Attachment(
    usageType="http://id.tincanapi.com/attachment/supporting_media",
    display=LanguageMap({'en-US': "supporting media"}),
    description=LanguageMap({'en-US': "A media file that supports the experience. For example a video that shows the "
                                      "experience taking place"}),
    contentType="application/json",
    length=len(attachments_json),
    sha2=sha256_attachments,
)

statement = Statement(
    actor=actor,
    verb=verb,
    object=Object,
    context=context,
    result=result,
    attachments=attachment,
)
