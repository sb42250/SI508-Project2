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

####get url
def params_unique_combination(baseurl, params_d, private_keys=["api_key"]):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}={}".format(k, params_d[k]))
    return baseurl + "&".join(res)
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
        self.typ = typ
        self.name = name
        self.description = desc
        self.url = url
    def set_address(self):
        parkdata = data.get(self.url)
        if parkdata is None:
            resp = requests.get(self.url,1)
            #print("i")
            parkdata = resp.text
            data.set(self.url,parkdata)
        parksoup = BeautifulSoup(parkdata, features = "html.parser")
        address_info = parksoup.find_all("div", class_ = "mailing-address")
        #print(address_info)
        for addr in address_info:
            #print(addr)
            try: 
                street = addr.p.find("span", class_ = "street-address")
                city = addr.p.find("span", attrs = {'itemprop':'addressLocality'})
                state = addr.p.find("span", class_ = "region")
                zipp = addr.p.find("span", class_ = "postal-code")
                self.address_street = street.text.strip("\n")
                self.address_city = city.text.strip("\n")
                self.address_state = state.text.strip("\n")
                self.address_zip = zipp.text.strip()
            except:
                self.address_street = "street not found"
                self.address_city = "city not found"
                self.address_state = "state not found"
                self.address_zip = "zipcode not found"
        return self.name,self.typ,self.address_street,self.address_city,self.address_state,self.address_zip     
            
    
    def __str__(self):
        return "'{}' ('{}'): '{}', '{}', '{}' '{}'".format(self.name,self.typ,self.address_street,self.address_city,self.address_state,self.address_zip)
    
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
    all_parks_obj = []
    resp_text = data.get(state_abbr)
    if resp_text is None:
        resp = requests.get(dicti[state_abbr])
        resp_text = json.loads(resp.text)
        data.set(state_abbr,resp_text)
    
    soup = BeautifulSoup(resp_text,features="html.parser")
    all_parks = soup.find(id="list_parks").find_all("div",{"class":"col-md-9"})
    #print(all_parks)
    for park in all_parks:
        name = park.find('a').string
        try:
            typ = park.find('h2').string
        except:
            typ = 'type not found'
        desc = park.find('p').string
        parkname = park.find('a').get('href')
        parkurl = "https://www.nps.gov" + parkname + "index.htm"
        new_park = NationalSite(typ, name, desc, parkurl)
        #print(new_park)
        #print(new_park.set_address())
        all_parks_obj.append(new_park)
    return all_parks_obj

def get_place_geo(national_site):
    baseurl = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?'
    params_diction = {}
    params_diction["key"] = google_places_key
    params_diction["input"] = national_site.name
    params_diction["inputtype"] = 'textquery'
    params_diction['fields'] = 'geometry'
    unique_ident_place = params_unique_combination(baseurl,params_diction)
    place_data = data.get(unique_ident_place)
    if place_data is None:
        resp = requests.get(baseurl, params_diction)
        resp_text = json.loads(resp.text)
        data.set(unique_ident_place,resp_text)
    place_data = eval(place_data)
    latitude = place_data['candidates'][0]['geometry']['location']['lat']
    longitude = place_data['candidates'][0]['geometry']['location']['lng']
    national_site.set_lat_and_lng(latitude,longitude)
    return(national_site.name,latitude,longitude)

    
def change_tuple_to_str(tuple):
    string = str(tuple[1])+','+ str(tuple[2])
    return string
## Must return the list of NearbyPlaces for the specifite NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list
def get_nearby_places_for_site(national_site):
    nearby_lst = []
    baseurl_nearby = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    params_diction_nearby = {}
    params_diction_nearby["key"] = google_places_key
    if get_place_geo(national_site) is None:
        params_diction_nearby["location"] = change_tuple_to_str(get_place_geo(national_site))
        params_diction_nearby['radius'] = 10000
        unique_ident_nearby = params_unique_combination(baseurl_nearby,params_diction_nearby)
        data_nearby = data.get(unique_ident_nearby)
        if data_nearby is None:
            resp2 = requests.get(baseurl_nearby, params_diction_nearby)
            data_nearby= json.loads(resp2.text)
            data.set(unique_ident_nearby,data_nearby,1)
        try:
            for place in data_nearby['results']:
                lat = place['geometry']['location']['lat']
                lng = place['geometry']['location']['lng']
                nearby_lst.append(NearbyPlace(place['name'],lat,lng))
            return nearby_lst
        except:
            return nearby_lst
    else:
        return nearby_lst

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
    #remove empty sites
    park_list = get_sites_for_state(state_abbr)
    for park in park_list:
        park_location = get_place_geo(park)
        if park_location != None:
            lat_vals.append(park_location[1])
            lon_vals.append(park_location[2])
            text_vals.append(park_location[0])
            # print(park_location)

    #get actual plot

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


def plot_nearby_for_site(site_object):
    big_lat_vals = []
    big_lon_vals = []
    big_text_vals = []
    small_lat_vals = []
    small_lon_vals = []
    small_text_vals = []
    # try:
    nearby_lst = get_nearby_places_for_site(site_object)
    big_lat_vals.append(site_object.lat)
    big_lon_vals.append(site_object.lng)
    big_text_vals.append(site_object.name)
    for nearby in nearby_lst:
        if nearby != None:
            small_lat_vals.append(nearby.lat)
            small_lon_vals.append(nearby.lng)
            small_text_vals.append(nearby.name)

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in big_lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in big_lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    lat_axis = [min_lat - 1, max_lat + 1]
    lon_axis = [min_lon - 1, max_lon + 1]

    center_lat = (max_lat + min_lat) / 2
    center_lon = (max_lon + min_lon) / 2

    nationalsites = dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = big_lon_vals,
        lat = big_lat_vals,
        text = big_text_vals,
        mode = 'markers',
        marker = dict(
            size = 20,
            symbol = 'star',
            color = "rgb(126,15, 126)",
        ))

    nearbyplaces = dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = small_lon_vals,
        lat = small_lat_vals,
        text = small_text_vals,
        mode = 'markers',
        marker = dict(
            opacity = 0.6,
            size = 8,
            symbol = 'square',
            color = 'red'

        ))

    data = [nationalsites, nearbyplaces]

    layout = dict(
        title = 'Places Near {}'.format(site_object.name),
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
    py.plot(fig, validate=False, filename='Places Near {}'.format(site_object.name) )


def main():
    last = {}
    while True:
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
                #print(state_name_input)
                site_list = get_sites_for_state(state_name_input)
                site_dict={}
                count = 1
                print("******************************")
                print("These are all the sites in {}".format(user_input))
                for site in site_list:
                    site_dict[count] = site
                    print('{}) {}'.format(count,site.name))
                    count += 1
                last = {}
                last = site_dict
                #print(last)
            print("******************************")
    
        elif "nearby" in user_input:
            print("******************************")
            number_input = user_input.split()[1]
            number = int(number_input)
            #print (number_input)
            site = last[number]
            print (site)
            nearby_lst = get_nearby_places_for_site(site)
            for nearby in nearby_lst:
                print(nearby)
                
        elif user_input == 'map':
            print("******************************")
            state_name_input = user_input.split()[1]
            try:
                plot_nearby_for_site(last[int(state_name_input)])
            except:
                plot_sites_for_state(state_name_input)

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
        
        if user_input == 'exit':
            print ("See you next time!")
            print("******************************")
            exit()


main()
