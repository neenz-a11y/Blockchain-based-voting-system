from flask import Flask, render_template, url_for, request, session, flash, redirect
from flask_mail import *
from email.mime.multipart import MIMEMultipart
import smtplib
import sqlite3
import pandas as pd
import numpy as np
import os
#import cv2
from PIL import Image
import shutil
import datetime
import time
from collections import Counter
import blockChain

if os.path.isfile("blockChainDatabase.json"):
    blockc=blockChain.blockchain()
else:
    blockc=blockChain.blockchain(gen=True)

with sqlite3.connect('users.db') as db:
    c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS nominee (id INTEGER PRIMARY KEY AUTOINCREMENT,member_name TEXT NOT NULL,party_name TEXT UNIQUE NOT NULL,symbol_name TEXT NOT NULL);')
c.execute('CREATE TABLE IF NOT EXISTS voters (id INTEGER PRIMARY KEY AUTOINCREMENT,first_name TEXT NOT NULL,last_name TEXT UNIQUE NOT NULL,aadhar_id TEXT NOT NULL,voter_id TEXT NOT NULL,email TEXT NULL,pno TEXT NOT NULL,state Text NOT NULL,d_name Text NOT NULL,verified Text NOT NULL);')
db.commit()
db.close()

app=Flask(__name__)
app.config['SECRET_KEY']='ajsihh98rw3fyes8o3e9ey3w5dc'


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/admin', methods=['POST','GET'])
def admin():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        
        # First check admin credentials
        if email == 'admin@gmail.com' and password == 'admin123':
            session['IsAdmin'] = True
            session['User'] = 'admin'
            flash('Admin login successful', 'success')
            return redirect(url_for('adminp'))
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute('''SELECT * FROM voters 
                      WHERE email = ? AND aadhar_id = ?''', 
                     (email, password))
            voter = c.fetchone()
            print(voter)
            if voter:
                block=blockc.check_blockchain()
                #block.pop(0)
                #print(block)
                votername=[]
                for i in range(1,len(block)):
                    votername.append(block[i]["voterid"])
                    print(votername)
                    print(voter[3])
                if voter[3] in  votername:
                    flash('You have already voted!', 'warning')
                    print("Already voted")
                    return render_template('index.html')
                
                session['User'] = {
                    'id': voter[0],
                    'voter_id': voter[4],
                    'email': voter[5],
                    'verified': voter[9]
                }
                session['select_aadhar']= voter[3]
                #flash('Voter login successful', 'success')
                return redirect(url_for('select_candidate'))
            else:
                flash('Invalid credentials!', 'danger')
                
        except sqlite3.Error as e:
            flash('Database error occurred', 'danger')
            print(f"Database error: {e}")
            
        finally:
            conn.close()
            
        return redirect(url_for('home'))
    
    # Clear existing sessions on GET request
    session.pop('IsAdmin', None)
    session.pop('User', None)
    return render_template('adminlogin.html', admin=False)

@app.route('/adminp', methods=['POST','GET'])
def adminp():
    return render_template('adminhome.html', admin=session['IsAdmin'])
    

@app.route('/add_nominee', methods=['POST','GET'])
def add_nominee():
    if request.method=='POST':
        member=request.form['member_name']
        party=request.form['party_name']
        logo=request.form['test']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM nominee WHERE member_name=?', (member,))
        m=c.fetchone()
        c.execute('SELECT * FROM nominee WHERE party_name=?', (party,))
        p=c.fetchone()
        c.execute('SELECT * FROM nominee WHERE symbol_name=?', (logo,))
        l=c.fetchone()
        if m:
           flash(r'The member already exists', 'info')
        elif p:
           flash(r'The party already exists', 'info')
        elif l:
           flash(r'The logo already exists', 'info')
        else:
            c.execute('INSERT INTO nominee (member_name, party_name, symbol_name ) VALUES (?, ?, ?)', (member,party, logo))
            conn.commit()
            flash(r"Successfully registered a new nominee", 'primary')
    return render_template('nominee.html', admin=session['IsAdmin'])

