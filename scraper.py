from bs4 import BeautifulSoup
import requests
import numpy as np

# Some functions to convert strings to dates and numbers

def getDate(text):
    return np.datetime64(text.strip())

def getCase(num):
    return int(num.replace(',' , ''))
 
# Downloading the html file

source = requests.get('https://www.canada.ca/en/public-health/services/diseases/2019-novel-coronavirus-infection/health-professionals/epidemiological-summary-covid-19-cases.html#a2').text

soup = BeautifulSoup(source, 'lxml')

# Extracting the table -- my process is extremely ad-hoc and should be simplified later....

data = [] # This will be the table
k = 0 # Counter for the amount of times the table has been found

for table in soup.find_all('table',class_='table table-bordered'):    
    if table.thead.tr.th.text == 'Onset dateFootnote 1' and k < 1:
        k += 1
        body = table.tbody
    
        for row in table.tbody.findAll('tr'):
            entry = []
            for element in row.findAll('td'):
                entry.append(element.text)
            data.append(entry)
    else:
        pass

# Cleaning up the data    

dates = []
cases = []

for item in data:
    dates.append( getDate(item[0]) )
    cases.append( getCase(item[1]) )

# Plotting and fitting the data

#Slight rework needed so that the dates are well comprehended by numpy and matplotlib

from scipy import optimize
import matplotlib.pyplot as plt

x = range(len(cases))

def logi(t, K, t0, r):
    y = K / (1 + np.exp( -r * (t-t0) ))
    return y

popt, pcov = optimize.curve_fit(
    logi,
    x,cases,
    p0 = [2000, 50, 1],
    sigma = np.zeros(len(cases))+50, absolute_sigma=True
)

perr = np.sqrt( np.diag(pcov) )

plt.bar(x,cases,label='Reported Cases')

x_plot = np.linspace(9,90,180)
plt.plot(x_plot,logi(x_plot,*popt), 'r', label='Logistic Regression')
plt.legend()
plt.xlim((20,90))
plt.xlabel('Days')
plt.ylabel('Number of reported cases')
plt.title('Expected number of total confirmed cases is: '+str(round(popt[0]))+' +/- '+str(round(perr[0])) ) 
txt="Data was retrieved on: "+ str(dates[-1])
plt.figtext(0.5, 0, txt, wrap=True, horizontalalignment='center', fontsize=12)

plt.show()