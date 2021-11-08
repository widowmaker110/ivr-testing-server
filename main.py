"""
    if ngrok is showing: http://[domain].ngrok.io -> http://localhost:3000,
    then set the port below to 3000. Make sure they match
"""
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from tinydb import TinyDB, Query
import uuid
from datetime import datetime
import json
import os

Tester = Query()

app = Flask(__name__)
db = TinyDB('./results/db.json')
path_to_json = './testSuite/'


@app.route("/voice", methods=['GET', 'POST'])
def voice():

    init_test_suite()

    current_item = get_current_test()
    print('voice function : current_item')
    print(current_item)
    current_index = int(current_item["currentIndex"])
    current_step = int(current_item["currentStep"])
    current_timeout = 0
    try:
        current_timeout = int(current_item["instructions"][current_index]["steps"][current_step]["timeout"])
    except:
        current_item["status"] = 'complete'
        db.update(current_item)
        print('CALL ENDED')

    resp = VoiceResponse()
    gather = Gather(num_digits=1, action='/gather', input="speech dtmf", timeout=current_timeout)
    gather.say('')
    resp.append(gather)
    resp.redirect('/voice')
    return str(resp)


@app.route('/gather', methods=['GET', 'POST'])
def gather():
    resp = VoiceResponse()
    current_item = get_current_test()
    print('gather function : current_item')
    print(current_item)
    current_index = int(current_item["currentIndex"])
    current_step = int(current_item["currentStep"])

    next_action = get_next_setp(current_item["instructions"], current_index, current_step)

    expected_instructions = get_expected_result(current_item["instructions"], current_index, current_step)
    number_of_instruction_files = len(current_item["instructions"])
    number_of_instructions_steps = len(current_item["instructions"][current_index]["steps"])

    result = {
        "file": current_item["instructions"][current_index]["file"],
        "step": expected_instructions
    }

    should_hang_up = False

    if "SpeechResult" in request.values:

        ivr_instruction = request.values['SpeechResult']

        # check to see if the expected result happned
        if ivr_instruction.lower() in expected_instructions:
            result["status"] = "passed"

            # increment where possible. Else, set to hang up
            if (current_step + 1) > number_of_instructions_steps and (current_index + 1) > number_of_instruction_files:
                should_hang_up = True
            elif (current_step + 1) > number_of_instructions_steps:
                current_index = current_index + 1
                current_step = 0
            else:
                current_step = current_step + 1

            current_item["currentIndex"] = current_index
            current_item["currentStep"] = current_step
        else:
            result["status"] = "failed"
            result["actualResult"] = ivr_instruction
            should_hang_up = True

    current_item["results"].append(result)
    db.update(current_item)

    # what to do next
    if next_action is None:
        # do nothing
        resp.say('')
        print('Nothing said')

    elif "press=" in next_action:
        resp.play('', digits=next_action.replace('press=', ''))
        print('Pressed: ' + next_action.replace('press=', ''))

    # say=
    else:
        resp.say(next_action.replace('say=', ''))
        print('Said: ' + next_action.replace('say=', ''))

    if should_hang_up:
        resp.hangup()
        print('CALL ENDED')

    resp.redirect('/voice')
    return str(resp)


def get_current_test():
    return db.search(Tester.status == 'in-progress')[0]


def init_test_suite():
    current_items = db.search(Tester.status == 'in-progress')

    if len(current_items) == 0:
        temp_new_record = {
            "unique_id": str(uuid.uuid4()),
            "status": 'in-progress',
            "startTimestamp": datetime.now().isoformat(),
            "endTimeStamp": None,
            "currentIndex": 0,
            "currentStep": 0,
            "instructions": [],
            "results": []
        }
        db.insert(temp_new_record)

        for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
            with open(path_to_json + file_name) as json_file:
                data = json.load(json_file)
                temp_list = temp_new_record["instructions"]
                temp_list.append(
                    {
                        "file": file_name,
                        "steps": data
                    }
                )
                temp_new_record["instructions"] = temp_list
                db.update(temp_new_record)


def get_expected_result(expected_instructions, current_index, current_step):
    responses = expected_instructions[current_index]["steps"][current_step]["expect"]
    return [each_string.lower() for each_string in responses]


def get_next_setp(expected_instructions, current_index, current_step):
    next_step = expected_instructions[current_index]["steps"][current_step]["then"]
    return next_step


app.run(debug=True, port=3000)
