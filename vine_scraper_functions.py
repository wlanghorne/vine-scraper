from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import csv
from time import sleep

url_1 = "https://vinelink.vineapps.com/search/persons;limit=1000;offset=0;showPhotos=false;isPartialSearch=false;siteRefId=ARSWVINE;personFirstName=" 
url_2 = ";personLastName=" 
url_3 = ";stateServed=AR"

def try_loading(url, driver):
	not_loaded = True
	while not_loaded: 
		driver.get(url)
		try: 
			WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.ID, "cdk-overlay-0")))
			not_loaded = False
		except:
			print("Page failed to load. Trying again...")
			not_loaded = True
			sleep(1)


def load_page(url, driver_path):
	
	# Initiate driver  
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("window-size=1920,1080")
	s = Service(driver_path)
	driver = webdriver.Chrome(service=s, options=chrome_options)
	driver.get(url)

	# HANDLE POPUPS 
	has_buttons = False 
	while not has_buttons:
		try_loading(url, driver)
		overlay = driver.find_element(By.ID, "cdk-overlay-0")
		buttons = overlay.find_elements(By.TAG_NAME, "button")
		try: 
			buttons[1].click()
			has_buttons = True
		except: 
			print("Couldn't find overlay button. Trying again...")
			has_buttons = False 
			sleep(1)

	WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "cdk-overlay-1")))
	overlay = driver.find_element(By.ID, "cdk-overlay-1")
	overlay.find_elements(By.TAG_NAME, "button")[0].click()

	return driver

def load (driver):
	try:
		WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".show-more.ng-star-inserted")))
	except: 
		return False
	load_more = driver.find_elements(By.CSS_SELECTOR, ".show-more.ng-star-inserted")
	load_fail = True
	while load_fail:
		try:
			load_more[0].find_element(By.TAG_NAME, "button").click()
			load_fail = False
		except:
			load_fail = True
			load_more = driver.find_elements(By.CSS_SELECTOR, ".show-more.ng-star-inserted")
			sleep(1)
	return True


def get_persons(url, driver_path, output_path):
	driver = load_page(url, driver_path)

	# Load all persons on the page
	#loading = True
	#while loading:
	#	loading = load(driver)
	
	cards = driver.find_elements(By.TAG_NAME, "vl-person-card")

	if not cards: 
		print("Trying to load page with fewer to check for error")

		driver = load_page(url.replace("1000", "100"), driver_path)
		cards = driver.find_elements(By.TAG_NAME, "vl-person-card")
		if not cards: 
			print("No persons listed with cooresponding lastname search")
			return False

	
	# Get person cards with status data
	data_dict = {}
	 
	for card in cards: 
		if card.find_elements(By.ID, "person-custody-status-value"):
			#print("Found custody card")
			if "In Custody" in card.find_element(By.ID, "person-custody-status-value").get_attribute("innerHTML"):
				#print("Found in-custody card")
				if card.find_elements(By.ID, "person-reporting-agency-name"):
					agency_name = card.find_element(By.ID, "person-reporting-agency-name").get_attribute("innerHTML")
					if "Community Correction" not in agency_name and "Department of Correction" not in agency_name and "Arkansas State Hospital" not in agency_name:
						#print("Found a local in-custody card")
						name = ""
						if card.find_elements(By.ID, "person-name"):
							name = card.find_element(By.ID, "person-name").get_attribute("innerHTML")
							data_dict[name] = [agency_name]
						if card.find_elements(By.ID, "person-age-value"):
							data_dict[name].append(card.find_element(By.ID, "person-age-value").get_attribute("innerHTML"))
						else: 
							data_dict[name].append("")
						if card.find_elements(By.ID, "person-gender-value"):
							data_dict[name].append(card.find_element(By.ID, "person-gender-value").get_attribute("innerHTML"))
						else: 
							data_dict[name].append("")
						if card.find_elements(By.ID, "person-race-value"):
							data_dict[name].append(card.find_element(By.ID, "person-race-value").get_attribute("innerHTML"))
						else: 
							data_dict[name].append("")
	driver.quit()

	if data_dict: 
		return data_dict
	else: 
		print("No one in local custody with cooresponding lastname search")
		return False

