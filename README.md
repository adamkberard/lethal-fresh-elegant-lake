This is a project for an interview process.

Swagger UI documentation here: http://lethal-fresh-elegant-lake.herokuapp.com/swagger/
Redoc UI documentation here: http://lethal-fresh-elegant-lake.herokuapp.com/redoc/


When POSTing pizza orders, the endpoint will accept either single pizza orders, OR a list of pizza orders

Example.
/order/ accepts both of these formats

{
    'Flavor': 'Hawaii',
    'Size': 'Large',
    'Crust': 'Thin'
}

OR

[
    {
        'Flavor': 'Hawaii',
        'Size': 'Large',
        'Crust': 'Thin'
    },
    {
        'Flavor': 'Regina',
        'Size': 'Medium',
        'Crust': 'Thin'
    },
    ...
]

It will return with either the single finalized pizza order if only sent one, or a list of the 
finalized pizza orders if sent a list. This isn't super clear in the documentation.


When running the server, both the SECRET_KEY and the SALT environment variables must be set.
These are set as environment variables to keep them out of version control and maintain the
security of the API.