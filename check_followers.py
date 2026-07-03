import os
import json
import smtplib
from email.message import EmailMessage
import instaloader

USERNAME = "friend_username"
TARGET = 500000
STATE_FILE = "state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"sent": False}

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


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

    if followers >= TARGET:
        send_email(followers)

        state["sent"] = True
        save_state(state)

        print("Email sent.")
    else:
        print("Target not reached.")


if __name__ == "__main__":
    main()