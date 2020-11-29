import socket
import sys, threading
from tkinter import *
import time
from pynput.keyboard import Listener, Key

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

	# chat box
	scrollbar_chat = Scrollbar(window)
	chat_box = Text(window, wrap="word", bg="black", fg="white", yscrollcommand=scrollbar_chat.set, state="disabled")
	chat_box.place(x=5, y=50, width=450, height=500)
	# scrollbar_chat.config(command=chat_box.yview)
	# scrollbar_chat.place(x=445, y=50, anchor="w")

	# groups on the server
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

	# persons on the server
	scrollbar_person = Scrollbar(window)
	Label(window, text="Online users", bg="black", fg="green", font=24).place(x=505, y=285)
	person_box = Text(window, wrap="word", bg="black", fg="white", yscrollcommand=scrollbar_person.set, state="disabled")
	person_box.place(x=456, y=320, width=190, height=230)

	# message box for typing
	radiobuttons_persons = []
	PERSONS = []
	selected_person = StringVar()

	scrollbar_msg = Scrollbar(window)
	msg_box = Text(window, wrap="word", bg="black", fg="white", yscrollcommand=scrollbar_msg.set)
	msg_box.place(x=5, y=570, width=450, height=100)

	file_attachment = False

	def send_msg():
		msg = msg_box.get("1.0", "end-1c")
		to = "*"*255
		ok = False
		option = ''
		if msg != '':
			if selected_group.get() != 'None':
				option = '2'
				to = selected_group.get()
				selected_person.set('')
			elif selected_person.get() != '':
				option = '1'
				to = selected_person.get()
				selected_group.set('None')
			elif file_attachment:
				msg_box.delete("1.0", "end")
				ok = True
			else:
				ok = True

			if not ok:
				data = f"{option} {to} {name} {msg}"

				try:
					client.sendall(data.encode())
				except:
					print("Connection error!")
					client.close()

				chat_box.config(state="normal")

				if option == '1':
					chat_box.insert("end", " <You>  ")
				elif option == '2':
					chat_box.insert("end", f" <Group: {to} - You>  ")

				chat_box.insert("end", f"{msg}\n",)
				chat_box.config(state="disabled")
				msg_box.delete("1.0", "end")
		if file_attachment:
			option = '3'
			selected_group.set('None')
			to = selected_person.get()
			# TODO: build up the message -> read file and send to the server

			data = f"{option} {to} {name} {msg}"


	send_btn = Button(window, text="Send", command=send_msg)
	send_btn.place(x=475, y=573, width=95, height=95)

	def receive_msg(radiobuttons_persons, PERSONS, selected_person):
		while True:
			try:
				# 0 - type
				# 1 - to
				# 2 - from
				# 3 - msg
				data = client.recv(36567).decode().split(' ')

				if data[0] == '1':
					chat_box.config(state="normal")
					chat_box.insert("end", f" <{data[2]}>  ")
					chat_box.insert("end", f"{data[3]}\n")
					chat_box.config(state="disabled")
				elif data[0] == '2':
					chat_box.config(state="normal")
					chat_box.insert("end", f" <Group: {data[1]} - {data[2]}>  ")
					chat_box.insert("end", f"{data[3]}\n")
					chat_box.config(state="disabled")
				elif data[0] == '4':
					while True:
						if data[3] == 'CTS':
							break
						PERSONS.append(data[3])

						data = client.recv(781).decode().split(' ')

					for b in radiobuttons_persons:
						b.pack_forget()
						b.destroy()
					person_box.delete("1.0", "end")

					radiobuttons_persons = []

					for v in PERSONS:
						if v != name:
							b = Radiobutton(person_box, text=v, value=v, variable=selected_person, bg="black", fg="white", indicatoron=0, selectcolor="gray")
							b.pack(anchor="center")
							radiobuttons_persons.append(b)
			except:
				print("Connection error!")
				client.close()
				break


	receive_thread = threading.Thread(target=receive_msg, args=(radiobuttons_persons, PERSONS, selected_person))
	receive_thread.start()

	# def chat_logic():
	# 	radiobuttons_persons = []
	# 	file_attachment = False

	# 	while True:
	# 		# option = 1 --> Private message
	# 		# option = 2 --> Group message
	# 		# option = 3 --> Send file
	# 		# option = 4 --> Update list of users
	# 		if selected_person.get() != '':
	# 			option = '1'
	# 			data = f"{option} {selected_person.get()} {name}"

	# 		client.sendall(data.encode())

	# 		# have to make another thread for it!!!!!!!
	# 		if option == '4':
	# 			PERSONS = []

	# 			while True:
	# 				try:
	# 					data = client.recv(255).decode()
	# 				except:
	# 					sys.exit()

	# 				if data == 'CTS':
	# 					break
	# 				PERSONS.append(data)

	# 			for b in radiobuttons_persons:
	# 				b.destroy()

	# 			radiobuttons_persons = []

	# 			for v in PERSONS:
	# 				if v != name:
	# 					b = Radiobutton(person_box, text=v, variable=selected_person, bg="black", fg="white", indicatoron=0, selectcolor="gray")
	# 					b.pack(anchor="center")
	# 					radiobuttons_persons.append(b)

	# 			if selected_person.get() != '':
	# 				for b in radiobuttons_persons:
	# 					if b.cget('text') == selected_person.get():
	# 						b.select()
	# 						break
	# 			else:
	# 				selected_person.set('')


	# chat_logic_thread = threading.Thread(target=chat_logic)
	# chat_logic_thread.start()

	window.mainloop()
	client.close()