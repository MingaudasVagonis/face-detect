import cv2, numpy, threading
import face_recognition
from PIL import Image, ImageTk
from time import sleep

#converts the frame to tkinter image to be displayed
def process_frame(frame):
	width, height, layer = frame.shape
	scaled = cv2.resize(frame,(0,0), fx = 500.0/height, fy= 500.0/height)
	scaled = Image.fromarray(scaled[:,:,::-1])
	return ImageTk.PhotoImage(scaled)

class Player:

	def __init__(self, listener):
		self.listener=listener
		self.increment = 0

	def __del__(self):
		if self.video_capture:
			if self.video_capture.isOpened():
				self.video_capture.release()

	#must be called on another thread than ui, processes and plays provided frames at 24 frames a second
	def play_frames(self,input_frames):
		self.video_capture = None
		frames = map(process_frame,input_frames)
		for frame in frames:
			self.listener(0,frame)
			sleep(1.0/24)

	#plays video from the url, every frame listener is called with succ flag, frame itself, percentage elapsed and frame's number
	def play(self, url):
		try:
			self.video_capture = cv2.VideoCapture(url)
		except:
			print("Failed to open video")
		self.length = self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
		while True:
			ret, frame = self.video_capture.read()
			if not ret:
				self.listener(ret)
				break
			self.increment+=1
			self.listener(ret,frame, self.increment/self.length, self.increment)

class Detect:

	def __init__(self):
		self.face_data = {"locations":[],"encodings":[]}
		self.player = Player(self.handle_frame)
		self.frames = []

	def __del__(self):
		del self.player

	#must be called on a different thread than ui, invokes player with provided video url
	def find(self,urls,callback, end_callback):
		target = face_recognition.load_image_file(urls["face"])
		self.callback = callback
		self.end_callback = end_callback
		self.target_encodings = [face_recognition.face_encodings(target)[0]]
		self.player.play(urls["video"])
	
	#stores a frame where target is detected
	def push_frame(self, frame, location, count):
		top, right, bottom, left = location
		cv2.rectangle(frame, (left*4, top*4), (right*4, bottom*4), ( 0, 255, 0), 2)
		self.frames.append((frame,count))

	#called on another thread, sends frame to ui
	def send(self,elapsed,frame):
		frame = process_frame(frame)
		self.callback(elapsed,frame)

	#listener passed to player
	def handle_frame(self,ret, frame = None, elapsed = 0, count = 0):
		if not ret:
			self.end_callback(self.frames)
			return
		#scaling the frame for performance and converting to bgr
		scaled_frame = cv2.resize(frame,(0,0), fx=0.25, fy=0.25)
		rgb_frame = scaled_frame[:,:,::-1]
		#finding faces in frame and their encodings
		self.face_data["locations"]=face_recognition.face_locations(rgb_frame)
		self.face_data["encodings"]=face_recognition.face_encodings(rgb_frame, self.face_data["locations"])
		#for each face found its encoding compared to target encoding and stored
		for location, encoding in zip(self.face_data["locations"], self.face_data["encodings"]):
			match = face_recognition.compare_faces(self.target_encodings,encoding)
			if match[0]:
				self.push_frame(frame, location, count)
				continue
			top, right, bottom, left = location
			cv2.rectangle(frame, (left*4, top*4), (right*4, bottom*4), (0, 0, 255), 2)
		#sending frame to ui
		threading.Thread(target=self.send, args=(elapsed,frame)).start()
