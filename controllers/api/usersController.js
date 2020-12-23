const fs = require('fs');
const path = require('path');
const {check, validationResult, body} = require('express-validator');
const bcrypt = require('bcrypt');

const usersFilePath = path.join(__dirname, '../../data/users.json');
const users = JSON.parse(fs.readFileSync(usersFilePath, 'utf-8'));

const usersController = {
    login : (req, res) => {
        if(req.body.email){
            let userLogin = users.find(user => {
                return user.email === req.body.email;
            })
            if(userLogin !== undefined){
                if(bcrypt.compareSync(req.body.password,userLogin.password)){
                    req.session.currentUser = userLogin;
                    res.status(200).json({
                        msg : 'User Logged In'
                    });
                }
                else{
                    res.status(403).json({
                        msg : 'User or password incorrect.'
                    });
                }
            }else{
                res.status(403).json({
                    msg : 'User or password incorrect.'
                });
            }
        }else{
            res.status(403).json({
                msg : 'User or password incorrect.'
            });
        }
    },
    register : (req, res) => {
        const errors = validationResult(req);

        if(errors.isEmpty()){
            let newId = users.length + 1;
            let accountDefault = {
                available : 5000,
                transactions: {}
            }
            let newUser = {
                id: newId,
                name : req.body.firstName,
                lastName : req.body.lastName,
                email: req.body.email,
                password: bcrypt.hashSync(req.body.password, 10),
                birth: req.body.birth,
                accountData : accountDefault
            }

            const newUsers = [...users, newUser];
            fs.writeFileSync(usersFilePath, JSON.stringify(newUsers, null, ' '));
            
            res.status(201).json({
                msg : 'User created'
            });
        }else{
            res.status(403).json({
                errors : errors.errors,
            });
        }
    },
    update : (req, res) => {
        res.send('Update');
    },
    balanceUpdate : (req, res) => {
        if(req.session.currentUser){
            let userToUpdate = users.find(user => {
                return user.email === req.session.currentUser.email;
            })
            if(userToUpdate != undefined){
                if(req.body.wdw <= userToUpdate.accountData.available){
                    const newUsers = users.map(user =>{
                        if(user.email == userToUpdate.email){
                            user.accountData.available -= req.body.wdw;
                        }
                        req.session.currentUser = user;
                        return user;
                    });
                    fs.writeFileSync(usersFilePath,JSON.stringify( newUsers, null, ' '));
                    res.redirect('/api/account');
                }else{
                    res.json("We can't withdrawal, not enough founds");
                }
            }else{
                res.json(`Internal issue`)
            }
        }else{
            res.json(`Please login to access your information.`)
        }
    },
    account : (req, res) => {
        if(req.session.currentUser){
            const {name, lastName, accountData, email} = req.session.currentUser;
            res.send(`Account Logged: ${name} ${lastName} (${email}) | Available: ${accountData.available}`);
        }else{
            res.json(`Please login to access your information.`)
        }
    },
    logout: (req, res) => {
        if(req.session.currentUser){
            let loggedOut = req.session.currentUser.name;
        
            req.session.destroy();
            res.json(`${loggedOut} is now Log Out`)
        }else{
            res.json(`There aren't current sessions active.`)
        }
    }
}

module.exports = usersController;