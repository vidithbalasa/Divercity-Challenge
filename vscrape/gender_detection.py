import cv2, os

genderProto='pretrained_models/gender_deploy.prototxt'
# give full path to genderModel (openCV being buggy w/o this for sum reason)
genderModel = os.path.abspath('pretrained_models/gender_net.caffemodel')


faceProto='pretrained_models/opencv_face_detector.pbtxt'
faceModel='pretrained_models/opencv_face_detector_uint8.pb'

MODEL_MEAN_VALUES=(78.4263377603, 87.7689143744, 114.895847746)

genderList=['Male','Female']
genderNet=cv2.dnn.readNet(genderModel,genderProto)
faceNet=cv2.dnn.readNet(faceModel,faceProto)

# generic code
def detect_image_gender(file: str) -> str:
    video = cv2.VideoCapture(file)
    padding = 20
    _, frame = video.read()
    [face_box] = get_face_boxes(faceNet,frame)
    # only one face box in linekdin profile pics
    face = frame[max(0,face_box[1]-padding):
                min(face_box[3]+padding,frame.shape[0]-1),max(0,face_box[0]-padding)
                :min(face_box[2]+padding, frame.shape[1]-1)]

    blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
    genderNet.setInput(blob)
    genderPreds = genderNet.forward()
    gender = genderList[genderPreds[0].argmax()]
    print(f'Gender: {gender}')
    return gender
    
def get_face_boxes(net, frame, conf_threshold:float=0.7) -> None:
    frame_height, frame_width, *_ = frame.shape
    # turn frame (image) into a blod to pass into the model
    blob=cv2.dnn.blobFromImage(frame, 1.0, (400,400), [104, 117, 123], True, False)

    # pass the blob into the model
    net.setInput(blob)
    detections=net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0,0,i,2]
        if confidence > conf_threshold:
            x1 = int(detections[0,0,i,3]* frame_width)
            y1 = int(detections[0,0,i,4]* frame_height)
            x2 = int(detections[0,0,i,5]* frame_width)
            y2 = int(detections[0,0,i,6]* frame_height)
            return [[x1, y1, x2, y2]]