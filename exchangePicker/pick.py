#! python3
# The MIT License (MIT)
#
# Copyright (c) 2014 Alexandre Vaillancourt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""This script is used to set up a Christmas pick for a group of people. The 
pick information is sent by email.

Basically, after setting the data in the two data files, the script randomly 
selects a receiving participant for each particiant, and then sends the name 
of the participant they have to give a gift to by email. 

It is designed so that the initiator of the script is not aware of the 
distribution of the pick, except for his own. It is designed so that a 
participant can't pick herself.

The participants.json file contains the information of who's participating, with
their email, and to whom they can't give a gift. This is useful to mutually 
exlude members of a couple or of ppl living in the same houshold. 

The emailconfig.json should contain the information about the sender and it's
smtp configuration. 

Optionally, the end-user could set the peronal data in files named 
participants.local.json and emailconfig.local.config in ordre to avoid having to
commit sensitive data to a repository. 

It is suggested to output the generated random seed in case a participant does
not get his email with the name he picked. 

Names in participants.json (e.g. p1, and p2) must match as comparison is done on 
these strings. 

Please perform some dry runs before sending the real email :P 

...and don't cheat, you'll spoil all the fun ;)
"""

import json
import os
import random
import sys
from smtplib import SMTP
from email.mime.text import MIMEText
from email.header import Header

def load_config():
    """Loads the configuration data from the file 'emailconfig.local.json' if it 
    finds it or from the default file 'emailconfig.json', as a dict."""

    emailconfig = dict()

    file_path = 'emailconfig.json'
    if os.path.isfile('emailconfig.local.json') :
        file_path = 'emailconfig.local.json'
    with open(file_path, 'r') as emailconfig_file:
        emailconfig = json.load(emailconfig_file)

    return emailconfig

def load_participants():
    """Loads the participants data from the file 'participants.local.json' if it 
    finds it or from the default file 'participants.json', as a list."""

    participant_data = list()

    file_path = 'participants.json'
    if os.path.isfile('participants.local.json') :
        file_path = 'participants.local.json'
    with open(file_path, 'r') as particiants_file:
        participant_data = json.load(particiants_file)

    return participant_data

def arrange_participants(participant_data):
    """Splits the list of participans into the participans and the exclusions
    rules"""
    participant_list = participant_data["participants"]
    participant_exclusions = participant_data["exclusions"]

    return participant_list, participant_exclusions

def generate_assignements(participants, exclusions):
    # Test seed : 7919554390471891426
    seed = random.randint(0, sys.maxsize)
    print("random seed: " + str(seed))
    myRand = random.Random(seed)

    attribution = dict()
    is_done = False
    while not is_done:
        receivers = list()
        for person in participants[1:len(participants)]:
            #print(person[0])
            receivers.append(person[0])
        first = participants[0][0]
        current = first

        attribution = dict()
        should_restart = False
        while len(receivers) > 0 and not should_restart:
            potential_receivers = list()
            #print( "current: " + current )
            for receiver in receivers:
                if not( receiver == current ) and receiver not in exclusions[current]:
                    potential_receivers.append(receiver)
                    #print( "  potential: " + receiver )
            if len(potential_receivers) == 0:
                should_restart = True
                #print("restarting...")
            else:
                chosen_index = myRand.randint(0, len(potential_receivers) - 1)
                attribution[current] = potential_receivers[chosen_index]
                #print( "  chosen: " + attribution[current] )

                current = potential_receivers[chosen_index]
                receivers.remove(current)

        if not should_restart:
            attribution[current] = first

            # for key in attribution.keys():
            #     print(key + "->" + attribution[key])

            is_done = True

    return attribution


def send_a_mail(email_config, dest_name, dest_adress, picked_name, dry_run):
    subject = "La Pige de Noël"
    message_content = dest_name + "!\r\nLa personne que tu as pigée pour l'échange de cadeau de Noël est : \r\n" + picked_name
    msg = MIMEText(message_content.encode('utf-8'), 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = email_config["from_address"]
    msg['To'] = dest_adress

    if dry_run:
        print(msg.as_string())
        return

    smtp = SMTP(email_config["smtp_server"])
    try:
        smtp.set_debuglevel(True)
        smtp.noop()
        smtp.starttls()
        smtp.login(email_config["from_username"], email_config["from_password"])
        smtp.send_message(msg)

    except Exception as inst:
        print(inst)

    smtp.quit()

def test_email(email_config):

    subject = "Héèéè"
    message_content = "Contentééééééé\r\nhûhûhhû\r\n"
    msg = MIMEText(message_content.encode('utf-8'), 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = email_config["from_address"]
    msg['To'] = email_config["to_test_address"]


    smtp = SMTP(email_config["smtp_server"])
    try:
        smtp.set_debuglevel(True)
        print("\rdbg smtp.noop()")
        print(smtp.noop())

        print("\rdbg smtp.starttls()")
        print(smtp.starttls())

        print("\rdbg smtp.login()")
        print(smtp.login(email_config["from_username"], email_config["from_password"]))

        print("\rdbg smtp.send_message()")
        print(smtp.send_message(msg))
    except Exception as inst:
        print(inst)

    print("\rdbg smtp.quit()")
    print(smtp.quit())



if __name__ == "__main__":
    email_config = load_config()
    should_test_mail = False
    if should_test_mail:
        test_email(email_config)
    else:
        participants = load_participants()
        participants, exclusions = arrange_participants( participants )
        attribution = generate_assignements( participants, exclusions )

        participants_dict = dict()
        # prepare data for an easier send
        for participant in participants:
            participants_dict[participant[0]] = participant[1]
        # send the email
        for participant in participants_dict.keys():
            name = participant
            address = participants_dict[participant]
            pick = attribution[name]
            #print(name + "(" + address + ")" + "->" + pick)
            send_a_mail(email_config, name, address, pick, False)

    print("Done!\n")

    #print("\n\n\n\n\n")


