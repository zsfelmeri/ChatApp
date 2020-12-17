import socket
import sys, threading, os
from tkinter import *
from tkinter import filedialog
import time

name = ''
# stop_thread = False
sync_ok_file = False

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


def popup_create_group():
	global et_group_name, et_password, popup_grp

	popup_grp = Tk()
	popup_grp.wm_title("Create Group")
	popup_grp.geometry("300x200+700+300")
	popup_grp.configure(bg="black")
	popup_grp.resizable(False, False)
	Label(popup_grp, text="Group name: ", bg="black", fg="white").grid(row=0, column=0, padx=(40, 10), pady=35, sticky="W")
	et_group_name = Entry(popup_grp, width=20, bg="white")
	et_group_name.grid(row=0, column=1, pady=35, sticky="W")
	Label(popup_grp, text="Password: ", bg="black", fg="white").grid(row=1, column=0, padx=(40, 10), pady=10, sticky="W")
	et_password = Entry(popup_grp, width=20, bg="white")
	et_password.grid(row=1, column=1, pady=10, sticky="W")
	Button(popup_grp, text="Create", command=create_group).grid(row=2, column=1, padx=10, pady=15, sticky="W")
	popup_grp.mainloop()


def popup_confirm_file(size, file, sender):
	global conf_file

	popup = Tk()
	popup.wm_title("Confirm File Transfer")
	popup.geometry("+700+300")
	popup.configure(bg="black")
	popup.resizable(False, False)
	l = Label(popup, text=f"{sender} want to send you a file: size: {size} filename: {file}", bg="black", fg="white", font=12)
	l.pack(side="top", fill="x", pady=10)
	b1 = Radiobutton(popup, text="Yes, I want the file", value="ack", variable=conf_file, bg="black", fg="white", selectcolor="black")
	b1.pack(anchor="center")
	b2 = Radiobutton(popup, text="No, I do not want the file", value="nack", variable=conf_file, bg="black", fg="white", selectcolor="black")
	b2.pack(anchor="center")
	btn = Button(popup, text="Confirm", command=popup.destroy)
	btn.pack(anchor="center")
	popup.mainloop()


def popup_join_group():
	global selected_group, GROUPS

	def join_group():
		for grp, pwd in GROUPS:
			if selected_group.get() == grp and et_password.get() == pwd:
				option = '6'
				data = f"{option} {selected_group.get()} {name} join"
				try:
					client.sendall(data.encode())
				except:
					clinet.close()
				option = ''
				break

		popup_grp.destroy()

	popup_grp = Tk()
	popup_grp.wm_title("Join Group")
	popup_grp.geometry("300x200+700+300")
	popup_grp.configure(bg="black")
	popup_grp.resizable(False, False)
	Label(popup_grp, text=f"You want to join to {selected_group.get()} group!", bg="black", fg="green").place(x=80, y=10, height=18)
	Label(popup_grp, text="Password: ", bg="black", fg="white").grid(row=1, column=0, padx=(20, 10), pady=30, sticky="W")
	et_password = Entry(popup_grp, width=20, bg="white")
	et_password.grid(row=1, column=1, pady=10, sticky="W")
	Button(popup_grp, text="Join", command=join_group).grid(row=2, column=1, padx=20, pady=15, sticky="W")
	popup_grp.mainloop()


try:
	client.sendall(name.encode())
	result = client.recv(14).decode()
except socket.error as err:
	print(err)
	stop_thread = True
	client.close()
	sys.exit()


