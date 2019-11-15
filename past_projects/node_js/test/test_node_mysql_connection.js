var mysql = require('mysql');

var con = mysql.createConnection({
  host: "localhost",
  user: "piuser",
  password: "BestPasswordEver"
});

con.connect(function(err) {
  if (err) throw err;
  console.log("Connected!");
});
