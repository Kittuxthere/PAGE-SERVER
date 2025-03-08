from flask import Flask, request, render_template_string, jsonify

import requests

import os

import re

import time

import threading

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

 

# Login credentials

ADMIN_USERNAME = "POST"

ADMIN_PASSWORD = "KITTU_XD"

class FacebookCommenter:

    def __init__(self):

        self.comment_count = 0

    def comment_on_post(self, cookies, post_id, comment, delay):

        with requests.Session() as r:

            r.headers.update({

                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7',

                'sec-fetch-site': 'none',

                'accept-language': 'id,en;q=0.9',

                'Host': 'mbasic.facebook.com',

                'sec-fetch-user': '?1',

                'sec-fetch-dest': 'document',

                'accept-encoding': 'gzip, deflate',

                'sec-fetch-mode': 'navigate',

                'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.166 Mobile Safari/537.36',

                'connection': 'keep-alive',

            })

            response = r.get(f'https://mbasic.facebook.com/{post_id}', cookies={"cookie": cookies})

            next_action_match = re.search('method="post" action="([^"]+)"', response.text)

            fb_dtsg_match = re.search('name="fb_dtsg" value="([^"]+)"', response.text)

            jazoest_match = re.search('name="jazoest" value="([^"]+)"', response.text)

            if not (next_action_match and fb_dtsg_match and jazoest_match):

                print("Required parameters not found.")

                return

            next_action = next_action_match.group(1).replace('amp;', '')

            fb_dtsg = fb_dtsg_match.group(1)

            jazoest = jazoest_match.group(1)

            data = {

                'fb_dtsg': fb_dtsg,

                'jazoest': jazoest,

                'comment_text': comment,

                'comment': 'Submit',

            }

            r.headers.update({

                'content-type': 'application/x-www-form-urlencoded',

                'referer': f'https://mbasic.facebook.com/{post_id}',

                'origin': 'https://mbasic.facebook.com',

            })

            response2 = r.post(f'https://mbasic.facebook.com{next_action}', data=data, cookies={"cookie": cookies})

            if 'comment_success' in response2.url and response2.status_code == 200:

                self.comment_count += 1

                print(f"Comment {self.comment_count} successfully posted.")

            else:

                print(f"Comment failed with status code: {response2.status_code}")

    def process_inputs(self, cookies, post_id, comments, delay):

        cookie_index = 0

        while True:

            for comment in comments:

                comment = comment.strip()

                if comment:

                    time.sleep(delay)

                    self.comment_on_post(cookies[cookie_index], post_id, comment, delay)

                    cookie_index = (cookie_index + 1) % len(cookies)

@app.route("/", methods=["GET", "POST"])

def index():

    if request.method == "POST":

        post_id = request.form['post_id']

        delay = int(request.form['delay'])

        cookies_file = request.files['cookies_file']

        comments_file = request.files['comments_file']

        cookies = cookies_file.read().decode('utf-8').splitlines()

        comments = comments_file.read().decode('utf-8').splitlines()

        if len(cookies) == 0 or len(comments) == 0:

            return "Cookies or comments file is empty."

        commenter = FacebookCommenter()

        commenter.process_inputs(cookies, post_id, comments, delay)

        return "Comments are being posted. Check console for updates."

    

    form_html = '''

    <!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>POST</title>

    <style>

        body {

            font-family: 'Poppins', sans-serif;

            background: #FFF9C4;

            color: #333;

            display: flex;

            flex-direction: column;

            min-height: 100vh;

            overflow-y: auto;

            align-items: center;

        }

        .container {

            background: rgba(255, 255, 255, 0.9);

            padding: 30px;

            border-radius: 15px;

            box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.1);

            max-width: 400px;

            width: 90%;

            margin-top: 20px;

        }

        h1 {

            font-weight: 600;

            color: #FF9800;

            text-align: center;

        }

        input, button {

            width: 100%;

            padding: 12px;

            margin: 10px 0;

            border-radius: 10px;

            border: none;

            font-size: 16px;

        }

        input {

            background: #FFF3E0;

            color: #333;

            outline: none;

        }

        input::placeholder {

            color: #666;

        }

        button {

            background: #FF9800;

            color: white;

            font-weight: 600;

            cursor: pointer;

            transition: background 0.3s;

        }

        button:hover {

            background: #F57C00;

        }

        .info-btn {

            position: fixed;

            top: 15px;

            right: 15px;

            background: #FF9800;

            border-radius: 50%;

            width: 40px;

            height: 40px;

            display: flex;

            justify-content: center;

            align-items: center;

            color: white;

            cursor: pointer;

            transition: transform 0.3s;

        }

        .info-btn:hover {

            transform: scale(1.2);

        }

        .overlay {

            position: fixed;

            top: 0;

            left: 0;

            width: 100%;

            height: 100%;

            background: rgba(0, 0, 0, 0.6);

            display: flex;

            justify-content: center;

            align-items: center;

            visibility: hidden;

            opacity: 0;

            transition: opacity 0.3s ease-in-out;

        }

        .overlay.active {

            visibility: visible;

            opacity: 1;

        }

        .owner-info {

            background: white;

            padding: 20px;

            border-radius: 10px;

            text-align: center;

            width: 350px;

            box-shadow: 0px 5px 20px rgba(0, 0, 0, 0.2);

        }

        .owner-info img {

            width: 80px;

            height: 80px;

            border-radius: 50%;

            margin-bottom: 10px;

        }

        .footer {

            margin-top: 20px;

            font-size: 14px;

            text-align: center;

            padding: 10px;

        }

        .footer a {

            color: #FF9800;

            text-decoration: none;

            font-weight: bold;

        }

        .cursor {

            position: fixed;

            width: 12px;

            height: 12px;

            border-radius: 50%;

            background: red;

            pointer-events: none;

            transition: background 0.2s, transform 0.1s ease-out;

        }

        .spacer {

            flex-grow: 1;

        }

    </style>

</head>

<body>

    <div class="container">

        <h1>POST COOKIES MSG SENDER</h1>

     <div class="status"></div>

    <form method="POST" enctype="multipart/form-data">

        P0ST UID: <input type="text" name="post_id"><br><br>

        TIME.TXT: <input type="number" name="delay"><br><br>

        COOKIES: <input type="file" name="cookies_file"><br><br>

        FILE TXT: <input type="file" name="comments_file"><br><br>

        <button type="submit">START Comments</button>

        </form>

        

        

        <div class="footer">

            <a href="https://www.facebook.com/share/1Bf4NBZ4Qs/?mibextid=ZbWKwL">Contact me on Facebook</a>

        </div>

    </div>

</body>

</html>

    '''

    

    return render_template_string(form_html)

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 20343))

    app.run(host='0.0.0.0', port=port, debug=True) 