if result == 'nack':
	popupmsg("This nickname is already taken!")
	stop_thread = True
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

	# groups on the server
	def create_group():
		global GROUPS, selected_group, radiobuttons_group, et_group_name, et_password, popup_grp, stop_thread
		if (et_group_name.get(), et_password.get()) not in GROUPS and et_group_name.get() != '':
			GROUPS.append((et_group_name.get(), et_password.get()))
			option = '5'
			new_group = True

			b = Radiobutton(group_box, text=et_group_name.get(), value=et_group_name.get(), variable=selected_group, bg="black", fg="white", indicatoron=0, selectcolor="gray")
			b.pack(anchor="center")
			radiobuttons_group.append(b)

			msg = f"{GROUPS[-1][0]} {GROUPS[-1][1]}"
			data = f"{option} all {name} {msg}"

			try:
				client.sendall(data.encode())
			except:
				stop_thread = True
				client.close()

			option = ''

		popup_grp.destroy()


	scrollbar_group = Scrollbar(window)
	Label(window, text="Groups", bg="black", fg="red", font=24).place(x=520, y=10)
	group_box = Text(window, wrap="word", bg="black", fg="white", yscrollcommand=scrollbar_group.set, state="disabled")
	group_box.place(x=456, y=50, width=190, height=225)
	create_group_btn = Button(window, text="Create Group", command=popup_create_group)
	create_group_btn.place(x=400, y=10)

	GROUPS = [("None", "")]
	radiobuttons_group = []
	selected_group = StringVar()

	b = Radiobutton(group_box, text=GROUPS[0][0], value=GROUPS[0][0], variable=selected_group, bg="black", fg="white", indicatoron=0, selectcolor="gray")
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
	conf_file = StringVar()
	conf_file.set('ack')
	prev_group = 'None'
	# is_inGroup = False

	def send_msg():
		global file_attachment, filename, option, stop_thread, sync_ok_file, conf_file, radiobuttons_group, prev_group

		msg = msg_box.get("1.0", "end-1c")
		to = "*"*255
		ok = False
		if msg != '':
			if selected_group.get() != 'None':
				option = '2'
				to = selected_group.get()
				selected_person.set(None)
				file_attachment = False
				if prev_group != to:
					prev_group = selected_group.get()
					popup_join_group()
			elif selected_person.get() != '':
				option = '1'
				to = selected_person.get()
				selected_group.set('None')
				radiobuttons_group[0].select()
				prev_group = 'None'
			elif file_attachment:
				msg_box.delete("1.0", "end")
				ok = True
				prev_group = 'None'
			else:
				ok = True
				file_attachment = False
				prev_group = 'None'

			if not ok:
				data = f"{option} {to} {name} {msg}"

				try:
					client.sendall(data.encode())
				except:
					print("Connection error!")
					stop_thread = True
					client.close()

				chat_box.config(state="normal")

				if option == '1':
					chat_box.insert("end", " <You>  ")
				elif option == '2':
					chat_box.insert("end", f" <Group: {to} - You>  ")

				chat_box.insert("end", f"{msg}\n",)
				chat_box.config(state="disabled")
				msg_box.delete("1.0", "end")
				option = ''
		if file_attachment:
			option = '3'
			selected_group.set('None')
			radiobuttons_group[0].select()
			to = selected_person.get()
			file_attachment = False
			prev_group = 'None'

			try:
				info = os.stat(filename)
				size = info.st_size

				# convert to human readable format
				def human_readable(size, decimal=2):
					for unit in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']:
						if size < 1024.0 or unit == 'PB':
							break
						size /= 1024.0
					return f"{size:.{decimal}f}{unit}"


				size = human_readable(size)

				data = f"{option} {to} {name} {size} {os.path.basename(filename)}"
				client.sendall(data.encode())

				# while not sync_ok_file:
				# 	pass

				if conf_file.get() == 'ack':
					chat_box.config(state="normal")
					chat_box.insert("end", "Sending file...")
					chat_box.config(state="disabled")

					with open(filename, "rb") as reader:
						while True:
							content = reader.read(36050)
							if not content:
								break

							msg = content.replace(b'\x00', b'\\x00')
							client.sendall(msg)
							# time.sleep(0.5)

					time.sleep(0.5)
					chat_box.config(state="normal")
					chat_box.insert("end", f" Done\n<File - You>  {os.path.basename(filename)}\n")
					chat_box.config(state="disabled")
					msg_box.delete("1.0", "end")

				msg = 'Done'
				client.sendall(msg.encode())
				option = ''
			except:
				stop_thread = True
				client.close()


	send_btn = Button(window, text="Send", command=send_msg)
	send_btn.place(x=475, y=568, width=95, height=70)


	def browse_file():
		global file_attachment, filename
		file_attachment = True
		filename = filedialog.askopenfilename(initialdir=".", title="Select A File", filetype=(("text", "*.txt"), ("document", "*.pdf"), ("document word", "*.docx"), ("image jpeg", "*.jpg"), ("image png", "*.png"), ("image bmp", "*.bmp"), ("image gif", "*.gif"), ("All Files", "*.*")))


	file_btn = Button(window, text="File", command=browse_file)
	file_btn.place(x=475, y=638, width=95, height=30)


	def receive_msg():
		global stop_thread, radiobuttons_persons, PERSONS, selected_person, GROUPS, radiobuttons_group, selected_group, conf_file, sync_ok_file

		while True:
			try:
				# 0 - type
				# 1 - to
				# 2 - from
				# 3: - msg
				data = client.recv(36567).decode().split(' ')

				# Private message
				if data[0] == '1':
					chat_box.config(state="normal")
					chat_box.insert("end", f" <{data[2]}>  {' '.join(data[3:])}\n")
					chat_box.config(state="disabled")
				# Group message
				elif data[0] == '2':
					chat_box.config(state="normal")
					chat_box.insert("end", f" <Group: {data[1]} - {data[2]}>  {' '.join(data[3:])}\n")
					chat_box.config(state="disabled")
				# Send file
				elif data[0] == '3':
					sender = data[2]
					size = data[3]
					filename = ' '.join(data[4:])

					# popup_confirm_file(size=size, file=filename, sender=sender)

					# sync_ok_file = True

					if conf_file.get() == 'ack':
						chat_box.config(state="normal")
						chat_box.insert("end", "Receiving file...")
						chat_box.config(state="disabled")

						with open(os.path.join(".", filename), "wb") as writer:
							while True:
								data = client.recv(36050)
								if data == b'Done':
									break

								data = data.replace(b'\\x00', b'\x00')
								writer.write(data)


						chat_box.config(state="normal")
						chat_box.insert("end", f" Done\n<File - {sender}>  {filename}\n")
						chat_box.config(state="disabled")
				# Update list of users
				elif data[0] == '4':
					ls = []
					while True:
						if data[3] == 'CTS':
							break
						ls.append(data[3])

						data = client.recv(781).decode().split(' ')

					for b in radiobuttons_persons:
						b.pack_forget()
						b.destroy()
					person_box.delete("1.0", "end")

					PERSONS = []
					for v in ls:
						if v not in PERSONS:
							PERSONS.append(v)

					for v in PERSONS:
						if v != name:
							b = Radiobutton(person_box, text=v, value=v, variable=selected_person, bg="black", fg="white", indicatoron=0, selectcolor="gray")
							b.pack(anchor="center")
							radiobuttons_persons.append(b)
				# Update list of groups
				elif data[0] == '5':
					grp_name = data[3]
					grp_pwd = data[4]
					GROUPS.append((grp_name, grp_pwd))
					b = Radiobutton(group_box, text=grp_name, value=grp_name, variable=selected_group, bg="black", fg="white", indicatoron=0, selectcolor="gray")
					b.pack(anchor="center")
					radiobuttons_group.append(b)
			except:
				print("Connection error!")
				stop_thread = True
				client.close()
				break


	receive_thread = threading.Thread(target=receive_msg)
	receive_thread.start()

	window.mainloop()
	stop_thread = True
	client.close()