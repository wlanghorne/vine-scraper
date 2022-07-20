from vine_scraper_functions import scrape_page
import os
import csv
import string
import sys

url_1 = "https://vinelink.vineapps.com/search/persons;limit=1000;offset=0;showPhotos=false;isPartialSearch=true;siteRefId=ARSWVINE;personFirstName=;personLastName="
url_2 = ";stateServed=AR"
driver_path = "./chromedriver"

name_suffix = ["jr", "sr", "i", "ii", "iii", "iv", "v", "vi"]

out_path = "./outputs/raw"

file_basename = "raw_output_"

headers = ["Name", "Agency", "Age", "Gender", "Race", "Charges"]

# Get last created raw output file
latest_file_num = 0
raw_files =[file for file in os.listdir(out_path) if file.endswith(".csv")]

for file in raw_files:
	file_num = int(str(file).replace(".csv","").replace(file_basename, ""))
	if file_num > latest_file_num:
		latest_file_num = file_num

# Get names to ignore
ignore_names = []
for raw_file in raw_files:
	with open(os.path.join(out_path,raw_file), "r") as file:
		reader = csv.reader(file)
		next(reader)
		for row in reader:
			ignore_names.append(row[0])

latest_file = ""
if latest_file_num > 0 :
	latest_file = file_basename + str(latest_file_num) + ".csv"

first_ltrs = string.ascii_lowercase
second_ltrs = string.ascii_lowercase
combos = []

urls = {}

for ltr in first_ltrs:
	for ltr_2 in second_ltrs:
		combos.append(ltr + ltr_2)

combos = sorted(list(set(combos)))


# Handle commandline arguments
start_combo = "aa"
end_combo = "zz"
command = ""

# Handle command line arguments 
argv = sys.argv
argv_len = len(argv)

if argv_len == 2:
	command = argv[1]
elif argv_len == 3:
	command = argv[1]
	start_combo = argv[2]
elif argv_len == 4:
	command = argv[1]
	start_combo = argv[2]
	end_combo = argv[3]
else:
	print("Error: must enter between one and three arguments. ['write'/'append' to write a new file or append to latest output file] [optional start letter combo] [optional end letter combo]")
	exit()

start_index = combos.index(start_combo)
end_index = combos.index(end_combo)

out_file_path = ""
if command == "write":
	# create new file and write to it 
	out_file = file_basename + str(latest_file_num + 1) + ".csv"
	out_file_path = os.path.join(out_path, out_file) 
	with open(out_file_path, "w") as file: 
		writer = csv.writer(file)
		writer.writerow(headers)
		file.close()
elif command == "append":
	if latest_file == 0:
		print("Error: No files to append to.")
		exit()
	else: 
		out_file = latest_file
		out_file_path = os.path.join(out_path, out_file)
else: 
	print("Error: Invalid command") 

for combo in combos[start_index : end_index+1]:
	urls[combo] = url_1 + combo + url_2

print("Getting info for people with lastnames from " + start_combo + " to " + end_combo)

for ltr_combo in urls.keys(): 

	print('Getting data for lastnames starting with: ' + ltr_combo)
	
	scrape_page(urls[ltr_combo], driver_path, out_file_path, ignore_names)

	


