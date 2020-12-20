const fs = require('fs');
const path = require('path');
var {check, validationResult, body} = require('express-validator');

const usersFilePath = path.join(__dirname, '../../data/users.json');
const users = JSON.parse(fs.readFileSync(usersFilePath, 'utf-8'));

const usersController = {
    login : (req, res) => {
        if(req.body.email){
            let userLogin = users.find(user => {
                return user.email === req.body.email;
            })
            if(userLogin !== undefined){
                if(req.body.password === userLogin.password){
                    res.status(200).json({
                        message : 'User Logged In'
                    });
                }
                else{
                    res.status(403).json({
                        message : 'User or password incorrect.'
                    });
                }
            }else{
                res.status(403).json({
                    message : 'User or password incorrect.'
                });
            }
        }else{
            res.status(403).json({
                message : 'User or password incorrect.'
            });
        }
    },
    register : (req, res) => {
        const errors = validationResult(req);

        if(errors.isEmpty()){
            let newId = users.length + 1;
            let newUser = {
                id: newId,
                name : req.body.firstName,
                lastName : req.body.lastName,
                email: req.body.email,
                password: req.body.password,
                birth: req.body.birth
            }

            const newUsers = [...users, newUser];
            fs.writeFileSync(usersFilePath, JSON.stringify(newUsers, null, ' '));
            
            res.status(201).json({
                message : 'User created'
            });
        }else{
            // return res.render('register',{
            //     errors:errors.errors,
            //     title:'Modas Emilse | Login'
            // })
            res.status(403).json({
                errors : errors.errors,
            });
        }
    },
    update : (req, res) => {
        res.send('Update');
    },
    storeUpdate : (req, res) => {
        res.send('StoreUpdate')
    },
    account : (req, res) => {
        res.send('Account');
    },
    logout: (req, res) => {
        res.send('Log Out')
    }
}

module.exports = usersController;