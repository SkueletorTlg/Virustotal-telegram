import math
import os
import time

from pyrogram import Client, Filters, ForceReply, InputMediaPhoto

from config import Config
from virustotal import virus

msgdic = {}

app = Client(
	"hey",
	api_id=Config.APP_ID,
	api_hash=Config.API_HASH,
	bot_token=Config.BOT_TOKEN
)


def progress(client, current, total, message_id, chat_id, start):
	now = time.time()
	diff = now - start
	if round(diff % 5.00) == 0 or current == total:
		percentage = current * 100 / total
		speed = current / diff
		elapsed_time = round(diff) * 1000
		time_to_completion = round((total - current) / speed) * 1000
		estimated_total_time = elapsed_time + time_to_completion
		elapsed_time = TimeFormatter(milliseconds=elapsed_time)
		estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
		progress = "[{0}{1}] \nPorcentaje: {2}%\n".format(
			''.join(["█" for i in range(math.floor(percentage / 5))]),
			''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
			round(percentage, 2)
		)
		tmp = progress + "{0} de {1}\Velocidad: {2}/s\nTiempo estimado: {3}\n".format(
			humanbytes(current),
			humanbytes(total),
			humanbytes(speed),
			estimated_total_time if estimated_total_time != '' else "0 s"
		)
		try:
			client.edit_message_text(
				chat_id,
				message_id,
				text="Descargando...\n {}".format(tmp)
			)
		except:
			pass

def humanbytes(size):
	if not size:
		return ""
	power = 2**10
	n = 0
	Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
	while size > power:
		size /= power
		n += 1
	return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
	seconds, milliseconds = divmod(int(milliseconds), 1000)
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
	tmp = ((str(days) + "d, ") if days else "") + \
		((str(hours) + "h, ") if hours else "") + \
		((str(minutes) + "m, ") if minutes else "") + \
		((str(seconds) + "s, ") if seconds else "") + \
		((str(milliseconds) + "ms, ") if milliseconds else "")
	return tmp[:-2]

@app.on_message(Filters.document)
def download_telegram_media(client, message):
	me=Config.userid
	if not message.from_user.id == me :
		client.send_message(
			chat_id=message.chat.id,
			text = 'Bot creado por @DKzippO'
		)
		return
	msg = client.send_message(
	  chat_id=message.chat.id,
	  text='Se está iniciando la descarga...\n¡Por favor, espera'
	)
	start_time = time.time()
	download_location = client.download_media(
	  message=message,
	  file_name='./',
	  progress=progress,
	  progress_args=(
		msg.message_id,
		message.chat.id,
		start_time
	  )
	)
	userid=message.from_user.id
	client.delete_messages(userid,msg.message_id)
	print('a')
	check_size(download_location,userid)
	print('b')

def send_msg(user,txt):
  app.send_message(user,txt,parse_mode="markdown")
  


def check_size(path,userid):
	viruslist = []
	reasons=[]
	b=os.path.getsize(path)
	print('file size is',b)
	obj=virus(str(path))
	if b>32*1024*1024:
		send_msg(userid,'Lo sentimos Este archivo es más grande que 32Mb')
		return
		obj.large_files()
	else:
		obj.smallfiles()
	if obj.res==False:
		send_msg(userid,'Error')
	send_msg(userid,obj.verbose)
	time.sleep(7)
	obj.get_report()
	for i in obj.report:
		
		if obj.report[i]['detected']==True:
			viruslist.append(i)
			reasons.append('➤ '+obj.report[i]['result'])
	if len(viruslist) > 0:
		names=' , '.join(viruslist)
		reason='\n'.join(reasons)
		send_msg(userid,'\n☣ --¡Se han detectado amenazas!-- ☣\n\n**{}** \n\n\n**Descripción**\n\n`{}`\n\n[Reporte detallado]({})'.format(names,reason,obj.link))
	else:
		send_msg(userid,'✔️ El archivo está limpio ')

app.run()
