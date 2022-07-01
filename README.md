*IoT Casus | Hogeschool Zuyd*

# EmojiMirror
Bij StreetLab werken studenten en docenten van de opleidingen ICT en Engineering aan innovatieve techniekprojecten op het gebied van kunstmatige intelligentie, data visualisatie, data science en software development. 
Het doel van het project was om op een creatieve manier de interesse en engagement van winkelend publiek te bevorderen door middel van een IoT opstelling. De groep had als idee bedacht om een smart mirror te maken op basis van emotie detectie waarbij feedback gegeven wordt aan de hand van licht en GIFjes.


![Alt text](https://github.com/nomivl/EmojiMirror/blob/main/EmojiMirror/emojimirror_Mockup.png)

## Installatie:
1.	Maak een virtual environment
2.	Activeer de virtualenv
3.	open EmojiMirror map in de command prompt
4.	run: pip install -r requirements.txt
5.	open main.py
6.	Verander de juiste settings:
      -	Webcam = 0 (default) of Webcam = 1
      - Verander webcamVertical naar True als de webcam gedraaid staat voor betere resolutie (wanneer de monitor ook verticaal staat)
      - SerialPort voor de lichten (meestal “COM3”of “COM4”)
      - Lights = False veranderen naar Lights = True
      - Kies de detectionSpeed 
        (lage waarde = hoge fps, hoge waarde: late reactie emotiedetectie)
      - Kies de sizeInterval
        (lage waarde = lage fps, hoge waarde: late reactie bij verlichting)
      - Kies de juiste classes in de emotionTargetList
      - standbyMaxCount bepalen (Bij drukke omgeving is 50 of hoger aangeraden)
      - GIFMonitorWidth = - de breedte van het middelste scherm
      - WebcamMonitorWidth = + de breedte van het middelste scherm
7.  run: python main.py



