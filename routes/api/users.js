var express = require('express');
var router = express.Router();
const usersController = require('../../controllers/api/usersController');
const { check, validationResult, body } = require('express-validator');

const fs = require('fs');
const path = require('path');

//const authenticationMiddleware = require('../../middleware/api/authentication');

// router.get('/',authenticationMiddleware, usersController.list);
// router.post('/login',usersController.login);
// router.get('/:id',authenticationMiddleware,usersController.find);

// NEW MEMBERS 
//router.get('/register', usersController.register);
router.post('/register', [
    check('password').isLength({min:5}).withMessage('Password must contain more than 5 characters'),
    check('email').isEmail().withMessage('Invalid email address'),
    body('email').custom(function(value){
      const usersFilePath = path.join(__dirname, '../../data/users.json');
      const users = JSON.parse(fs.readFileSync(usersFilePath, 'utf-8'));
      for(let i=0; i<users.length; i++){
        if(users[i].email === value){
          return false;
        }
      }
      return true;
    }).withMessage('User is already in our database'),
  ], usersController.register);

// CURRENT USERS
//router.get('/login', usersController.login);
router.post('/login', usersController.login);

router.get('/logout',usersController.logout);

// USERS DASHBOARD 
//router.get('/account', usersController.account);

//router.get('/account/update', usersController.update);
router.post('/account/update', usersController.storeUpdate);


module.exports = router;