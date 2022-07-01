
from imp import reload
from turtle import width
from tensorflow.keras.preprocessing.image import img_to_array
from deepface import DeepFace
import cvzone
import cv2
from tensorflow.keras.models import load_model
import numpy as np
from models import FacialExpressionModel
import serial
import time


###################################################### SETTINGS ########################################################
# 0 = default camera
webcam = 1
# wel of niet de webcam draaien:
webcamVertical = False
#keuze uit groep 2 (model met probability frame), groep 5 (Python Deepface Library) of projectgroep 7:
group = 2
# keuze uit: standard, emoji of faceemoji
GIFType = "faceemoji"

#Lichten gebruiken
lights = False

#COM3 port voor de lichten kan verschillen 
serialPort = 'COM3'
#kiezen om de hoeveel frames emotiedetectie wordt uitgevoerd.
# tussen 1 en 10 
detectionSpeed = 5

#Voor de lichten wordt de meest detecteerde emotie weergeven binnen een bepaalde interval. Wanneer dit op False staat wordt de laatst detecteerde emotie gebruikt.
useMostFreqEmotion = True
# sizeInterval bepaald over hoeveel detecties de meest gedetecteerde emotie wordt achterhaald, 
# of bij useMostFreqEmotion = False wordt de laatste emotie binnen het interval gebruikt. 

# Let op de detection speed kan dit proces beinvloeden.
# (sizeInterval * detectionspeed bepaald hoe snel light() wordt aangeroepen).
sizeInterval = 3

# Gebruikte emoties
# Keuze uit: "angry" ,"disgust","fear", "happy", "sad", "surprise","neutral"
emotionTargetList = ["neutral" ,"happy", "angry", "sad"]


#
keepLastEmotion = False
#De hoeveelheid frames dat geen gezicht te vinden is en standaard gif en lichtkleur moet weergegeven.
standbyMaxCount = 50


# Feedback van GIFs en LEDS is chaotisch bij meerdere gezichten.  
# (DetectionSpeed moet op 1 bij meerdere gezichten)
maxFaces = 1

# start de webcam/gif window zoveel pixels naar links (-) of rechts (+) vanaf het hoofdscherm 
GIFMonitorWidth = -1920
WebcamMonitorWidth = +1200

#de hoogte zal niet veel uitmaken aangezien "cv2.WINDOW_FULLSCREEN" dit overschrijdt 
GIFMonitorHeight = 1200
WebcamMonitorHeight = 1920

#gebruikte font
font = cv2.FONT_HERSHEY_SIMPLEX





### #Voor definieren  ########################################################################################################################
#Bij houden wanneer lichten of GIFS bij een nieuwe emotie veranderd moeten worden
newEmotion = False
emotion = ""
# wordt alleen gebruikt bij > Light = True
lightEmotionStatus = ""

# Houdt de frame count van GIFs bij. wanneer de GIF is afgelopen (wanneer gifFrameCount >= maxFrames) wordt de GIF opnieuw geladen.
gifFrameCount = 0

# Houdt frameCount bij.
frameCount = 0

# Houdt aantal detecties bij. wordt alleen gebruikt bij > Light = True
detectCount = 0

# Houdt gevonden detecties binnen een bepaalde interval bij. Wordt alleen gebruikt bij > Light = True
detections = []

standby = False

#Houdt bij wanneer het systeem om de standaard GIF's en lichten moeten: if standby > standbyMaxCount
standbyCount = 0




# Lichten
# geef string naam emotie door aan arduino
def light(emotion):
    serialcomm = serial.Serial(serialPort, 9600)
    time.sleep(0.25)
    for x in range(0,3):
        serialcomm.write(emotion.encode())
        time.sleep(0.25)

#show detection results
def feedback(frame,emotion,x,y,w,h):
        # bounding box om gezicht.
        cvzone.cornerRect(frame, (x,y, (w), (h)),15,3  ,rt=0)
        #toont gevonden emotie onder bounding box.
        cv2.putText(frame, emotion, (x, y+h+30), font, .75, (47, 47, 255), 2)
        # toont hoeveelste detecteerde gezicht boven de bounding box.
        if maxFaces != 1:
                cv2.putText(frame, str(faceCount), (x, y-10), font, .85,  (0, 255, 0), 2, cv2.LINE_AA)  

# achterhaald meest detecteerde emoties in een lijst (grootte van de lijst hangt af van de sizeInterval)        
def most_frequent(List):
    return max(set(List), key = List.count)

# achterhaald of een gedetecteerde emotie nieuw is of niet.
def emotionStatus(prev_Emotion, cur_emotion):
        if cur_emotion == prev_Emotion:           
                return False, cur_emotion
                                
        else:
                return True, cur_emotion

