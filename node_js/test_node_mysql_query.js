var mysql = require('mysql');

var con = mysql.createConnection({
  host: "localhost",
  user: "piuser",
  password: "BestPasswordEver",
  database: "project1"
});

con.connect(function(err) {
  if (err) throw err;
  console.log("Connected!");
  var sql = "SELECT * FROM sensors"
  con.query(sql, function (err, result, fields) {
    if (err) throw err;
    console.log(result);
  });
});
