import socket
import sys, threading, os
from tkinter import *
from tkinter import filedialog
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
	filename = ''

	def send_msg():
		global file_attachment, filename
		msg = msg_box.get("1.0", "end-1c")
		to = "*"*255
		ok = False
		option = ''
		if msg != '':
			if selected_group.get() != 'None':
				option = '2'
				to = selected_group.get()
				selected_person.set('')
				file_attachment = False
			elif selected_person.get() != '':
				option = '1'
				to = selected_person.get()
				selected_group.set('None')
			elif file_attachment:
				msg_box.delete("1.0", "end")
				ok = True
			else:
				ok = True
				file_attachment = False

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
			file_attachment = False

			try:
				# import pdb;pdb.set_trace()
				data = f"{option} {to} {name} {os.path.basename(filename)}"
				client.sendall(data.encode())

				chat_box.config(state="normal")
				chat_box.insert("end", f" <File - You>  {os.path.basename(filename)}\n")
				chat_box.config(state="disabled")
				msg_box.delete("1.0", "end")

				with open(filename, "r") as reader:
					while True:
						content = reader.read(36050)
						if not content:
							break

						msg = content
						data = f"{option} {to} {name} {msg}"
						client.sendall(data.encode())
						time.sleep(0.1)

				msg = 'Done'
				data = f"{option} {to} {name} {msg}"
				client.sendall(data.encode())
			except:
				client.close()

	send_btn = Button(window, text="Send", command=send_msg)
	send_btn.place(x=475, y=568, width=95, height=70)

	def browse_file():
		global file_attachment, filename
		file_attachment = True
		filename = filedialog.askopenfilename(initialdir=".", title="Select A File", filetype=(("text", "*.txt"), ("document", "*.pdf"), ("document word", "*.docx"), ("image jpeg", "*.jpg"), ("image png", "*.png"), ("image bmp", "*.bmp"), ("image gif", "*.gif"), ("All Files", "*.*")))


	file_btn = Button(window, text="File", command=browse_file)
	file_btn.place(x=475, y=638, width=95, height=30)

	def receive_msg(radiobuttons_persons, PERSONS, selected_person):
		while True:
			try:
				# 0 - type
				# 1 - to
				# 2 - from
				# 3 - msg
				data = client.recv(36567).decode().split(' ')

				# Private message
				if data[0] == '1':
					chat_box.config(state="normal")
					chat_box.insert("end", f" <{data[2]}>  {data[3]}\n")
					chat_box.config(state="disabled")
				# Group message
				elif data[0] == '2':
					chat_box.config(state="normal")
					chat_box.insert("end", f" <Group: {data[1]} - {data[2]}>  {data[3]}\n")
					chat_box.config(state="disabled")
				# Send file
				elif data[0] == '3':
					chat_box.config(state="normal")
					chat_box.insert("end", f" <File - {data[2]}>  {data[3]}\n")
					chat_box.config(state="disabled")

					filename = data[3]
					with open(os.path.join(".", filename), "w") as writer:
						while True:
							if data[3] == 'Done':
								break

							writer.write(data[3])
							data = client.recv(36567).decode().split()
				# Update list of users
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

	window.mainloop()
	client.close()