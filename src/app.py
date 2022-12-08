import emoji as emj
import random
import json
import requests
from flask import render_template
from flask import current_app as app
from flask import Flask


def create_app():
    """Construct the core application."""
    app = Flask(__name__, template_folder="templates")

    with app.app_context():
        return app


app = create_app()

"""Route declaration."""


def get_perlmutter_status_title(name: str = "perlmutter"):
    app.logger.info(name)
    if name == 'favicon.ico':
        return None

    respose = requests.get(f'https://api.nersc.gov/api/v1.2/status/{name}',
                           headers={'accept': 'application/json'})

    app.logger.info(respose.text)
    data = json.loads(respose.text)
    app.logger.debug(data)

    return {
        'active': (data['status'] == 'active'),
        'description': data['description'],
        'notes': data['notes']
    }


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
bad_emoji = [':thumbs_down:',
             ':SOS_button:',
             ':ambulance:',
             ':angry_face:',
             ':angry_face_with_horns:',
             ':cold_face:',
             ':enraged_face:',
             ':collision:',
             ':confounded_face:',
             ':crying_cat:',
             ':crying_face:',
             ':disappointed_face:',
             ':down_arrow:',
             ':face_vomiting:'
             ':face_vomiting:',
             ':face_with_crossed-out_eyes:',
             ':face_with_diagonal_mouth:',
             ':face_with_head-bandage:',
             ':face_with_open_mouth:',
             ':face_with_peeking_eye:',
             ':face_with_raised_eyebrow:',
             ':face_with_rolling_eyes:',
             ':face_with_spiral_eyes:',
             ':face_with_steam_from_nose:',
             ':face_with_symbols_on_mouth:',
             ':face_with_thermometer:',
             ]


@app.route('/', defaults={'name': 'perlmutter'})
@app.route('/<path:name>')
def home(name):
    if name == 'favicon.ico':
        return render_template("home.html")
    status = get_perlmutter_status_title(name)
    if 'active' in status and status['active']:
        if status['description'] == "System Degraded":
            color = "Coral"
            emoji = random.choice(good_emoji)
            notes = status['notes']
            title = f"Maybe? {name} is degraded."
        else:
            color = "MediumSeaGreen"
            emoji = random.choice(good_emoji)
            notes = ""
            title = f"YES! {name} is up!"
    else:
        color = "#A93226"
        emoji = random.choice(bad_emoji)
        notes = status['notes']
        title = f"NO! {name} is down!"

    return render_template(
        "home.html",
        description=emj.emojize(emoji),
        notes=notes,
        color=color,
        title=title,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
