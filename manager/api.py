
import pandas as pd
from geopy.geocoders import Nominatim
from manager import strings
import datetime


data = pd.read_csv('./caso_full.csv.gz', compression='gzip')
pd.set_option('display.max_columns', None)
data.head()

geolocator = Nominatim(user_agent="covidbot")
#print(data.query(" city == 'Bagé' & date == '2020-03-19'"))

def get_from_brazil():
    
    date = datetime.datetime.now()
    redu_date=0
   
    state_query_total = data.query(f"place_type== 'state' & date == '{date.strftime('%Y-%m-%d')}'")
    
    while state_query_total.empty:
        #if q is null retry until last date in dataframe\\
        redu_date +=1
        date =datetime.datetime.now() - datetime.timedelta(redu_date)
        

        state_query_total = data.query(f"place_type== 'state' & date == '{date.strftime('%Y-%m-%d')}'")
        
        if redu_date ==10:
            return 'registros para sua localização não encontrado nos ultimos 10 dias'
    else:
     
        return strings.text_br_resume.format(
        # gambiarra to invert date
        datetime.datetime.strptime(f"{state_query_total.iloc[0]['date']}", "%Y-%m-%d").strftime('%d-%m-%Y'),
        # sum total data in states collun for create a country datas
        state_query_total['new_confirmed'].sum(),
        state_query_total['last_available_confirmed'].sum(),
        state_query_total['new_deaths'].sum(),
        state_query_total['last_available_deaths'].sum(),
        )

def city_retun(city):
    '''pega como parametro os dados do GPS (Longitude e latitude) do bot e returna uma sting com os dados filtrados por cidade '''
    
    #get location from longitude
    try:
     location = geolocator.reverse(city, timeout=60)
    except:
        return 'Ocorreu um erro em sua localização tente mais tarde...'
   
    try:
     cityy = location.raw['address']['city']
    except:
     cityy = location.raw['address']['town']


    state = strings.list_uf[location.raw['address']['state']]

    date = datetime.datetime.now()
    redu_date=0
    city_query = data.query(f"state== '{state}' & city == '{cityy}' & date == '{date.strftime('%Y-%m-%d')}' ")
    state_query = data.query(f"place_type== 'state' & state == '{state}' & date == '{date.strftime('%Y-%m-%d')}' ")

    while city_query.empty:
        #if q is null retry until last date in dataframe\\
        redu_date +=1
        date =datetime.datetime.now() - datetime.timedelta(redu_date)
        city_query = data.query(f"state== '{state}' & city == '{cityy}' & date == '{date.strftime('%Y-%m-%d')}' ")
        state_query = data.query(f"place_type== 'state' & state == '{state}' & date == '{date.strftime('%Y-%m-%d')}'")
        
    
        # if dont date in last 10 days
        if redu_date ==10:
            return 'registros para sua localização não encontrado nos ultimos 10 dias'
    else:
        
        return strings.text_city_resume.format(city_query.iloc[0]['city'],
        #gambiarra for inverter date string
        datetime.datetime.strptime(f"{city_query.iloc[0]['date']}", "%Y-%m-%d").strftime('%d-%m-%Y') ,
        #datas from city
        city_query.iloc[0]['new_confirmed'] if not city_query.iloc[0]['is_repeated'] else 'Não ouve divulgação de dados até a hora dessa coleta neste dia',
        city_query.iloc[0]['last_available_confirmed'],
        city_query.iloc[0]['new_deaths'] if not city_query.iloc[0]['is_repeated'] else 'Não ouve divulgação de dados até a hora dessa coleta neste dia',
        city_query.iloc[0]['last_available_deaths'],
        #datas from state
        state_query.iloc[0]['state'],
        state_query.iloc[0]['new_confirmed'] if not state_query.iloc[0]['is_repeated'] else 'Não ouve divulgação de dados até a hora dessa coleta neste dia',
        state_query.iloc[0]['last_available_confirmed'],
        state_query.iloc[0]['new_deaths'] if not state_query.iloc[0]['is_repeated'] else 'Não ouve divulgação de dados até a hora dessa coleta neste dia',
        state_query.iloc[0]['last_available_deaths']
        )
        

        


        #print(city_query.iloc[0]['last_available_deaths'])
        #print(state_query.iloc[0])

        
    
        
            
       
           

  
#print(city_retun('-31.327530, -54.109661'))
#print(get_from_brazil())




# location = geolocator.reverse("-31.327530, -54.109661")
# print(location.raw['address']['city'])
# print(strings.list_uf[location.raw['address']['state']])

