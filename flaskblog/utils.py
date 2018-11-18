import os
import secrets

from PIL import Image
from flask import url_for, current_app
from flask_mail import Message

from flaskblog import mail


def image_upload(image, path, size):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(image.filename)
    image_name = random_hex + f_ext
    image_path = os.path.join(current_app.root_path, path, image_name)

    # Resize uploaded image
    i = Image.open(image)
    i.thumbnail(size)
    i.save(image_path)

    return image_name


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Reset Password Request',
                  sender='noreplay@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_password', token=token, _external=True)}

If you did not make this request simply ignore this email and no changes will be made.
'''

    mail.send(msg)