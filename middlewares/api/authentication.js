const jwt = require('jsonwebtoken');

const authMiddleware = (req, res, next) => {
    const token = req.headers.token;
    let secret = process.env.JWT_SECRET;

    if(!token){
        res.json({
            msg : "Verification is unsuccessful."
        });
    }else{
        jwt.verify(token, secret, (err, decoded) => {
            if(err){
                res.json({
                    msg : "Invalid token"
                })
            }else{
                req.currentUser = decoded.userLogin;
                next();
            }
        })
    }
}

module.exports =  authMiddleware;