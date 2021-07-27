# ReactBank (Backend)

#### Description:
<p> Before start getting into my Final Project details, I really want to thank the CS50 Team for the amazing quality of the lectures, each detail was incredible usefull and I will be always remembering all that I learned with you. </p>
<p>David, Doug, Brian, you guys really enjoy teaching and we can feel it with every lecture, thank you for that willingness to share what you know, really appreciate it.</p>
<p> This project was inspired by CS50 Financial practice, I created this FullStack App that uses a ReactJS FrontEnd, also some great technologies such as: Bootstrap, CSS, SCSS and JavaScript. </p>

<p>For the BackEnd, Python Flask BackEnd with the following available end points: </p>

<br>

## GET Endpoints:

- / : Main page with Flask views working as a "docs" web site to understand the API.
- /help : Docs/ information about the API
- /api/ : Shows status of the API
- /api/register : End point to create users.
- /api/login : End point to login users.

## POST Endpoints:
- /api/account : End point to get user data after user are logged in.
- /api/account/transactions : End point to get list of user's transactions.
- /api/account/wdw : End point that allow users to "withdrawal" money from their account.
- /api/account/transfer : End point that allow users to "transfer" money from their account to another (created) account.
- /api/account/deposit : End point that allow users to "deposit" to their account once the current balance is below $250.
- /api/account/update : End point that allow users to update their current password.

## GET/POST Endpoints:
- /api/logout : End point that clears current session and log out users.


I will be updating this app, deployed version will be soon available through :

- FrontEnd : <URL HERE> https://reactbank-front-end.netlify.app/
- BackEnd : <URL HERE> https://reactbank-back-end.herokuapp.com/


# THANK YOU [CS50](https://cs50.harvard.edu/x/2021/) !

## How to use ReactBank Back-End:

1. Clone this repo

    ```bash
        git clone https://github.com/jhonnierandrey/reactbank-bk
    ```

2. Install all the required dependencies requirements.txt using pip .

    ```bash
        pip install -r requirements.txt
    ```

3. To start on your local machine (starts using server.js):

    ```bash
        flask run
    ```

4. OPTIONAL : To start on your local network:

    ```bash
        FLASK_APP=app.py FLASK_ENV=development flask run --port *portnumber* --host=*hostnumber*
    ```

## Contributing

1. Fork it (<https://github.com/jhonnierandrey/reactbank-bk/fork>)
2. Create your own branch (`git checkout -b newFeature/yourIdea`)
3. Commit your changes (`git commit -m 'Add your commit'`)
4. Push to the branch (`git push`)
5. Create a new Pull Request

### References

[Python](https://www.python.org/)
<br>
[Flask](https://palletsprojects.com/p/flask/)

### License

This project is licensed under the MIT License
