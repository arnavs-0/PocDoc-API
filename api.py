from flask import Flask, request
from re import match
from requests import get, post
from keys import APP_ID, API_KEY


app = Flask(__name__)


@app.route('/symptoms', methods=['GET'])
def symptoms():
    return {'symptoms': infermedica_symptoms}, 200


@app.route('/diagnosis', methods=['POST'])
def diagnosis():
    arguments = request.json if request.json else {}
    try:
        assert 'gender' in arguments, 'Missing <gender> argument'
        assert str(arguments['gender']).lower() in ['male', 'female'], '<gender> argument requires value of "male" or "female"'
        assert 'age' in arguments, 'Missing <age> argument'
        assert match(r'^[0-9]+$', str(arguments['age'])), '<age> argument requires integer value'
        assert 'symptoms' in arguments, 'Missing <symptoms> argument'
        assert isinstance(arguments['symptoms'], list), '<symptoms> argument requires list of symptoms'
    except AssertionError as error:
        return {'message': str(error)}, 400

    body = {'sex': arguments['gender'].lower(), 'age': int(arguments['age'])}
    symptom_ids = []
    for experienced_symptom in arguments['symptoms']:
        symptom_ids += [{'id': experienced_symptom, 'choice_id': 'present'}]
    body.update({'evidence': symptom_ids})

    diagnosis_request = post(base+'/diagnosis', json=body, headers=__headers).json()
    infermedica_diagnosis = []
    try:
        conditions = diagnosis_request['conditions']
        for condition in conditions:
            infermedica_diagnosis += [{'name': condition['common_name'], 'probability': condition['probability']*100}]
    except KeyError:
        return {'message': 'Invalid request'}, 400
    return {'conditions': infermedica_diagnosis}, 200


__headers = {'App-Id': APP_ID, 'App-Key': API_KEY}

base = 'https://api.infermedica.com/v2'

infermedica_symptoms = []
symptoms_request = get(base+'/symptoms', headers=__headers).json()

for symptom in symptoms_request:
    infermedica_symptoms += [{'id': symptom['id'], 'name': symptom['common_name']}]

if __name__ == '__main__':
    app.run()
