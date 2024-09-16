from glob import glob
import os
import time
from pathlib import Path, PurePath
from django.core.management.base import BaseCommand, CommandError
from polls.models import Question as Poll

class Command(BaseCommand):
    help = 'Scrap the AET log files'

	def xelonFromFilename(self, filename):
		#print(filename)
		filename2 = filename.split("\\")[-1]
		filename2 = filename2.split("_")[0]
		#print(filename.split("_")[0])
		return filename2

	def matRefFromFilename(self, filename):
		#print(filename)
		filename2 = filename.split("\\")[-1]
		filename2 = filename2.split("_")[1]
		#print(filename.split("_")[0])
		return filename2

	def compFromFilename(self, filename):
	#print(filename)
		filename2 = filename.split("\\")[-1]
		filename2 = filename2.split("_")[2]
	#print(filename.split("_")[0])
		return filename2

	def verif_bon(d):
		try:
			# exclure AET garçonnière
			if d[0][2]  == "38-00":
				return False
			# exclure mauvais logs
			if d[-1:][0][2] != "OK":
				return False
		except:
			return False
		return True

	def d2dict(self, d, filename, ref):
		dictt = {}
		list_dictt = []
		for line in d:
			try:
				if not '' in line:
					#print(line)
					dictt["REF"] = ref
					dictt["AET"] = d[0][2]
					dictt["XELON"] = xelonFromFilename(filename)
					dictt["MAT_REF"] = matRefFromFilename(filename)
					dictt["COMP_REF"] = compFromFilename(filename)
					dictt["DATE"] = os.stat(filename).st_mtime
					dictt["MEASURE_NAME"] = line[1]
					dictt["VALUE"] = line[2].replace(",",".")
					dictt["LOWER_BOND"] = line[4].replace(",",".")
					dictt["UPPER_BOND"] = line[5].replace(",",".")
					#print(dictt)
					list_dictt.append(dictt.copy())
			except:
				pass
		#print(list_dictt)
		return list_dictt


	def handle(self)
		now = time.time()

		ref_prod = ["DCM3.5","DCM6.2A","DCM6.2C","E98","EDC15C2","EDC16C34","EDC17C60","EDC17C84","ME17.9.52","VD46.1"]
		new_files = []
		for ref in ref_prod:
			#print(ref)
			fichiers_csv = []
			# path = f"L:\\LOGS\\LOG_AET\\{ref}\\*\\*.csv"
			path = f"L:\\LOGS\\LOG_AET\\{ref}\\"
			path = Path(path)
			#for pathi in os.listdir(path):
			#	print(pathi)
			#exit()
			path = str(PurePath(path, "*\\*.csv" ))
			list_fichiers_par_ref = glob(path , recursive = True)


			for fichier in list_fichiers_par_ref:
				if(now - os.stat(fichier).st_mtime < 24*3600):
					new_files.append((fichier,ref))
			#print(os.path.getctime(fichier))
			#print(len(new_files))

		all_products_list_dictt = []
		for new_file, ref in new_files:
			with open(new_file,"r") as file:
				data=file.read().splitlines()
				data2=[] 
				#print("vin", vin_from_filename(new_file))
				if xelonFromFilename(new_file)[1:] == "123456789":
					continue
				for i in data:
					data2.append(i.split(";"))
				if(verif_bon(data2)):
					list_dictt = d2dict(data2, new_file, ref)
					all_products_list_dictt.append(list_dictt)

		print(all_products_list_dictt)