@app.route('/registration', methods=['POST','GET'])
def registration():
    if request.method=='POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        state = request.form['state']

        middle_name = request.form['middle_name']
        aadhar_id = request.form['aadhar_id']
        voter_id = request.form['voter_id']
        pno = request.form['pno']
        age = int(request.form['age'])
        email = request.form['email']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT aadhar_id FROM voters')
        all_aadhar_ids = c.fetchall()
        c.execute('SELECT voter_id FROM voters')
        all_voter_ids = c.fetchall()
        
        if age >= 18:
            if (aadhar_id in all_aadhar_ids) or (voter_id in all_voter_ids):
                flash(r'Already Registered as a Voter')
            else:
                c.execute('INSERT INTO voters (first_name, last_name, aadhar_id, voter_id, email,pno,state,d_name, verified ) VALUES (?, ?, ?, ?, ?, ?, ?,?,?)', (first_name,  last_name, aadhar_id, voter_id, email, pno, state, "Thiruvananthapuram", 'no'))
                conn.commit()
    
                session['aadhar']=aadhar_id
                session['status']='no'
                session['email']=email
                return redirect(url_for('adminp'))
        else:
            flash("if age less than 18 then not eligible for voting","info")
    return render_template('voter_reg.html')


# @app.route('/capture_images', methods=['POST','GET'])
# def capture_images():
#     if request.method=='POST':
#         cam=cv2.VideoCapture(0, cv2.CAP_DSHOW)
#         sampleNum = 0
#         path_to_store=os.path.join(os.getcwd(),"all_images\\"+session['aadhar'])
#         try:
#             shutil.rmtree(path_to_store)
#         except:
#             pass
#         os.makedirs(path_to_store, exist_ok=True)
#         while (True):
#             ret, img = cam.read()
#             try:
#                 gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#             except:
#                 continue
#             faces = cascade.detectMultiScale(gray, 1.3, 5)
#             for (x, y, w, h) in faces:
#                 cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
#                 # incrementing sample number
#                 sampleNum = sampleNum + 1
#                 # saving the captured face in the dataset folder TrainingImage
#                 cv2.imwrite(path_to_store +r'\\'+ str(sampleNum) + ".jpg", gray[y:y + h, x:x + w])
#                 # display the frame
#             else:
#                 cv2.imshow('frame', img)
#                 cv2.setWindowProperty('frame', cv2.WND_PROP_TOPMOST, 1)
#             # wait for 100 miliseconds
#             if cv2.waitKey(100) & 0xFF == ord('q'):
#                 break
#             # break if the sample number is morethan 100
#             elif sampleNum >= 200:
#                 break
#         cam.release()
#         cv2.destroyAllWindows()
#         flash("Registration is successfull","success")
#         return redirect(url_for('train'))
#     return render_template('capture.html')

# from sklearn.preprocessing import LabelEncoder
# import pickle
# le = LabelEncoder()

# def getImagesAndLabels(path):
#     folderPaths = [os.path.join(path, f) for f in os.listdir(path)]
#     faces = []
#     Ids = []
#     global le
#     for folder in folderPaths:
#         imagePaths = [os.path.join(folder, f) for f in os.listdir(folder)]
#         aadhar_id = folder.split("\\")[1]
#         for imagePath in imagePaths:
#             # loading the image and converting it to gray scale
#             pilImage = Image.open(imagePath).convert('L')
#             # Now we are converting the PIL image into numpy array
#             imageNp = np.array(pilImage, 'uint8')
#             # extract the face from the training image sample
#             faces.append(imageNp)
#             Ids.append(aadhar_id)
#             # Ids.append(int(aadhar_id))
#     Ids_new=le.fit_transform(Ids).tolist()
#     output = open('encoder.pkl', 'wb')
#     pickle.dump(le, output)
#     output.close()
#     return faces, Ids_new

# @app.route('/train', methods=['POST','GET'])
# def train():
#     if request.method=='POST':
#         recognizer = cv2.face.LBPHFaceRecognizer_create()
#         faces, Id = getImagesAndLabels(r"all_images")
#         print(Id)
#         print(len(Id))
#         recognizer.train(faces, np.array(Id))
#         recognizer.save("Trained.yml")
#         flash(r"Model Trained Successfully", 'Primary')
#         return redirect(url_for('home'))
#     return render_template('train.html')


