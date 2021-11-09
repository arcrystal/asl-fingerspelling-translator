import cv2
import mediapipe as mp
import pandas as pd
import pickle
import os
import sys
import string

class Translator:

    def __init__(self):
        # Store current working directory
        self.HERE = os.getcwd() + "/"
        iX = [f"{i}_X" for i in range(21)]
        iY = [f"{i}_Y" for i in range(21)]
        iZ = [f"{i}_Z" for i in range(21)]
        # Save dataframe column names
        self.hand_id_cols = iX + iY + iZ
        # Columns of fingertips in coordinates df
        tipsX = [f"{i}_X" for i in range(4,21,4)]
        tipsY = [f"{i}_Y" for i in range(4,21,4)]
        self.tip_cols = tipsX + tipsY
        # Font for showing letter on video stream feeds
        self.FONT = cv2.FONT_HERSHEY_SIMPLEX
        # list of letters in Alphabet
        self.ALPHABET = list(string.ascii_uppercase)

    def translate_video_stream(self, draw_handpoints=False):
        """
        Create video capture object to start video stream.
        Synchronously translates video stream.
        """
        prediction = None
        predictions = [None]
        cap = cv2.VideoCapture(0)
        hands = mp.solutions.hands.Hands()
        mpDraw = mp.solutions.drawing_utils

        tips = [4, 8, 12, 16, 20] # index for fingertips from mediapipe hands

        test = pd.DataFrame(columns = self.hand_id_cols) #start with an empty dataframe for group of frames

        cwd = os.getcwd().split("/")[-1]
        if cwd=="src":
            rf = pickle.load(open(self.HERE + "models/rf.sav", 'rb'))
        elif cwd=="asl-fingerspelling-translator":
            rf = pickle.load(open(self.HERE + "src/models/rf.sav", 'rb'))
        else:
            raise FileNotFoundError

        prediction = None
        predictions = [None]

        rowX_order = []
        rowY_order = []
        prev1_rowX_order = []
        prev1_rowY_order = []
        prev2_rowX_order = []
        prev2_rowY_order = []
        prev3_rowX_order = []
        prev3_rowY_order = []
        prev4_rowX_order = []
        prev4_rowY_order = []
        prev5_rowX_order = []
        prev5_rowY_order = []
        # Start video stream
        while(cap.isOpened()):
            success, img = cap.read() # Capture the video frame by frame
            width = 0
            height = 0
            try:
                height, width, channels = img.shape
            except:
                break #Break the loop if there are no more frames

            #Image boundaries
            boundaries = {'maxX': width,  'minX': 0,
                          'maxY': height, 'minY': 0}
            
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #convert image to RGB
            results = hands.process(imgRGB) #process image to look for hands
            if results.multi_hand_landmarks: #if there is a hand identified
                for handLms in results.multi_hand_landmarks: #keep track of each x,y coordinate of points on hand

                    if draw_handpoints:
                        mpDraw.draw_landmarks(img, handLms, mp.solutions.hands.HAND_CONNECTIONS) #draw points on hand

                    X = []
                    Y = []
                    Z = []
                    for lm in handLms.landmark:
                        X.append(lm.x) 
                        Y.append(lm.y)
                        Z.append(lm.z)

                #note min and max values of hand coordinates
                maxY = max(Y)
                minY = min(Y)
                maxX = max(X)
                minX = min(X)
                maxZ = max(Z)
                minZ = min(Z)
                            
                #scale X and Y to be on 0,1 scale in between min and max finger values
                scaledX = [(x - minX) / (0.9*(maxX-minX)) for x in X]
                scaledY = [(y - minY) / (0.9*(maxY-minY)) for y in Y]
                scaledZ = [(z - minZ) / (0.9*(maxZ-minZ)) for z in Z]
                
                xRange = maxX - minX
                yRange = maxY - minY
                
                # normalize min and max values to be on same scale as width, height
                boundaries['maxY'] = int(maxY*height + 0.5*yRange)
                boundaries['minY'] = int(minY*height - 0.5*yRange)
                boundaries['minX'] = int(minX*width - 0.5*xRange)
                boundaries['maxX'] = int(maxX*width + 0.5*xRange)

                row = scaledX + scaledY + Z
                rowDf = pd.DataFrame([row], columns = self.hand_id_cols) #convert fingertip coordinates to df

                scaledX_tips = [scaledX[4],scaledX[8],scaledX[12],scaledX[16],scaledX[20]]
                scaledY_tips = [scaledY[4],scaledY[8],scaledY[12],scaledY[16],scaledY[20]]
                
                tips = scaledX_tips + scaledY_tips
                tipDf = pd.DataFrame([tips], columns = self.tip_cols)

                #Reset order of fingers in frame
                rowX_order = []
                rowY_order = []

                #add order of finger coordinates to x and y lists
                for index in pd.DataFrame(tipDf.mean()).sort_values(by=0).index:
                    if "X" in index:
                        rowX_order.append(index)
                    elif "Y" in index:
                        rowY_order.append(index)

                if len(test) > 1:
                    # Check if x and y order changed
                    if (rowX_order == prev1_rowX_order) and (rowY_order == prev1_rowY_order) or \
                       (rowX_order == prev2_rowX_order) and (rowY_order == prev2_rowY_order) or \
                       (rowX_order == prev3_rowX_order) and (rowY_order == prev3_rowY_order) or \
                       (rowX_order == prev4_rowX_order) and (rowY_order == prev4_rowY_order) or \
                       (rowX_order == prev5_rowX_order) and (rowY_order == prev5_rowY_order):
                        test = test.append(rowDf, ignore_index = True)
                    else:
                        # predict with random forest model
                        letter_probs = rf.predict_proba(test).sum(axis=0)
                        # Get letter from max probability
                        prediction = self.ALPHABET[letter_probs.argmax()]
                        """
                        If the prediction is different from the previous one,
                        we flag this as a potential mis-classification and 
                        continue to the next frame. Otherwise, we overlay that 
                        letter onto our output frame.
                        """
                        if prediction != predictions[-1]:
                            predictions.append(prediction)
                            continue
                        else:
                            predictions.append(prediction)
                        test = pd.DataFrame(columns = self.hand_id_cols)

                else:
                    test = test.append(rowDf, ignore_index = True)
                
                prev5_rowX_order = prev4_rowX_order.copy()
                prev5_rowY_order = prev4_rowY_order.copy()
                prev4_rowX_order = prev3_rowX_order.copy()
                prev4_rowY_order = prev3_rowY_order.copy()
                prev3_rowX_order = prev2_rowX_order.copy()
                prev3_rowY_order = prev2_rowY_order.copy()
                prev2_rowX_order = prev1_rowX_order.copy()
                prev2_rowY_order = prev1_rowY_order.copy()
                prev_rowX_order = rowX_order.copy()
                prev_rowY_order = rowY_order.copy()
                
                #set min and max values to video pixel limits if their values exceed those limits
                for key in boundaries:
                    boundaries[key] = max(0, boundaries[key])
                    if(key == 'maxX' or key == 'minX'):
                        boundaries[key] = min(width, boundaries[key])  
                    elif(key == 'maxY' or key == 'minY'):
                        boundaries[key] = min(height, boundaries[key])   
            else:
                test = pd.DataFrame(columns = self.hand_id_cols)

            # TODO: making website translation frame scale with with size (currently static)
            if prediction is not None:
                x = 250
                y = 650
                # img = cv2.flip(img, 1)
                cv2.putText(img, prediction, (x, y), self.FONT, 8, (0,0,255), 8)
            
            ret, jpeg = cv2.imencode('.jpg', img)
            res = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + res + b'\r\n\r\n')
        cap.release() # After the loop release the cap object
        cv2.destroyAllWindows() # Destroy all the windows
        cv2.waitKey(1)

