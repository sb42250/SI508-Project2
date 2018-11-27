## proj_nps.py
## Skeleton for Project 2, Fall 2018
## ~~~ modify this file, but don't rename it ~~~
from secrets import google_places_key
from bs4 import BeautifulSoup
from cache import *
import requests
import json
import plotly
import plotly.plotly as py
import pandas as pd
plotly.tools.set_credentials_file(username='yyjia', api_key='sapIKxAZcU5WKeJxlRdC')
## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
#####chche
CACHE_FNAME = 'proj2_cache.json'
data =Cache(CACHE_FNAME)


######all state and url
dicti = {}
lst =[]
url = "https://www.nps.gov/index.htm"
html_text = requests.get(url).text 
soup = BeautifulSoup(html_text,features="html.parser")
button = soup.find('ul',class_ ="dropdown-menu SearchBar-keywordSearch" ) .find_all('a')
n = 0
basic_url_nps = "https://www.nps.gov"
for a in button:
    x = a['href'].split("/")[2]
    dicti[x] = basic_url_nps + a['href']
#ark_list
#or values in dicti.items:
#   url= values
#   html_text = requests.get(url).text 
#    soup = BeautifulSoup(html_text,features="html.parser")
#    newlink = soup.find('li',class_ = 'clearfix').find_all('a')
    #or a in newlink:
        
class NationalSite():
    def __init__(self, typ, name, desc, url=None):
        self.type = typ
        self.name = name
        self.description = desc
        self.url = url
        
    def set_address(self):
        parkdata = data.get(self.url)
        parksoup = BeautifulSoup(parkdata, features = "html.parser")
        address_info = parksoup.find_all("div", class_ = "mailing-address")
        for addr in address_info:
            try: 
                street = addr.p.find("span", class_ = "street-address")
                city = addr.p.find("span", attrs = {'itemprop':'addressLocality'})
                state = addr.p.find("span", class_ = "region")
                zip = addr.p.find("span", class_ = "postal-code")
                self.address_street = street.text.strip("\n")
                self.address_city = city.text.strip("\n")
                self.address_state = state.text.strip("\n")
                self.address_zip = zip.text.strip()
            except:
                self.address_street = "street not found"
                self.address_city = "city not found"
                self.address_state = "state not found"
                self.address_zip = "zipcode not found"
                
            
    
    def __str__(self):
        return "{} ({}): {}, {}, {} {}".format(self.name,self.type,self.address_street,self.address_city,self.address_state,self.address_zip)
    
    def set_lat_and_lng(self,lat,lng):
        self.lat = lat
        self.lng = lng
## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class NearbyPlace():
    def __init__(self, name, lat, lng):
        self.name = name
        self.lat = lat
        self.lng = lng
        self.location = "{}, {}".format(lat,lng)
    def __str__(self,name,typ,desc):
        return self.name
        
## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov
def get_sites_for_state(state_abbr):
    state_page = dicti[state_abbr]
    html_text = requests.get(state_page).text
    all_parks_obj = []
    soup = BeautifulSoup(html_text,features="html.parser")
    all_parks = soup.find(class_="clearfix").find_all("div")
    for park in all_parks:
        name = park.find('a').string
        try:
            type = park.find('h2').string
        except:
            type = 'type not found'
        desc = park.find('p').string
        smallurl = park.find('a').get('href')
        parkurl = "https://www.nps.gov" + smallurl + "index.htm"
        new_park = NationalSite(type, name, desc, parkurl)
        new_park.set_address()
        all_parks_obj.append(new_park)
    return all_parks_obj


## Must return the list of NearbyPlaces for the specifite NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list
def get_nearby_places_for_site(national_site):
    pass

## Must plot all of the NationalSites listed for the state on nps.gov
## Note that some NationalSites might actually be located outside the state.
## If any NationalSites are not found by the Google Places API they should
##  be ignored.
## param: the 2-letter state abbreviation
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_sites_for_state(state_abbr):
    lat_vals = []
    lon_vals = []
    text_vals = []
    
    park_list = get_sites_for_state(state_abbr)
    for park in park_list:
        park_location = get_place_geometry(park)
        if park_location != None:
            lat_vals.append(park_location[1])
            lon_vals.append(park_location[2])
            text_vals.append(park_location[0])
    
    
    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v
    

    lat_axis = [min_lat -1, max_lat + 1]
    lon_axis = [min_lon - 1, max_lon + 1]

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    data = [ dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = lon_vals,
            lat = lat_vals,
            text = text_vals,
            mode = 'markers',
            marker = dict(
                size = 20,
                symbol = 'star',
                color = "rgb(126,15, 126)",
            )
            )]


    layout = dict(
            title = 'National Sites in {}'.format(state_abbr),
            geo = dict(
                scope='usa',
                projection=dict( type='albers usa' ),
                lataxis = dict(range = lat_axis),
                lonaxis = dict(range = lon_axis),
                showland = True,
                landcolor = "rgb(239, 219, 135)",
                showlakes = True,
                lakecolor = "rgb(59, 155, 252)",
                subunitcolor = "r(100, 100, 100)",
                center = {'lat': center_lat, 'lon': center_lon },
                countrycolor = "rgb(217, 100, 217)",
                countrywidth = 3,
                subunitwidth = 3,
            ),
        )

    fig = dict( data=data, layout=layout )
    py.plot( fig, validate=False, filename='National Sites in {}'.format(state_abbr) )




## Must plot up to 20 of the NearbyPlaces found using the Google Places API
## param: the NationalSite around which to search
## returns: nothing
## side effects: launches a plotly page in the web browser
def get_sites_for_state(state_abbr):
    return []

def get_nearby_places_for_site(national_site):
    return []

def main():
    last_step = {}
    user_input = input(
        '''
Please input your command:

- list <stateabbr>
- nearby <result_number>
- map
- help
- exit

''')
        
    if "list" in user_input:
            state_name_input = user_input.split()[1]
            if state_name_input in dicti.keys():
                print ("Getting sites for you! Please wait...")
                site_list = get_sites_for_state( state_name_input)
                site_dict={}
                count = 1
                print("******************************")
                print("These are all the sites in {}".format(user_input))
                print("******************************")
                for site in site_list:
                    site_dict[count] = site
                    print('{}) {}'.format(count,site.name))
                    count += 1
                last_step = {}
                last_step = site_dict
            else:
                print("******************************")
                print ("Wrong input, please input again")
            print("******************************")
    
    elif "nearby" in user_input:
            print("******************************")
    
    elif user_input == 'map':
            print("******************************")
        
    elif user_input == 'help':
            print ('Those commands are:')
            print(
'''
- list <stateabbr>
e.g. list MI
This will tell you all the national parks in this state!

- nearby <result_number>
e.g. nearby 2
This will show you a list of all the nearby places

- map
e.g. map
This will show the current result(if any) in the format of map

- exit
exits the program
'''
            )
            print("******************************")
        
    elif user_input == 'exit':
            print ("Exiting")
            print("******************************")
            exit()


    else:
        print('Wrong input, please input again')
        print("******************************")


    user_lst = get_sites_for_state(user_input)
    for item in user_lst:
        print(item)

main()