# @app.route('/voting', methods=['POST','GET'])
# def voting():
#     if request.method=='POST':
#         pkl_file = open('encoder.pkl', 'rb')
#         my_le = pickle.load(pkl_file)
#         pkl_file.close()
#         recognizer = cv2.face.LBPHFaceRecognizer_create() # cv2.createLBPHFaceRecognizer()
#         recognizer.read(r"static\Trained.yml")
#         cam=cv2.VideoCapture(0, cv2.CAP_DSHOW)
#         font = cv2.FONT_HERSHEY_SIMPLEX
#         flag = 0
#         detected_persons=[]
#         while True:
#             ret, im = cam.read()
#             flag += 1
#             if flag==200:
#                 flash(r"Unable to detect person. Contact help desk for manual voting", "info")
#                 cv2.destroyAllWindows()
#                 return render_template('voting.html')
#             gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
#             faces = cascade.detectMultiScale(gray, 1.2, 5)
#             print(faces)
#             for (x, y, w, h) in faces:
#                 cv2.rectangle(im, (x, y), (x + w, y + h), (225, 0, 0), 2)
#                 Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
#                 if (conf > 40):
#                     det_aadhar = my_le.inverse_transform([Id])[0]
#                     detected_persons.append(det_aadhar)
#                     cv2.putText(im, f"Aadhar: {det_aadhar}", (x, y + h), font, 1, (255, 255, 255), 2)
#                 else:
#                     cv2.putText(im, "Unknown", (x, y + h), font, 1, (255, 255, 255), 2)
#             cv2.imshow('im', im)
#             try:
#                 cv2.setWindowProperty('im', cv2.WND_PROP_TOPMOST, 1)
#             except:
#                 pass
#             if len(detected_persons)>10:
#                 session['select_aadhar']=det_aadhar
#                 cv2.destroyAllWindows()
#                 return redirect(url_for('select_candidate'))

#             if (cv2.waitKey(1) == (ord('q')) ):
#                 try:
#                     session['select_aadhar']=det_aadhar
#                 except:
#                     cv2.destroyAllWindows()
#                     return redirect(url_for('home'))
#                 cv2.destroyAllWindows()
#                 return redirect(url_for('select_candidate'))
#     return render_template('voting.html')

@app.route('/select_candidate', methods=['POST','GET'])
def select_candidate():
    #extract all nominees
    aadhar = session['aadhar']
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM nominee')
    all_nom = c.fetchall()

    if request.method == 'POST':
            vote = request.form['test']
            vote = vote[1:]
            vote = vote[:-1]
            print(vote)
            v=vote.split(',')
            blockc.create_block(voterid=str(session['select_aadhar']),party=str(v[2]))
            flash(r"Voted Successfully", 'Primary')
            return redirect(url_for('home'))
    return render_template('select_candidate.html', noms=sorted(all_nom))

@app.route('/voting_res')
def voting_res():
    # votes = pd.read_sql_query('select * from vote', mydb)
    # counts = pd.DataFrame(votes['vote'].value_counts())
    # counts.reset_index(inplace=True)
    # all_imgs=['1.png','2.png','3.jpg','4.png','5.png','6.png']
    # all_freqs=[counts[counts['index']==i].iloc[0,1] if i in counts['index'].values else 0 for i in all_imgs]
    # df_nom=pd.read_sql_query('select * from nominee', mydb)
    # all_nom=df_nom['symbol_name'].values
    block=blockc.show_blockchain()
    #block.pop(0)
    print(block)
    partname=[]
    for i in range(1,len(block)):
        partname.append(block[i]["party"])
   
    frequency = Counter(partname)

    # Separate elements and their frequencies into two lists
    elements = list(frequency.keys())
    frequencies = list(frequency.values())
    return render_template('voting_res.html',lll=zip(elements,frequencies),total_votes=len(block)-1)

if __name__=='__main__':
    app.run(debug=True)

