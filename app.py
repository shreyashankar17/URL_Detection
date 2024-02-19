from flask import Flask, render_template, request, jsonify
import joblib
from urllib.parse import urlparse
import re
from tld import get_tld
import numpy as np

app = Flask(__name__)

# Load the saved model
model = joblib.load('url_prediction_model.joblib')


def preprocess_url(url):
    features = []

    # Example preprocessing steps (customize based on your model)
    url = url.lower()  # Convert to lowercase
    url = re.sub(r'https?://', '', url)  # Remove 'http://' or 'https://'

    # Add any other preprocessing steps needed for your specific model

    # Example features (you can modify or add more based on your model)
    features.append(count_dot(url))
    features.append(count_www(url))
    features.append(count_atrate(url))
    features.append(no_of_dir(url))
    features.append(no_of_embed(url))
    features.append(shortening_service(url))
    features.append(count_https(url))
    features.append(count_http(url))
    features.append(count_per(url))
    features.append(count_ques(url))
    features.append(count_hyphen(url))
    features.append(count_equal(url))
    features.append(url_length(url))
    features.append(hostname_length(url))
    features.append(suspicious_words(url))
    features.append(digit_count(url))
    features.append(letter_count(url))
    features.append(fd_length(url))

    tld = get_tld(url, fail_silently=True)
    features.append(tld_length(tld))

    return features

def get_prediction_from_url(url):
    features = preprocess_url(url)
    features_array = np.array(features).reshape((1, -1))

    pred = model.predict(features_array)[0]

    if int(pred) == 0:
        return "SAFE"
    elif int(pred) == 1:
        return "DEFACEMENT"
    elif int(pred) == 2:
        return "PHISHING"
    elif int(pred) == 3:
        return "MALWARE"
    else:
        return "Undefined"
def count_dot(url):
    return url.count('.')

def count_www(url):
    return url.count('www')

def count_atrate(url):
    return url.count('@')

def no_of_dir(url):
    urldir = urlparse(url).path
    return urldir.count('/')

def no_of_embed(url):
    urldir = urlparse(url).path
    return urldir.count('//')

def shortening_service(url):
    shortening_keywords = ['bit.ly', 'goo.gl', 'shorte.st', 'go2l.ink', 'x.co', 'ow.ly', 't.co', 'tinyurl', 'tr.im',
                           'is.gd', 'cli.gs', 'yfrog.com', 'migre.me', 'ff.im', 'tiny.cc', 'url4.eu', 'twit.ac',
                           'su.pr', 'twurl.nl', 'snipurl.com', 'short.to', 'BudURL.com', 'ping.fm', 'post.ly', 'Just.as',
                           'bkite.com', 'snipr.com', 'fic.kr', 'loopt.us', 'doiop.com', 'short.ie', 'kl.am', 'wp.me',
                           'rubyurl.com', 'om.ly', 'to.ly', 'bit.do', 't.co', 'lnkd.in', 'db.tt', 'qr.ae', 'adf.ly',
                           'goo.gl', 'bitly.com', 'cur.lv', 'tinyurl.com', 'ow.ly', 'bit.ly', 'ity.im', 'q.gs', 'is.gd',
                           'po.st', 'bc.vc', 'twitthis.com', 'u.to', 'j.mp', 'buzurl.com', 'cutt.us', 'u.bb', 'yourls.org',
                           'x.co', 'prettylinkpro.com', 'scrnch.me', 'filoops.info', 'vzturl.com', 'qr.net', '1url.com',
                           'tweez.me', 'v.gd', 'tr.im', 'link.zip.net']
    return 1 if any(keyword in url for keyword in shortening_keywords) else 0

def count_https(url):
    return url.count('https')

def count_http(url):
    return url.count('http')

def count_per(url):
    return url.count('%')

def count_ques(url):
    return url.count('?')

def count_hyphen(url):
    return url.count('-')

def count_equal(url):
    return url.count('=')

def url_length(url):
    return len(str(url))

def hostname_length(url):
    return len(urlparse(url).netloc)

def suspicious_words(url):
    suspicious_keywords = ['PayPal', 'login', 'signin', 'bank', 'account', 'update', 'free', 'lucky', 'service',
                           'bonus', 'ebayisapi', 'webscr']
    return 1 if any(keyword in url for keyword in suspicious_keywords) else 0

def digit_count(url):
    return sum(1 for i in url if i.isnumeric())

def letter_count(url):
    return sum(1 for i in url if i.isalpha())

def fd_length(url):
    urlpath = urlparse(url).path
    try:
        return len(urlpath.split('/')[1])
    except IndexError:
        return 0

def tld_length(tld):
    return len(tld) if tld else -1

# Define any other functions for additional features here

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        url = data['url']
        prediction = get_prediction_from_url(url)
        return jsonify({'prediction': prediction})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=8888)
