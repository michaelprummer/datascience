<?php
/**
 * Rest api
 */

require_once("DB.php");
$db = check_db();



if(isset($_POST['action'])) {
    $action = $_POST['action'];

    switch($action) {
        case 'setup':  database_setup(); break;
        case 'addTweet':  add_tweet($_POST['time'], $_POST['username'],$_POST['content'],$_POST['lola'],$_POST['location']); break;
    }

}

function check_db(){
    global $db;
    if(!$db){
        $db = new DB('root', '', null);
        $db -> select_db("DataScience");
    }

    return $db;
}

function database_setup() {
    global $db;

    $table = "CREATE TABLE Tweets (
        id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        time TIMESTAMP,
        username VARCHAR(30) NOT NULL,
        content VARCHAR(255),
        lola VARCHAR(30),
        location VARCHAR(30)
    )";

    $db -> query_bool($table);
}

function add_tweet($time, $username, $content, $lola, $location){
    global $db;
    $db = check_db();

    $insert = "INSERT INTO `datascience`.`tweets` (`id`, `time`, `username`, `content`, `lola`, `location`) VALUES (NULL, '$time', '$username', '$content', '$lola', '$location');";

    echo $db -> query_bool($insert);
}

?>
