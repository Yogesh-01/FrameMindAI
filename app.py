from datetime import datetime
import time
from flask import Flask,jsonify, flash, redirect,render_template,request, url_for
from sqlalchemy import create_engine
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from dotenv import load_dotenv
from flask_cors import CORS  # Import CORS
app=Flask(__name__)
CORS(app)

# app.secret_key = 'Secret_Key'

# urls = {
#     'key': '1234',
#     'password': 'password'
# }

API_KEY = "7f6d5cc4da8f455f85c47d6c60dc6fac"  # Replace with your actual API key
ENDPOINT = "https://genai-openai-lighteninglancers.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview"


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Max file size 16 MB
access_token = os.getenv('ACCESS_TOKEN')
transcript_text = []
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

@app.route('/')
def landing():
    return render_template('index.html')

with app.app_context():
    db.create_all()
 
# Allowed video file extensions
ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'avi', 'mov', 'flv'}
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
 
    def __init__(self, filename, path, size):
        self.filename = filename
        self.path = path
        self.size = size
 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/home',methods=['GET'])
def home_page():

    return render_template('home.html')

@app.route('/accessToken',methods=['GET'])
def getAccess():
    global access_token
    if(request.method=='GET'):
        url = "https://api.videoindexer.ai/Auth/trial/Accounts?generateAccessTokens=true&allowEdit=true"
        headers = {
                "Ocp-Apim-Subscription-Key": "e0e1beac58e349b49d50bd0e43bf3cd6"
            }
        response = requests.get(url, headers=headers)
        print(response.json())
        access_token = response.json()[0]['accessToken']
        return jsonify(response.json())
    else:
        return "no get"

@app.route('/submit-url',methods=['GET','POST'])
# @login_required
# def home_page():
#     if(request.method=='POST'):
#         print(request)
#         # url=request.args.get('urml')

#         data=request.get_json()
#         # url=request.form['url']
#         print(data)

#     return render_template('home.html')
def upload_file():
    # Check if the post request has the file part
    if(request.method=='POST'):
        url = request.form.get('url')
        # if 'file' not in request.files:
        #     return jsonify({'message': 'No file part'}), 400
    
        # file = request.files['file']
    
        # If no file is selected
        # if file.filename == '':
        #     return jsonify({'message': 'No selected file'}), 400
    
        # Check if the file is allowed
        
        print(access_token)
        upload_url = 'https://api.videoindexer.ai/trial/Accounts/c7ae81e6-9046-49b0-8524-cc8a56ed622a/Videos'
        params = {
            'name': 'Video123',
            'privacy': 'Private',
            'videoUrl': url,
            'isSearchable': 'true',
            'indexingPreset': 'Default',
            'streamingPreset': 'Default',
            'sendSuccessEmail': 'false',
            'useManagedIdentityToDownloadVideo': 'false',
            'preventDuplicates': 'false',
            'accessToken': access_token
        }
        headers = {
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': 'e0e1beac58e349b49d50bd0e43bf3cd6'
        }

        # Send the POST request
        response = requests.post(upload_url, params=params, headers=headers)
        print(response.json())

        # Return success response with video details
        # return jsonify({
        #     'message': 'File uploaded successfully',
        #     'filename': filename,
        #     'path': filepath,
        #     'size': file_size
        # }), 200
        res = response.json()
        # if "ErrorType" in res and res['ErrorType'] == 'VIDEO_ALREADY_IN_PROGRESS':
        #     video_id = res['Message'].split("video id: '")[1].split("'")[0]
        # else : video_id = res['id']
        # while (1):
        #     url = 'https://api.videoindexer.ai/trial/Accounts/c7ae81e6-9046-49b0-8524-cc8a56ed622a/Videos/'+video_id+'/Index'
        #     params = {
        #         'accessToken': access_token
        #     }
        #     headers = {
        #         'Cache-Control': 'no-cache',
        #         'Ocp-Apim-Subscription-Key': 'e0e1beac58e349b49d50bd0e43bf3cd6'
        #     }
        #     response = requests.get(url, params=params, headers=headers)
        #     if response.json()['state'] == 'Processed':
        #         break   
        #     print(response.json())
        #     time.sleep(2)
                
        return redirect(url_for('about'))
    else:
        return render_template('home.html')
 
@app.route('/videosList',methods=['GET'])
def about():
    url = 'https://api.videoindexer.ai/trial/Accounts/c7ae81e6-9046-49b0-8524-cc8a56ed622a/Videos'
    params = {
        'pageSize': 100,
        'skip': 0,
        'accessToken': access_token
    }
    headers = {
        'Cache-Control': 'no-cache',
        'Ocp-Apim-Subscription-Key': 'e0e1beac58e349b49d50bd0e43bf3cd6'
    }
    response = requests.get(url, params=params, headers=headers)
    print(response.json())
    VideoList = response.json()['results']
    return render_template('videoList.html', videos=VideoList)

@app.route('/video/<video_id>', methods=['GET'])
def video_detail(video_id):
    global transcript_text
    
    print(video_id, "hello i this")
    url = "https://api.videoindexer.ai/trial/Accounts/c7ae81e6-9046-49b0-8524-cc8a56ed622a/Videos/"+video_id+"/Index"
    params = {
        'accessToken': access_token
    }
    headers = {
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': 'e0e1beac58e349b49d50bd0e43bf3cd6'
        }
    response = requests.get(url, params=params, headers=headers)
    print(url, response.json())
    transcript_text = response.json()['videos'][0]['insights']["transcript"]
  
    print(video_id, "hello i this 234")
    return render_template('videoDetail.html', id=video_id, transcipts = transcript_text, access_token=access_token)


def get_ai_response(user_input):
    print(transcript_text)
    payload = {
        "messages": [
            {"role": "system", "content": "You are an transcript assistant that helps people find information from transcript object also provides the timestamp of that information. You can take reference from transcript and internet. Answer in 40 words,transcript is as follows:".join(str(text["text"] for text in transcript_text)),},
            {"role": "user", "content": user_input},
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800,
    }
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the response code is not 200
        response_data = response.json()
        ai_message = response_data['choices'][0]['message']['content']
        return ai_message
    except requests.RequestException as e:
        print(f"Error: {e}")
        return "Sorry, I couldn't get a response from the AI."
    
@app.route("/get-ai-response", methods=["POST"])
def chat():
    # Check if the request has JSON content and a 'message' key
    if not request.is_json:
        return jsonify({"error": "Invalid request format. Expected JSON."}), 400

    data = request.get_json()
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # Get AI's response
    ai_response = get_ai_response(user_input)
    return jsonify({"response": ai_response})

if __name__=="__main__":
    app.run(debug=True)
