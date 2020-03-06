import time
from bs4 import BeautifulSoup
import requests
import pickle
import random
import pprint


# Make soup function
def make_soup(url_to_get):
    # Request the website
    response = requests.get(url_to_get)

    # Check the return status
    if response.status_code == 200:
        # Make and return the soup
        return BeautifulSoup(response.text, 'html.parser')
    else:
        return None


def get_links(soup_obj):
    # For each page we want to get all the car post listings
    listings_urls = []

    # Car detail URL base; will be used to gather the details of each car post listing
    car_detail_url = 'https://www.cars.com{}'

    # Loop through listing
    for listing in soup_obj.find_all('div', {'class': 'shop-srp-listings__listing-container'}):
        # Get each vehicle's detail url
        vehicle_url = listing.find('a').attrs['href']
        # print(car_detail_url.format(vehicle_url))

        # Save to our master list of car urls
        listings_urls.append(car_detail_url.format(vehicle_url))

    return listings_urls


# Get the data from each post
def get_posts(listings):
    # Now that we have the url's of each listing, we want to capture the data for each car
    # The data model will be: a list of cars, where each car will have several attributes.
    # Model will be executed via list of dictionaries
    # Collect the cars and car details in cars_list master list
    cars_list = []
    for post in listings:
        # Request the URL and make soup
        new_soup = make_soup(post)

        # Check if we're blocked
        if new_soup is None:
            break

        else:
            # Need to get the VIN for each car; this tends not follow the same pattern for each page
            # Pull the unordered list called 'basics'
            # Returns a list of list items
            try:
                basics_list = new_soup.find('ul', {'class': 'vdp-details-basics__list'}).find_all('li', {'class': 'vdp-details-basics__item'})
            except:
                print('Couldnt get the data')

            # Set the VIN variable
            vin = ''

            # Loop through the items in the list and find the VIN
            for list_item in basics_list:
                try:
                    # Split each item by its ':' and check if it contains the vin
                    if 'VIN' in list_item.get_text().strip().split(':'):
                        vin = list_item.get_text().strip().split(':')[1]
                        vin = vin.split(' ')[1]
                except:
                    print("Couldn't get something")

            try:
                # Get the vehicle's other characteristics
                car_attribute = {
                    'model': new_soup.find('h1', {'class': 'cui-heading-2--secondary vehicle-info__title'}).get_text().strip(),
                    'price': new_soup.find('span', {'class': 'vehicle-info__price-display vehicle-info__price-display--dealer cui-heading-2'}).get_text().strip(),
                    'vin': vin,
                    'mileage': new_soup.find('div', {'class': 'vdp-cap-price__mileage--mobile vehicle-info__mileage'}).get_text().strip(),
                    'mpg': new_soup.find_all('li', {'class': 'vdp-details-basics__item'})[4].find('span').get_text().strip(),
                    'color': new_soup.find_all('li', {'class': 'vdp-details-basics__item'})[1].find('span').get_text().strip()
                }

            except:
                print("Couldn't get something")

            # Add the vehicle dict to the master list of cars
            cars_list.append(car_attribute)

            print('Got ' + car_attribute['model'])

        # Set a random time to sleep
        print('Waiting...', '\n')
        time.sleep(random.randint(0, 2))

    # Return the data of cars
    return cars_list


# Start the program
if '__main__' == __name__:
    # url
    url = 'https://www.cars.com/for-sale/' \
          'searchresults.action/?dealerType=all&page={}&perPage=20&rd=30&searchSource=PAGINATION&' \
          'sort=relevance&stkTypId=28881&zc=44113'

    # Vehicle detail url
    detail_url = 'https://www.cars.com{}'

    # Set the max number of pages to scrape
    max_pages = 50

    # Create a master list to hold the cars
    car_master_list = []

    # Loop through each page
    for page in range(1, max_pages + 1):
        # Build the URL for the page
        new_url = url.format(page)

        print('Getting page #{}'.format(page))
        print('Getting page URL {}'.format(new_url))

        # Make the soup for the page/URL
        soup = make_soup(url_to_get=new_url)

        # Error handling
        if soup is None:
            break

        # Get the links to the car postings on that page
        listing_urls = get_links(soup_obj=soup)

        # Get the data from each post; ie go to each car posting and get the data
        cars_data = get_posts(listings=listing_urls)

        # Add the cars data to the master list
        for car_detail in cars_data:
            car_master_list.append(car_detail)

    # Print our results
    # pprint.pprint(cars_data)

    print('Done!')
    pprint.pprint(car_master_list)
    print(len(car_master_list))

    # Pickle the list of cars for later analysis
    with open('cars_data_1.txt', 'wb') as fp:
        pickle.dump(car_master_list, fp)
