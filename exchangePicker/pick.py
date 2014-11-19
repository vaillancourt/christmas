#! python3

import json
import os
import random
import sys
from smtplib import SMTP
from email.mime.text import MIMEText
from email.header import Header

def load_participants():
    """Loads the participants data from the file 'participants.local.json' if it 
    finds it or from the default file 'participants.json', as a dict."""

    participant_data = list()

    file_path = 'participants.json'
    if os.path.isfile('participants.local.json') :
        file_path = 'participants.local.json'
    with open(file_path, 'r') as particiants_file:
        participant_data = json.load(particiants_file)

    return participant_data

def arrange_participants(participant_data):
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


def send_a_mail(dest_name, dest_adress, picked_name, dry_run):
    subject = "La Pige de Noël"
    message_content = dest_name + "!\r\nLa personne que tu as pigée pour l'échange de cadeau de Noël est : \r\n" + picked_name
    msg = MIMEText(message_content.encode('utf-8'), 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = 'username@example.com'#fix
    msg['To'] = dest_adress

    if dry_run:
        print(msg.as_string())
        return

    smtp = SMTP("example.com")#fix
    try:
        #smtp.set_debuglevel(True)
        smtp.noop()
        smtp.starttls()
        smtp.login("fixusername@example.com","fixpassword")#fix
        smtp.send_message(msg)
    except Exception as inst:
        print(inst)

    smtp.quit()

def test_email():

    subject = "Héèéè"
    message_content = "Contentééééééé\r\nhûhûhhû\r\n"
    msg = MIMEText(message_content.encode('utf-8'), 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = 'username@example.com'
    msg['To'] = 'fixusername@example.com'


    smtp = SMTP("example.com")#fix
    try:
        smtp.set_debuglevel(True)
        print("\rdbg smtp.noop()")
        print(smtp.noop())

        print("\rdbg smtp.starttls()")
        print(smtp.starttls())

        print("\rdbg smtp.login()")
        print(smtp.login("fixusername@example.com","fixpassword")#fix

        print("\rdbg smtp.send_message()")
        print(smtp.send_message(msg))
    except Exception as inst:
        print(inst)

    print("\rdbg smtp.quit()")
    print(smtp.quit())



if __name__ == "__main__":
    # test_email()
    participants = load_participants()
    participants, exclusions = arrange_participants( participants )
    attribution = generate_assignements( participants, exclusions )

    participants_dict = dict()
    for participant in participants:
        participants_dict[participant[0]] = participant[1]
    for participant in participants_dict.keys():
        name = participant
        address = participants_dict[participant]
        pick = attribution[name]
        print(name + "(" + address + ")" + "->" + pick)
        #send_a_mail(name, address, pick, False)

    print("Done!\n")

    #print("\n\n\n\n\n")


