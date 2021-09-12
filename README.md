# Letsgotravel
[https://letsgotravel-capstone.herokuapp.com/]


## Description

Letsgotravel is created for travelers who are looking for their next adventure. The application allows the user to lookup countries and their basic information such as capital, population, currency, region, native name, and languages. The user can also create travel bucketlists and view other users' travel plans. The application requires the user to create an account and log in in order to create new lists and add/remove countries.

### REST APIs
* Rest countries API
Returns json containing information about a country.
    URL: [https://restcountries.eu/rest/v2/name/]
    Method: GET
    URL Params: 
    Required: 
        * country=[string]

* Pixabay API
Returns json containing a link to the image.
    URL: [https://pixabay.com/api/]
    Method: GET
    Query Params: 
    Required:
        * key=[string]
        * q=[string]
    Optional:
        * image_type=[string]
        * per_page=[integer]
        * category=[string]


