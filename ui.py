from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar, Style

base = { "font":("Arial bold",30), "anchor":"c" }

theme = {
	"buttons":{
		"normal": { **base,"fg":"white", "bg":"#1c1d22"},
		"inverted": {**base,"fg":"#3f55e1", "bg":"#1c1d22"}
	},
	"labels":{
		"error": {"fg":"red", "bg":"#21232a","font":("Arial bold",10), "anchor":"c"},
		"colored": {**base,"fg":"white", "bg":"#3f55e1"}
	}
}

files = {
	"video":('video files',('.mp4')),
	"face":('image files', ('.png', '.jpg'))
}

class UIHandler:
	
	def __init__(self):
		self.stages={}
		self.root=Tk()
		s = Style()
		s.theme_use("default")
		s.configure("TProgressbar", thickness=25, background="#5169ff", pady=20, padx=10)

	def __open_dialog(self,button, display_text):
		self.error("")
		url = filedialog.askopenfilename(initialdir = "/", title = display_text,  filetypes=[files[display_text.split()[0].lower()]])
		if url:
			button.configure(fg="#9aa2b1")
			self.callback(display_text.split()[0].lower(), content=url )

	def confirm_start(self):
		self.stages["progress"]=self.__stage_progress()

	def pass_frame(self, frame, value = None):
		self.stages["progress"][1].configure(image=frame)
		self.stages["progress"][1].image = frame
		self.error("")
		if value:
			self.stages["progress"][0]['value']=value*100
			self.root.update_idletasks()

	def __full_button(self,parent, display_text, callback, style, pack = "top", lm = 0, tm=0):
		button=Label(parent, text=display_text, **theme["buttons"][style])
		button.bind("<Button-1>", lambda e, button = button:callback(button,display_text))
		button.pack( fill=BOTH, expand=1, side=pack,ipadx=20, ipady=40, padx=(lm,10), pady=(tm,10))
		return button

	def __label(self,parent,style,text, ipady):
		label=Label(parent, text=text,**theme["labels"][style])
		label.pack(fill=BOTH, expand=1, ipady=ipady, ipadx=40)
		return label

	def __stage_main(self):
		frame = Frame(self.root, bg="#21232a")
		frame.pack(fill=BOTH, expand=1)
		widgets = [frame]
		self.__full_button(frame,"Video Source", self.__open_dialog, "normal", pack="left", lm=10)
		self.__full_button(frame,"Face Source", self.__open_dialog, "normal", pack="right")
		widgets.append(self.__full_button(self.root,"Find", lambda x,y:self.callback("start"), "inverted", lm=10))
		return widgets

	def stage_final(self,first_frame = None):
		self.stages["progress"][0].pack_forget()
		if first_frame is not None:
			frame = Frame(self.root, bg="#21232a")
			frame.pack(fill=BOTH, expand=1)
			self.__full_button(frame,"Play",lambda x,y: self.callback("play"),"normal",pack="left", lm=10, tm=10)
			self.__full_button(frame,"Save",lambda x,y: self.callback("save"),"normal",pack="right",tm=10)
			self.pass_frame(first_frame)
		else: self.stages["progress"][1].pack_forget()

	def __stage_progress(self):
		for widget in self.stages["main"]:
			widget.pack_forget()
		feed = Label(self.root)
		feed.pack(padx=10)
		progress=Progressbar(self.root,orient=HORIZONTAL,mode='determinate')
		progress.pack(fill=X, expand=1, padx=10,pady=10)
		return [progress,feed]

	def error(self,text):
		self.error_label.configure(text=text)

	def start(self,callback):
		self.callback=callback
		self.root.title("Face Detection")
		self.root.configure(background="#21232a")
		self.__label(self.root,"colored","Face Detection",10)
		self.error_label=self.__label(self.root,"error","",0)
		self.stages["main"]=self.__stage_main()
		self.root.mainloop()
