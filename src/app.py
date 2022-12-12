import time
import emoji as emj
import random
import json
import requests
from flask import render_template
from flask import current_app as app
from flask import Flask
from enum import Enum


good_emoji = [':thumbs_up:',
              ':thumbs_up_dark_skin_tone:',
              ':thumbs_up_light_skin_tone:',
              ':thumbs_up_medium-dark_skin_tone:',
              ':thumbs_up_medium-light_skin_tone:',
              ':thumbs_up_medium_skin_tone:',
              ':rocket:',
              ':T-Rex:',
              ':bridge_at_night:',
              ':check_mark_button:',
              ]
maybe_emoji = [':confounded_face:',
               ':ambulance:',
               ':disappointed_face:',
               ':face_with_head-bandage:',
               ':face_with_thermometer:',
               ]
bad_emoji = [':thumbs_down:',
             ':SOS_button:',
             ':angry_face:',
             ':angry_face_with_horns:',
             ':cold_face:',
             ':enraged_face:',
             ':collision:',
             ':crying_cat:',
             ':crying_face:',
             ':down_arrow:',
             ':face_vomiting:',
             ':face_with_crossed-out_eyes:',
             ':face_with_diagonal_mouth:',
             ':face_with_open_mouth:',
             ':face_with_peeking_eye:',
             ':face_with_raised_eyebrow:',
             ':face_with_rolling_eyes:',
             ':face_with_spiral_eyes:',
             ':face_with_steam_from_nose:',
             ':face_with_symbols_on_mouth:',
             ]


class SystemState(Enum):
    ACTIVE = 1
    DOWN = 2
    DEGRADED = 3
    MAINTNAINCE = 4
    UNKNOWN = 5


def create_app():
    """Construct the core application."""
    app = Flask(__name__, template_folder="templates")

    with app.app_context():
        return app


app = create_app()


def get_perlmutter_status_title(name: str = "perlmutter"):
    app.logger.info(name)
    if name == 'favicon.ico':
        return {'state': SystemState.UNKNOWN,
                'notes': f'Status of {name} unknown'
                }

    respose = requests.get(f'https://api.nersc.gov/api/v1.2/status/{name}',
                           headers={'accept': 'application/json'})

    app.logger.info(respose.text)
    try:
        data = json.loads(respose.text)
    except json.decoder.JSONDecodeError:
        return {'state': SystemState.UNKNOWN,
                'notes': f'Status of {name} unknown'
                }
    app.logger.debug(data)

    if data['status'] == 'active':
        state = SystemState.ACTIVE
        if data['description'] == "System Degraded":
            state = SystemState.DEGRADED
    else:
        state = SystemState.DOWN
        if data['description'] == "Scheduled Maintenance":
            state = SystemState.MAINTNAINCE

    event_time, notes = get_notes(data['notes'])
    return {
        'state': state,
        'active': (data['status'] == 'active'),
        'description': data['description'],
        'notes': notes,
        'time': event_time
    }


def get_notes(notes):
    try:
        notes = notes[0]
        tmp = notes.split(",")
        event_time = tmp[0]
        notes = tmp[-1]
    except Exception as err:
        app.logger.error(f"{type(err).__name__}: {err}")
        return time.time(), ""

    return event_time, notes


@app.route('/', defaults={'name': 'perlmutter'})
@app.route('/<path:name>')
def home(name):
    if name == 'favicon.ico':
        return render_template("home.html")
    status = get_perlmutter_status_title(name)

    match status['state']:
        case SystemState.ACTIVE:
            color = "MediumSeaGreen"
            emoji = random.choice(good_emoji)
            notes = ""
            title = f"YES! {name} is up!"
        case SystemState.DEGRADED:
            color = "Coral"
            emoji = random.choice(maybe_emoji)
            notes = status['notes']
            title = f"Maybe? {name} is degraded."
        case SystemState.DOWN:
            color = "#A93226"
            emoji = random.choice(bad_emoji)
            notes = status['notes']
            title = f"NO! {name} is down!"
        case SystemState.MAINTNAINCE:
            color = "RoyalBlue"
            emoji = random.choice(maybe_emoji)
            notes = status['notes']
            title = f"No, {name} is down for maintenance."
        case SystemState.UNKNOWN:
            color = "MediumPurple"
            emoji = random.choice(bad_emoji)
            notes = status['notes']
            title = f"System {name} not found!"

    return render_template(
        "home.html",
        description=emj.emojize(emoji),
        notes=notes,
        color=color,
        title=title,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