#Bij angry, happy, en sad wordt een afbeelding over het gezicht geplaatst.
# de transparante png afbeeldingen moeten in de map "images" staan met de naam van de emotie.
def filter(emotion, frame,face):
        
        #als de gevonden emotie een filter heeft:
        if emotion == "angry" or emotion == "happy" or emotion == "sad":
                overlay = cv2.imread('images/'+emotion+'.png' , cv2.IMREAD_UNCHANGED)
                #face[2] = width, face[3] = height
                overlayResize = cv2.resize(overlay, (face[2],face[3]))
                
                # als emotie een filter heeft die boven het gezicht geplaatst moet worden:
                if  emotion == "angry" or emotion == "happy":
                         # y - 30% van de hoogte van het gezicht 
                        filterHeight = int(face[1]-face[3]*.3)
                        #alleen filter afbeelden als die niet buiten de frame valt (om een foutmelding te voorkomen):
                        if filterHeight > 0: 
                                frame = cvzone.overlayPNG(frame, overlayResize, [face[0],filterHeight])
                        else:
                                return frame
                # anders wordt de filter op de coordinaten van het gezicht geplaatst:
                else:
                        frame = cvzone.overlayPNG(frame, overlayResize, [face[0],face[1]])
        return frame

def reloadGIF(emotion):
        gifFrameCount = 0
        GIF = cv2.VideoCapture("GIF/"+emotion+"/"+GIFType+".gif")
        maxFrames = int(GIF.get(cv2.CAP_PROP_FRAME_COUNT))
        return GIF, gifFrameCount, maxFrames
#GEZICHTSDETECTIE
face_detection = cv2.CascadeClassifier('haarcascade_files/haarcascade_frontalface_default.xml')


#EMOTIE DETECTIE MODELLEN
# group 2 heeft een detectie window met probablities, groep 7 en 5 hebben die niet. 
# voor groep 5 wordt hier geen model ingeladen maar de python deepface library gebruikt > DeepFace.analyze()
model_group2 = load_model('models/_mini_XCEPTION.106-0.65.hdf5', compile=False)
model_group7 = FacialExpressionModel('models/model.json', 'models/model_weights.oversampled.hdf5')
predictions_group7 = []
# Wordt alleen voor de predicties bij groep 2 gebruikt
EMOTIONS_WINDOW = ["angry" ,"disgust","fear", "happy", "sad", "surprise","neutral"]