def get_charges(url, driver_path, names, load_num, data_dict):

	hit_name = False 
	no_more_load = True

	driver = load_page(url, driver_path)

	proper_load = False 

	# Make sure the page loaded with names
	while not proper_load: 
		no_names = driver.find_elements(By.ID, "pnf-main-header")
		if no_names:
			if "No results found" in no_names[0].get_attribute("innerHTML"):
				print("Error in loading page... trying again")
				driver = load_page(url, driver_path)
		else:
			proper_load = True

	while not hit_name: 

		cards = driver.find_elements(By.TAG_NAME, "vl-person-card")

		# load the page only as many times as needed
		#for i in range(load_num):
		#	if not load(driver):
		#		no_more_load = True

		for card in cards: 
			name = card.find_element(By.ID, "person-name").get_attribute("innerHTML")
			agency_name = card.find_element(By.ID, "person-reporting-agency-name").get_attribute("innerHTML")

			# if name and agency match, get charge info 
			if name in names and agency_name in data_dict[name][0]:
				print("Getting info for " + name)

				hit_name = True

				try: 
					WebDriverWait(card, 5).until(EC.presence_of_element_located((By.ID, "person-details-button")))
				except: 
					print("There are no additional details available for " + name)

				detail_button = card.find_elements(By.ID, "person-details-button")

				if detail_button:
					detail_button[0].click()

					try: 
						WebDriverWait(driver, 60).until(EC.staleness_of(detail_button[0]))
					except:
						print("Unable to get details. Trying again")
						sleep(2)
						return get_charges(url, driver_path, names, load_num, data_dict)

					WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, "cc-ok-button")))

					ok_button = driver.find_elements(By.ID, "cc-ok-button")

					if ok_button:

						ok_clicked = False 
						while not ok_clicked:

							try: 
								ok_button[0].click()
								ok_clicked = True
							except: 
								ok_button = driver.find_elements(By.ID, "cc-ok-button")
								ok_clicked = False 
								sleep(1)

					try: 
						WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "person-charge-details")))
					except: 
						print("There are no charge details available for " + name)
						names.remove(name)

					charge_button = driver.find_elements(By.ID, "person-charge-details")
					if charge_button:

						charge_clicked = False 
						while not charge_clicked:
							try: 
								charge_button[0].click()
								charge_clicked = True
							except: 
								charge_button = driver.find_elements(By.ID, "person-charge-details")
								charge_clicked = False 
								sleep(1)


						charge_wrappers = driver.find_elements(By.CSS_SELECTOR, ".labeled-data.bold-labels.ng-star-inserted")

						charges = []
						if charge_wrappers:
							for i in range(len(charge_wrappers)):
								charge_name = driver.find_elements(By.ID, "charge-name-data-" + str(i))
								if charge_name:
									charges.append(charge_name[0].get_attribute("innerHTML"))
						
						data_dict[name].append(charges)
						names.remove(name)

						print("There are " + str(len(names))+ " names remaining for this letter combination")
				break

		if not hit_name:
			if not no_more_load:
				load_num = load_num + 1
			else:
				driver.quit()
				return data_dict 


	driver.quit()
	if names:
		return get_charges(url, driver_path, names, load_num, data_dict)
	else:
		return data_dict


def scrape_page(url, driver_path, output_path, ignore_names):

	data_dict = get_persons(url, driver_path, output_path)

	# if there are people being held by local law enforcement in jails, get their charges 
	if data_dict: 
		names = set(data_dict.keys())
		names = list(names - set(ignore_names))
				
		data_dict = get_charges(url, driver_path, names, 0, data_dict)

		with open(output_path, 'a') as f: 
			writer = csv.writer(f)
			for name in data_dict.keys():
				writer.writerow([name] + data_dict[name])

			f.close()








