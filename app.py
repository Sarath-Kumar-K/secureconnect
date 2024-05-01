from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime
import pandas as pd
import joblib
import random

model = joblib.load('random_forest_model.pkl')
df = pd.read_csv('modified_dataset.csv')
X_train = df.drop('Label', axis=1) # You would typically drop the target variable from your dataset to get X_train
X_train_encoded = pd.get_dummies(X_train) # Encode categorical variables using one-hot encoding
app = Flask(__name__)

# Create a dictionary with variable names as keys and their values
data_dict = {
    "IP Address": "",
    "Geolocation": "India",
    "User Agent": "",
    "Session Duration": random.randint(7, 100),
    "Data Transfer Volume": random.randint(0, 100),
    "Packet Size": random.randint(100, 1000),
    "Status Code": 200,
    "Protocol": "",
    "Proxy Detected": 0
}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/test')
def test():
    user_agents = ['Blackhole', 'Cobalt Strike', 'Metasploit', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/99.0.1150.37 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0', 'Zeus']
    countries = ['Austria','Belgium','China','France','Germany','India','Indonesia','Italy','Japan','Netherlands','Pakistan','Philippines','Poland','Russia','Saudi Arabia','Spain','Sweden','Turkey','United Kingdom','Vietnam']
    protocols = ['HTTP','HTTPS','TCP','UDP','ICMP','SSH','POP3','SMTP','Telnet','IMAP']
    status_codes = [200,301,302,400,401,403, 404, 500,503]
    return render_template('cyber-form.html',countries=countries,user_agents=user_agents,status_codes=status_codes,protocols=protocols)

@app.route('/ipdata', methods=['POST'])
def ipdata():
    form_data = request.form.to_dict()
    return predict(form_data)

@app.route('/employee')
def employee():
    return predict(data_dic)

def get_users():
    with open('users.json', 'r') as file:
        users_data = json.load(file)
    return users_data['users']

def authenticate(username, password):
    users = get_users()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return True
    return False
@app.route('/login', methods=['POST'])
def login():
    # Get username and password from the form
    # ip details 
    data_dict["IP Address"] = request.remote_addr
    data_dict["User Agent"] = request.user_agent.string
    data_dict["Protocol"] = request.scheme
    proxy_headers = ['X-Forwarded-For', 'X-Real-IP', 'Via']
    if any(header in request.headers for header in proxy_headers):
        data_dict["Proxy Detected"] = 1
    else:
        data_dict["Proxy Detected"] = 0

    # print(ip_address)
    # print(user_agent)
    # print(timestamp)
    # print(status_code)
    # print(protocol)
    # print(is_proxy)
    # form data
    username = request.form['username']
    password = request.form['password']

    # Authenticate user (add your authentication logic here)

    # If authentication is successful, redirect to dashboard
    if authenticate(username, password):
        return redirect(url_for('dashboard'))

    # If authentication fails, redirect back to login page
    return redirect(url_for('index'))

def predict(form_data):

    # Extract form data from the parameter
    form_data = form_data
    # Extract and store the IP address separately
    ip_address = form_data.pop('IP Address', None)
    print("IP Address = ",ip_address)
    print("Form Data:",form_data)
    integer_columns = ['Session Duration', 'Data Transfer Volume', 'Packet Size', 'Status Code', 'Proxy Detected']
    for column in integer_columns:
        if column in form_data:
            form_data[column] = int(form_data[column])
    
    print("After conversion Form Data:",form_data)

    # Convert form data to a DataFrame
    form_df = pd.DataFrame([form_data])

    # Store the original column names before encoding
    original_columns = ['Geolocation', 'User Agent', 'Session Duration', 'Data Transfer Volume','Packet Size', 'Status Code', 'Protocol', 'Proxy Detected']

    #Encode categorical variables in the form data
    encoded_form = pd.get_dummies(form_df, columns=original_columns)

    # Align the columns with the training data columns
    encoded_form_aligned = encoded_form.reindex(columns=X_train_encoded.columns, fill_value=0)

    # Align the columns of encoded_form_aligned with X_train_encoded.columns
    # encoded_form_aligned = encoded_form_aligned.reindex(columns=X_train_encoded.columns, fill_value=0)

    # print("Training data columns:", X_train_encoded.columns)
    # print("Encoded form data columns:", encoded_form_aligned.columns)
    # print("Length of X_train_encoded.columns:", len(X_train_encoded.columns))
    # print("Length of encoded_form_aligned.columns:", len(encoded_form_aligned.columns))

    # encoded_form_aligned = encoded_form_aligned[X_train_encoded.columns]

    # Make prediction using the machine learning model
    prediction = model.predict(encoded_form_aligned)

    # Redirect based on prediction result
    if isinstance(prediction, list): # Check if prediction is a list
        prediction_value = prediction[0]
    else: # Get the first element if it's a list
        prediction_value = prediction  # Use prediction directly if it's not a list

    if prediction_value == 0:  # Benign connection
        print("Not Malicious")
        return redirect('https://sarath-kumar.vercel.app')
    elif prediction_value == 1:  # Malicious connection
        print("Malicious Ip Detected")
        return redirect(f'http://localhost:8000/login?ip={ip_address}')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
