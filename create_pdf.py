# Created by Reb (rew@alum.mit.edu)
# Updated 2/14/20

import csv
import datetime
import math
import os
import sys

import jinja2
import pdfkit
from PyPDF2 import PdfFileReader, PdfFileWriter

timestamp = datetime.datetime.now().strftime("%m.%d.%Y_%H.%M.%S")

# The responses for which cards will be created - downloaded as CSV from Google form responses
RESPONSES_CSV = "csv/example_responses.csv"

# Describes columns of responses CSV. Depends on setup of Google form, may change year to year
MAX_RECIPIENTS_PER_SENDER = 12 # max number of ppl each buyer can send flowers to (per form submission)
SENDER_INFO_LEN = 7 # number of csv fields associated with the sender
RECIPIENT_INFO_LEN = 7 # number of csv fields associated with each recipient
SENDER_DISPLAY_IDX = 94 # index of the column containing the sender's display name
DELIVERY_IDX = 6 # index of pickup or delivery

# Parameters for adjusting font size based on message length / size of card
DEFAULT_FONT_SZ = 16 # the default text size
MAX_MSG_LEN = 180 # after this many characters, the font size will begin to scale down
FONT_MULTIPLIER = 6 # how fast to scale down the font

# Specify various input files for formatting, these probably won't need to be changed year to year
FRONT_IMG_FILE = f"file://{os.path.abspath('images/front.png')}"
BACK_IMG_FILE = f"file://{os.path.abspath('images/back.png')}"
MESSAGE_TEMPLATE_FILE = "html/message_template.html"
INFO_TEMPLATE_FILE = "html/info_template.html"
CSS_FILE = "html/style.css"
MESSAGE_PDF_FILE = "out/messages.pdf"
OUT_PDF_FILE = f"out/finished_{timestamp}.pdf"
INFO_PDF_FILE = "out/info.pdf"


def get_font_size(message):
    if len(message) <= MAX_MSG_LEN:
        return DEFAULT_FONT_SZ
    else:
        overage = len(message) - MAX_MSG_LEN
        change = math.log(1 + overage / MAX_MSG_LEN) * FONT_MULTIPLIER # logarithmic scaling - looked best from experimenting
        return DEFAULT_FONT_SZ - change

def get_card_from_recipient_data(row, recipient_index, sender, delivery):
    recipient_info = row[recipient_index : recipient_index + RECIPIENT_INFO_LEN]
    recipient, recipient_email, num_flowers, address, room_no, message, _ = recipient_info

    if not recipient: # happens for rows where people don't designate all 12 possible recipients
        return None

    message = message.strip()
    if room_no:
        address = f"{address} {room_no}"
    font_size = get_font_size(message)

    return {
        "delivery": delivery,
        "sender": sender,
        "recipient": recipient,
        "address": address,
        "num_flowers": num_flowers,
        "message": message,
        "font_size": font_size,
    }

def generate_cards_from_csv(csv_file):
    cards = []
    with open(csv_file) as responses:
        reader = csv.reader(responses, delimiter=',')
        first = True
        for row in reader:
            # skip first row
            if first:
                first = False
                continue

            # sender data
            sender = row[SENDER_DISPLAY_IDX]
            if not sender:
                sender = "Anonymous"
            delivery = True if row[DELIVERY_IDX] == "Delivery" else False # Delivery or pickup?

            for ri in range(MAX_RECIPIENTS_PER_SENDER):
                recipient_index = ri * RECIPIENT_INFO_LEN + SENDER_INFO_LEN
                card = get_card_from_recipient_data(row, recipient_index, sender, delivery)
                if card: cards.append(card)
    return cards

def create_individual_pdfs(cards):
    loader = jinja2.FileSystemLoader(searchpath="./")
    env = jinja2.Environment(loader=loader)
    message_template = env.get_template(MESSAGE_TEMPLATE_FILE)
    info_template = env.get_template(INFO_TEMPLATE_FILE)

    reordered_cards = []
    for i in range(0, len(cards), 2):
        first = cards[i]
        if i + 1 < len(cards):
            second = cards[i + 1]
        else:
            second = {}
        reordered_cards.extend([second, first])

    messages_rendered = message_template.render(cards=cards, back_img=BACK_IMG_FILE, front_img=FRONT_IMG_FILE)
    info_rendered = info_template.render(cards=reordered_cards, back_img=BACK_IMG_FILE, front_img=FRONT_IMG_FILE)
    pdfkit.from_string(messages_rendered, MESSAGE_PDF_FILE, css=CSS_FILE)
    pdfkit.from_string(info_rendered, INFO_PDF_FILE, css=CSS_FILE)

def splice_pdfs_into_final():
    with open(MESSAGE_PDF_FILE, "rb") as messages:
        with open(INFO_PDF_FILE, "rb") as info:
            with open(OUT_PDF_FILE, 'wb') as out:
                output_stream = sys.stdout
                writer = PdfFileWriter()
                messages_reader = PdfFileReader(messages)
                info_reader = PdfFileReader(info)

                for i in range(messages_reader.getNumPages()):
                    writer.addPage(messages_reader.getPage(i))
                    writer.addPage(info_reader.getPage(i))

                writer.write(out)


if __name__ == "__main__":
    cards = generate_cards_from_csv(RESPONSES_CSV)
    create_individual_pdfs(cards)
    splice_pdfs_into_final()
    