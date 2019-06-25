import ui, detector
import threading, cv2, sys
class LookUp:

	def __init__(self):
		self.urls ={}
		self.end_frames = []
		self.uih = ui.UIHandler()
		self.uih.start(self.callback)

	#ui callbacks
	def callback(self, id, content = None):
		if id == "start":
			if ("video" in self.urls) & ("face" in self.urls):
				self.uih.confirm_start()
				self.find()
			else:
				self.uih.error("Invalid file(s)")
		elif id in {"find","save","play"}:
			eval('self.' + id + '(' + (content if content else ' ') + ')')
		elif content:
			self.urls[id]=content

	#mediator function between detector and ui
	def pass_frame(self,elapsed, frame):
		self.uih.pass_frame(frame, elapsed)

	def play(self):
		self.uih.error("loading")
		player = detector.Player(self.pass_frame)
		#playing stamped target frames
		threading.Thread(target = player.play_frames, args = (self.end_frames,)).start()

	def stamp(self, frame_tuple):
		cv2.putText(frame_tuple[0],f'frame: {frame_tuple[1]}',(10,50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255),4,cv2.LINE_AA)
		return frame_tuple[0]

	#called when there is no more frames in the video, 'frames' constains the frame and the frame's number
	def end(self,frames):
		self.end_frames = [self.stamp(tup) for tup in frames]
		#first frame passed to ui
		self.uih.stage_final(detector.process_frame(self.end_frames[0]) if len(self.end_frames) > 0 else None)

	#starting the search on another thread than ui
	def find(self):
		detect = detector.Detect()
		threading.Thread(target=detect.find, args=(self.urls, self.pass_frame, self.end)).start()

	#saves the parts where target was found
	def save(self):
		if len(self.end_frames) < 1:
			return
		height, width, layer = self.end_frames[0].shape
		#creating an output url from video source url by replacing the name
		url = self.urls["video"].replace(self.urls["video"].split("/")[-1],"output.mp4")
		#video stream from destination url, format, frames per sec and dimensions
		stream = cv2.VideoWriter(url ,cv2.VideoWriter_fourcc(*'mp4v'), 15, (width,height))   
		for frame in self.end_frames:
			stream.write(frame)
		stream.release()
		#close window after writing
		sys.exit(0)


LookUp()