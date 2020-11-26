import socket
import sys, threading
from tkinter import *
import time

name = ''

window = Tk()
window.title("ChatApp")
window.configure(background="black")
window.geometry("400x100+700+300")
window.resizable(False, False)

def get_name():
	global name
	if et_name.get() != '':
		name = et_name.get().strip()
		window.destroy()


Label(window, text="Enter your name: ", bg="black", fg="white").grid(row=0, column=0, padx=(40, 10), pady=35, sticky="W")
et_name = Entry(window, width=20, bg="white")
et_name.grid(row=0, column=1, pady=35, sticky="W")
btn_connect = Button(window, text="Connect", command=get_name).grid(row=0, column=2, padx=10, pady=35, sticky="W")
window.mainloop()

server_ip, port = 'localhost', 13001
server_addr = (server_ip, port)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(server_addr)

def popupmsg(msg):
	popup = Tk()
	popup.wm_title("X")
	popup.geometry("+800+350")
	label = Label(popup, text=msg, font=10)
	label.pack(side="top", fill="x", pady=10)
	B1 = Button(popup, text="Ok", command=popup.destroy)
	B1.pack()
	popup.mainloop()


try:
	client.sendall(name.encode())
	result = client.recv(14).decode()
except socket.error as err:
	print(err)
	client.close()
	sys.exit()


if result == 'nack':
	popupmsg("This nickname is already taken!")
	client.close()
	sys.exit()
elif result == 'ack':
	window = Tk()
	window.title("ChatApp")
	window.configure(background="black")
	window.geometry("650x720+650+150")
	window.resizable(False, False)


	# chat box todo: logic
	scrollbar_chat = Scrollbar(window)
	chat_box = Text(window, wrap="word", bg="black", fg="white", yscrollcommand=scrollbar_chat.set, state="disabled")
	chat_box.place(x=5, y=50, width=450, height=500)
	# scrollbar_chat.config(command=chat_box.yview)
	# scrollbar_chat.place(x=445, y=50, anchor="w")

	# groups on the server, todo: update it & logic
	scrollbar_group = Scrollbar(window)
	Label(window, text="Groups", bg="black", fg="red", font=24).place(x=520, y=10)
	group_box = Text(window, wrap="word", bg="black", fg="white", yscrollcommand=scrollbar_group.set, state="disabled")
	group_box.place(x=456, y=50, width=190, height=225)

	GROUPS = ["None", "Kings", "Gamers", "TrollChat"]
	radiobuttons_group = []
	selected_group = StringVar()

	for v in GROUPS:
		b = Radiobutton(group_box, text=v, value=v, variable=selected_group, bg="black", fg="white", indicatoron=0, selectcolor="gray")
		b.pack(anchor="center")
		radiobuttons_group.append(b)

	radiobuttons_group[0].select()

	# persons on the server, todo: update it & logic
	scrollbar_person = Scrollbar(window)
	Label(window, text="Online users", bg="black", fg="green", font=24).place(x=505, y=285)
	person_box = Text(window, wrap="word", bg="black", fg="white", yscrollcommand=scrollbar_person.set, state="disabled")
	person_box.place(x=456, y=320, width=190, height=230)

	# message box for typeing, todo: action
	scrollbar_msg = Scrollbar(window)
	msg_box = Text(window, wrap="word", bg="black", fg="white", yscrollcommand=scrollbar_msg.set)
	msg_box.place(x=5, y=570, width=450, height=100)

	def send_msg():
		if msg_box.text != '':
			


	send_btn = Button(window, text="Send", command=send_msg)
	send_btn.place(x=475, y=573, width=95, height=95)


	selected_person = StringVar()
	option = 'sendlistofnames'

	def update_person_list():
		radiobuttons_persons = []
		while True:
			PERSONS = []
			client.sendall(option.encode())

			while True:
				try:
					data = client.recv(255).decode()
				except:
					sys.exit()

				if data == 'ack':
					break
				PERSONS.append(data)

			# print(PERSONS)

			for b in radiobuttons_persons:
				b.destroy()

			radiobuttons_persons = []

			# print(selected_person.get())

			for v in PERSONS:
				if v != name:
					b = Radiobutton(person_box, text=v, variable=selected_person, bg="black", fg="white", indicatoron=0, selectcolor="gray")
					b.pack(anchor="center")
					radiobuttons_persons.append(b)

			time.sleep(10)


	update_person_list_thread = threading.Thread(target=update_person_list)
	update_person_list_thread.start()

	window.mainloop()
	client.close()