# GIF WINDOW
cv2.namedWindow("GIF", cv2.WND_PROP_FULLSCREEN)
#verplaatst window naar gekozen punt met GIFMonitorWidth. de hoogte (GIFMonitorHeight) zal niet veel uitmaken aangezien "cv2.WINDOW_FULLSCREEN" dit zelf aanpast.
cv2.moveWindow("GIF", GIFMonitorWidth, GIFMonitorHeight)
cv2.setWindowProperty("GIF", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
GIF = cv2.VideoCapture("GIF/"+GIFType+".gif")

# aantal frames in eerste ingeladen GIF
maxFrames = int(GIF.get(cv2.CAP_PROP_FRAME_COUNT))



# WEBCAM
cv2.namedWindow("Webcam", cv2.WND_PROP_FULLSCREEN)
#verplaatst window naar gekozen punt met WebcamMonitorWidth. de hoogte (WebcamMonitorHeight) zal niet veel uitmaken aangezien "cv2.WINDOW_FULLSCREEN" dit zelf aanpast.
cv2.moveWindow("Webcam", +WebcamMonitorWidth, WebcamMonitorHeight)
# Set window full Screen.
cv2.setWindowProperty("Webcam", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

#webcam.
# bij sommige laptops moet "cv2.CAP_DSHOW" verwijderd worden.
camera = cv2.VideoCapture(webcam,cv2.CAP_DSHOW)


                


while True:
    frame = camera.read()[1]
    if webcamVertical:
        frame =cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    _, GIFframe = GIF.read()
    # webcam spiegelen voor mirror effect.        
    frame = cv2.flip(frame,1)
    gifFrameCount += 1
    # per frame wordt gekeken of er een gezicht is gevonden. 
    face =  None
    faceCount = 0
    frameCount += 1
    
    #gezichtsdetectie
    grey_frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)
    faces = face_detection.detectMultiScale(grey_frame, 1.3, 5)
    

    newEmotion= False
    for (x, y, w, h) in faces:
        
          

        # wanneer meer gezichten in het frame zijn dan toegestaand, stopt de loop.
        # Feedback van GIFs en LEDS is chaotisch bij meerdere gezichten.
        if faceCount >= maxFaces:
                break
        else:
                # bewaar coordinaten van gezicht en hou het aantal bij:
                face = (x,y, (w), (h))
                if face:
                        faceCount += 1
                #om de zoveel frames wordt de emotie van het gevonden gezicht achterhaald.
                # er zijn hiervoor 3 verschillende emotie detectie modellen mogelijk (groep 7,2 en 5)
                if faceCount>0 and frameCount % detectionSpeed == 0:
                        standby = False
                        detectCount += 1
                        if group == 7:
                                faceResize = cv2.resize(grey_frame[y:y+h, x:x+w], (48, 48))
                                preds = model_group7.predict(faceResize[np.newaxis, :, :, np.newaxis])
                                predictions_group7.append(preds)
                                
                                newEmotion, emotion = emotionStatus(emotion,preds[0][0])
                        elif group == 5:
                                try:
                                        analyze = DeepFace.analyze(frame[y:y+h, x:x+w],actions=['emotion'])
                                        newEmotion, emotion = emotionStatus(emotion,analyze['dominant_emotion'])
                                except:
                                        print("Can't find an emotion")
                        elif group == 2:
                                canvas = np.zeros((250, 300, 3), dtype="uint8")
        
                                # Extract the ROI of the face from the grayscale image, resize it to a fixed 48x48 pixels, and then prepare
                                # the ROI for classification via the CNN
                                roi = cv2.resize(grey_frame[y:y+h, x:x+w], (48, 48))
                                roi = roi.astype("float") / 255.0
                                roi = img_to_array(roi)
                                roi = np.expand_dims(roi, axis=0)

                                preds = model_group2.predict(roi)[0]
                                emotion_probability = np.max(preds)
                        
                                newEmotion, emotion = emotionStatus(emotion,EMOTIONS_WINDOW[preds.argmax()])

                                for (i, (label, prob)) in enumerate(zip(EMOTIONS_WINDOW, preds)):
                                        if label in emotionTargetList:
                                                # construct the label text
                                                text = "{}: {:.2f}%".format(label, prob * 100)
                                                width = int(prob * 300)
                                                cv2.rectangle(canvas, (7, (i * 35) + 5),
                                                (width, (i * 35) + 35), (0, 0, 255), -1)
                                                cv2.putText(canvas, text, (10, (i * 35) + 23), font, 0.45,  (255, 255, 255), 1, cv2.LINE_AA)
                                        else:
                                                # construct the label text
                                                text = "{}: staat uit".format(label)
                                                cv2.putText(canvas, text, (10, (i * 35) + 23), font, 0.45,  (58, 58, 58), 1, cv2.LINE_AA)

                                
                                
                
                                cv2.imshow("Probabilities", canvas)
                                
                           
                # In de loop blijven
                # Bounding box om het gezicht.
                # Toon detectie info wanneer meerdere gezichtdetecties mogelijk zijn:
                if face and maxFaces != 1:
                        #toont detectie info
                        feedback(frame,emotion,x,y,w,h)
                        # plaats afbeelding over het gezicht.
                        frame = filter(emotion,frame,face)
                        
    if emotion not in emotionTargetList and emotion != "":
        emotion = "Neutral"    
    # Buiten de loop
    # Toon detectie info wanneer maar 1 gezicht gedetecteerd kan worden:
    if face and maxFaces == 1:
        #toont detectie info
        feedback(frame,emotion,x,y,w,h)
        # plaats afbeelding over het gezicht.
        frame = filter(emotion,frame,face) 
    #Bij gebruik van  lichten, wordt de meest detecteerde emotie weergeven binnen een bepaalde interval.
    # sizeInterval bepaald over hoeveel detecties de meest gedetecteerde emotie wordt achterhaald.
    if lights and maxFaces == 1 and face:
        if detectCount > sizeInterval:
                
                detectCount = 0
                
                newLightStatus = False
                if useMostFreqEmotion:
                        newLightStatus, lightEmotionStatus = emotionStatus(lightEmotionStatus,most_frequent(detections))
                       
                else:
                        
                        newLightStatus, lightEmotionStatus = emotionStatus(lightEmotionStatus,detections[-1])
                        
                if newLightStatus:
                        light(lightEmotionStatus)
                        #print(lightEmotionStatus)
                detections = []
                
                        
                
        else:
                detections.append(emotion)
        #toont de lichtstatus links boven op het scherm.
        cv2.putText(frame,"LIGHT: "+lightEmotionStatus, (50,50), font, .85,  (255, 255, 0), 2, cv2.LINE_AA)        
    if not keepLastEmotion:            
        #wanneer er 10 frames achter elkaar geen gezicht is gevonden dan wordt de emotie op neutraal gezet
        if faces==() and standbyCount > standbyMaxCount and not standby:
                print("STANDBY")
                standby = True
                emotion= ""
                GIF, gifFrameCount, maxFrames = reloadGIF(emotion)
                if lights:
                        standby = True
                        light("NoFace")
                standbyCount = 0
                
        elif faces==() and not standby:
                standbyCount+=1                      
        
    # Bij elke nieuwe emotie wordt een nieuwe GIF aangeroepen en de framecount weer op 0 gezet:  
    if newEmotion:
        print("Nieuwe emotie detected: ", emotion)
        GIF, gifFrameCount, maxFrames = reloadGIF(emotion)
    # Wanneer GIF is afgespeeld en nog geen nieuwe emotie is gevonden wordt de GIF opnieuw ingeladen.    
    elif gifFrameCount >= maxFrames:
        GIF, gifFrameCount, maxFrames = reloadGIF(emotion)
        

    
    cv2.imshow("GIF", GIFframe)    
    if webcam == 1:
        cv2.imshow('Webcam', frame)
    cv2.imshow('Copy Webcam', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        #serialcomm.close()
        break

camera.release()
cv2.destroyAllWindows()


