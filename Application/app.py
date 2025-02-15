import pandas as pd
from flask import Flask, render_template, request, url_for, jsonify
import joblib
from ChatBot import ChatBotManager
import chd
import ecg_mi
import stroke
import os
import time
import pickle


api_key = "sk-2LsuYpxzZFo3Yma9mszrT3BlbkFJsdnyurgbArO8i6LZbZU5123456"[:-6]
os.environ['OPENAI_API_KEY'] = api_key

app = Flask(__name__)
chatbot = ChatBotManager()
app.config['UPLOAD_FOLDER'] = "ecg_mi/images"


try:
    with open('chats.pkl', 'rb') as file:
        chats= pickle.load(file)
except:
    chats =[]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/cities", methods=["GET"])
def get_cities():
    doctor_data = pd.read_excel('doctors.xlsx')
    cities = doctor_data.city

    return list(cities.unique())

@app.route("/chat_api", methods=['GET'])
def chat():
    try:
        question = request.form["question"]
        answer = chatbot.generate_answer(question)
        return {"answer": answer}
    except Exception as e:
        return {"error" :str(e)}


@app.route("/stroke", methods=["POST","GET"])
def stroke_prediction():
    if request.method == "POST":
        data = {
        "age": int(request.form.get('age')),
        "hypertension": int(request.form.get('hypertension')),
        "heart_disease": int(request.form.get('heart_disease')),
        "avg_glucose_level": int(request.form.get('avg_glucose_level')),
        "height": int(request.form.get('height')),
        "weight": int(request.form.get('weight')),
        "gender": int(request.form.get('gender')),
        "ever_married":int( request.form.get('ever_married')),
        "work_type":int( request.form.get('work_type')),
        "Residence_type": int(request.form.get('Residence_type')),
        "smoking_status": int(request.form.get('smoking_status'))
        }
        pipeline = joblib.load("stroke/pipeline.joblib")
        model = joblib.load("stroke/rf_under_Stroke_model.joblib")
        prediction = stroke.perform_prediction(data, pipeline, model)
        doctors = get_doctors()
        return render_template("stroke.html", 
                               result = prediction['prediction'], message=prediction['Message'],doctors=doctors)
    else:
        return render_template("stroke.html", prediction="0")


@app.route("/chd", methods=["POST","GET"])
def chd_prediction():
    if request.method == "POST":
        data = {
        "age": int(request.form.get('age')),
        "currentSmoker": int(request.form.get('currentSmoker')),
        "cigsPerDay": int(request.form.get('cigsPerDay')),
        "BPMeds": int(request.form.get('BPMeds')),
        "prevalentStroke": int(request.form.get('prevalentStroke')),
        "prevalentHyp": int(request.form.get('prevalentHyp')),
        "diabetes":int( request.form.get('diabetes')),
        "totChol":int( request.form.get('totChol')),
        "sysBP": int(request.form.get('sysBP')),
        "diaBP": int(request.form.get('diaBP')),
        "height": int(request.form.get('height')),
        "weight": int(request.form.get('weight')),
        "heartRate": int(request.form.get('heartRate')),
        "glucose": int(request.form.get('glucose')),
        "gender": int(request.form.get('gender'))
        }
        pipeline = joblib.load("chd/pipeline.joblib")
        model = joblib.load("chd/rf_CHD_under_model.joblib")

        prediction = chd.perform_prediction(data, pipeline, model)
        doctors = get_doctors()
        return render_template("chd.html",
                               result = prediction['prediction'], message=prediction['Message'],doctors=doctors)
    else:
        return render_template("chd.html", prediction="0")
    
@app.route("/ecg_mi", methods=["POST","GET"])
def ecg_mi_prediction():
    
    if request.method == "POST":
        data = {
            "Age":int(request.form.get("Age")),
            "CK-MB":int(request.form.get("CK-MB")),
            "Troponin":float(request.form.get("Troponin"))}
        file = request.files['image']
        if file.filename == '':
            return 'No selected file', 400
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            print("file_path")
        file.save(file_path)
        pipeline = joblib.load("ecg_mi/mi_pipeline.joblib")
        model = joblib.load("ecg_mi/mi_model.joblib")
        ecg_model = joblib.load('ecg_mi/best_rf_model_ecg_images.pkl')
        
        prediction = ecg_mi.mi_ecg_prediction(data, pipeline, model, file_path, ecg_model)
        doctors = get_doctors()
        print(prediction)
        return render_template("ecg.html",
                               result = prediction['prediction'], message=prediction['Message'],doctors=doctors)
    else:
        return render_template("ecg.html", prediction="0")
    
@app.route("/chat", methods=["POST","GET"])
def chat_page():
    if request.method == "POST":
        try:
            
            question = request.form["question"]
            print(question)
            answer = chatbot.generate_answer(question)
            chats.append({"question":question, "answer":answer})
            save_questions(chats)
            return render_template("chat.html", chats=chats)
        except Exception as e:
            return {"error" :str(e)}
    else:
        return render_template("chat.html", chats=chats)
    

    
@app.route("/stroke_analysis")
def stroke_analysis():
    return render_template("stroke_analysis.html")

@app.route("/chd_analysis")
def chd_anlaysis():
    return render_template("chd_analysis.html")

@app.route("/about")
def about():
    return render_template("about.html")

def get_doctors(city="المنوفية"):
    doctor_data = pd.read_excel('doctors.xlsx')
    custom_data = doctor_data[doctor_data.city == city]
    data_list = []
    for i in range(len(custom_data)):
        row_data = custom_data.iloc[i]
        dict_data = {"name": str(row_data[0]), "image": row_data.image,
                        "location": row_data.location, "price": row_data.price}
        data_list.append(dict_data)
    return data_list

def save_questions(list):
    with open('chats.pkl', 'wb') as file:
        pickle.dump(list, file)



if __name__ == "__main__":
    app.run(debug=True)






