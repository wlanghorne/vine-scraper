import csv 
import os

raw_path = "./outputs/raw/"
all_ftp_path = "./outputs/pro/ftps.csv"
pure_ftp_path = "./outputs/pro/pure.csv"
agency_path = "./outputs/pro/agencies.csv"

ftp_variations = ['ftp', 'to pay', 'nonpayment']

ftp_rows = []
pure_ftp_rows = []
agency_counter = {}

# Get raw files 
raw_files =[file for file in os.listdir(raw_path) if file.endswith(".csv")]

if not raw_files:
	print("No raw files to process")
	exit()

with open(os.path.join(raw_path,raw_files[0]), "r") as file:
	reader = csv.reader(file)
	ftp_rows = [next(reader) + ['Raw file']]
	pure_ftp_rows = ftp_rows

	file.close()

for raw_file in raw_files:


	with open(os.path.join(raw_path,raw_file), "r") as r_file: 
		reader = csv.reader(r_file)
		
		for row in reader:
			has_ftp = False
			pure_ftp = True
			agency = row[1].strip()
			if len(row) >= 6:
				charge_list = row[5].lower()

				charge_list = charge_list.strip('][').split(', ')

				if not agency in agency_counter.keys() :
					agency_counter[agency] = {"total": 0, "ftp": 0, "empty": 0}

				for charge in charge_list:
					curr_charge_ftp = False 
					charge = charge.lower()
					for ftp_variation in ftp_variations:
						if ftp_variation in charge and not "child" in charge:
							has_ftp = True
							curr_charge_ftp = True  

					if not curr_charge_ftp:
						pure_ftp = False 

				if has_ftp:
					agency_counter[agency]["ftp"] = agency_counter[agency]["ftp"] + 1 
					ftp_rows = ftp_rows + [row + [raw_file]]

				if pure_ftp:
					pure_ftp_rows = pure_ftp_rows + [row + [raw_file]]

				agency_counter[agency]["total"] = agency_counter[agency]["total"] + 1

				if not charge_list: 
					agency_counter[agency]["total"] = agency_counter[agency]["total"] + 1 
					agency_counter[agency]["empty"] = agency_counter[agency]["empty"] + 1 

		r_file.close()

# write all FTPs 
with open(all_ftp_path, "w") as all_file: 
	writer = csv.writer(all_file)

	for ftp_row in ftp_rows:
		writer.writerow(ftp_row)

	all_file.close()

# write all pure FTPs 
with open(pure_ftp_path, "w") as pure_file: 
	writer = csv.writer(pure_file)

	for pure_ftp_row in pure_ftp_rows:
		writer.writerow(pure_ftp_row)

	pure_file.close()

with open(agency_path, "w") as agency_file:
	writer = csv.writer(agency_file)

	writer.writerow(["Agency", "Total detainees", 'Detainees with FTPS', "Percentage with FTPS", "Detainees w/o charges listed"])

	for agency in agency_counter.keys():
		writer.writerow([agency, agency_counter[agency]["total"],agency_counter[agency]["ftp"], round(agency_counter[agency]["ftp"]/agency_counter[agency]["total"]*100,0),  agency_counter[agency]["empty"]])

	agency_file.close()