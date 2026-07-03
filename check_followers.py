import os
import json
import smtplib
from email.message import EmailMessage
import instaloader
from datetime import datetime, timezone

USERNAME = "creators.almanac"
TARGET = 500000
STATE_FILE = "state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "sent": False,
            "pre_alert_sent": False,
            "last_check": None
        }

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def should_check(state, followers):
    now = datetime.now(timezone.utc)

    if state["last_check"] is None:
        return True

    last = datetime.fromisoformat(state["last_check"])

    hours_since = (now - last).total_seconds() / 3600

    if followers < 499000:
        return hours_since >= 6
    else:
        return hours_since >= 1


def update_last_check(state):
    state["last_check"] = datetime.now(
        timezone.utc
    ).isoformat()

    save_state(state)

def send_499k_email(followers):
    sender = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASSWORD"]
    receiver = os.environ["ALERT_EMAIL"]

    msg = EmailMessage()
    msg["Subject"] = f"🔥 {USERNAME} is about to hit 500k!"
    msg["From"] = sender
    msg["To"] = receiver

    msg.set_content(
        f"""
Heads up!

@{USERNAME} has reached {followers:,} followers.

500k is getting close. Keep an eye on Instagram!
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

def send_email(followers):
    sender = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASSWORD"]
    receiver = os.environ["ALERT_EMAIL"]

    msg = EmailMessage()
    msg["Subject"] = f"🚀 {USERNAME} hit {followers:,} followers!"
    msg["From"] = sender
    msg["To"] = receiver

    msg.set_content(
        f"""
Your friend @{USERNAME} has reached {followers:,} followers!

Go congratulate them before everyone else!
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)


def main():
    state = load_state()

    if state["sent"]:
        print("Email already sent.")
        return

    loader = instaloader.Instaloader()

    profile = instaloader.Profile.from_username(
        loader.context,
        USERNAME
    )

    followers = profile.followers

    print(f"Followers: {followers}")

    if not should_check(state, followers):
        print("Skipping check.")
        return

    update_last_check(state)

    # Send early alert at 499k
    if followers >= 499000 and not state["pre_alert_sent"]:
        send_499k_email(followers)

        state["pre_alert_sent"] = True
        save_state(state)

        print("499k email sent.")

    # Send final alert at 500k
    if followers >= TARGET and not state["sent"]:
        send_email(followers)

        state["sent"] = True
        save_state(state)

        print("500k email sent.")
    else:
        print("Target not reached.")
if __name__ == "__main__":
    main()