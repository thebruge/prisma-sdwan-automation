#! /usr/local/bin/python3.8

import jinja2
import os
import requests
import csv

template_file = "template-jinja.yml"
csv_parameter_file = "template-params.csv"
config_parameters = []
output_directory = "configs"

requests.packages.urllib3.disable_warnings()

### KARL SCHMUTZ - The following additional variables are needed to build the address
# this is used to determine the LAT/Long from the function get_lat_long (string)
headers = {}
site_lat_header = "site_lat"
site_long_header = "site_long"

site_lat_index = "site_lat"
site_long_index = "site_long"

site_street_column = -1
site_city_column = -1
site_state_column = -1
site_zipcode_column = -1
site_country_column = -1
site_street2_column = -1
site_street2_header = "street2"
site_street_header = "street"
site_city_header = "city"
site_state_header = "state"
site_zipcode_header = "post_code"
site_country_header = "country"

### this function does the address search against mapquest - please substitue for you own key
def get_lat_long (text_as_str):
    #latitude = 22
    #longitude = 33
    #return (latitude, longitude)
    map_url = f"https://www.mapquestapi.com/geocoding/v1/address?key=YXhn7Z43jl1rUOrevwzAsYLQStGhdGcu&location={address_concat}"
    location = requests.get(url=map_url, verify=False).json()
    latLng = location['results'][0]['locations'][0]['latLng']
    latitude = latLng['lat']
    longitude = latLng['lng']
    return (latitude, longitude)

# 1. read the contents from the CSV files -
#   Reworked to use the Python CSV handler as some edge cases were causing f.open to parse incorrectly
print("Read CSV parameter file...")
with open(csv_parameter_file, newline='') as csvinput:

    # 2. for Jinja2, we need to convert the given CSV file into the a python
    # dictionary to get the script a bit more reusable, I will not statically
    # limit the possible header values (and therefore the variables)
    print("Convert CSV file to dictionaries...")

    lineread = csv.reader(csvinput, delimiter=',', quotechar='"')

    ###Assume row 1 is the header row, assign the header columns
    row = next(lineread)
    for index,item in enumerate(row):

        headers[index] = item ## This line assignes the index to names for use in the DICT later
        if item == site_street_header:
            site_street_column = index
        if item == site_street2_header:
            site_street2_column = index
        if item == site_city_header:
            site_city_column = index
        if item == site_state_header:
            site_state_column = index
        if item == site_zipcode_header:
            site_zipcode_column = index
        if item == site_country_header:
            site_country_column = index
        if item == site_lat_header:
            latitude_column_index = index
        if item == site_long_header:
            longitude_column_index = index

    ##Now Read the remaining rows and assign the dict
    for index,row in enumerate(lineread):
        parameter_dict = dict()
        for i in range(0,len(row)):
            parameter_dict[headers[i]] = row[i]

        if parameter_dict[site_lat_header] == "" and parameter_dict[site_long_header] == "":
            address_concat = parameter_dict[site_street_header]
            address_concat += ", " + parameter_dict[site_city_header]
            address_concat += ", " + parameter_dict[site_state_header] + " " + parameter_dict[site_zipcode_header]
            if (parameter_dict[site_country_header] != ""):      #country is optional. if blank, do not use
                address_concat += ", "
                address_concat += parameter_dict[site_country_header]
            address_concat = address_concat.strip()
            print("     FOUND street address: ", address_concat)
            latlon_request = get_lat_long(address_concat)
            parameter_dict[site_lat_header] = latlon_request[0]
            parameter_dict[site_long_header] = latlon_request[1]

        config_parameters.append(parameter_dict)


# 3. next we need to create the central Jinja2 environment and we will load
# the Jinja2 template file
print("Create Jinja2 environment...")
env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="."))
template = env.get_template(template_file)

# we will make sure that the output directory exists
if not os.path.exists(output_directory):
    os.mkdir(output_directory)

# 4. now create the templates
print("Create templates...")
for parameter in config_parameters:
    result = template.render(parameter)
    f = open(os.path.join(output_directory, parameter['site_code'] + ".yaml"), "w")
    f.write(result)
    f.close()
    print("Configuration '%s' created..." % (parameter['site_code'] + ".yaml"))
print("DONE")
