<?php
/**
 * Rest api
 */
require_once("DB.php");
define("DB_NAME", "datascience");
$db = check_db();


if(isset($_POST['action'])) {

    $action = $_POST['action'];

    switch($action) {
        case 'setup':  database_setup();
            break;

        case 'remove': database_remove();
            break;

        case 'clear':  database_clear();
            break;

        case 'addTweet':
            add_tweet($_POST['time'], $_POST['username'], $_POST['tweetId'], $_POST['content'],$_POST['latitude'], $_POST['longitude'],$_POST['location']);
            break;
    }

}

function check_db(){
    global $db;

    if(!$db){
        $db = new DB('root', '', null);
        $db -> select_db(DB_NAME);
    }

    return $db;
}

function database_remove() {
    global $db;
    $result = $db -> query_bool("DROP DATABASE ". DB_NAME . ";");
    echo $result==1?"OK":"FAILED";
}

function database_clear() {
    global $db;
    $result = $db -> query_bool("TRUNCATE TABLE tweets;");
    echo $result==1?"OK":"FAILED";
}

function database_setup() {
    global $db;

    $table = "CREATE TABLE Tweets (
        id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        time int(10),
        username VARCHAR(30) NOT NULL,
        twitter_id VARCHAR(30) NOT NULL,
        content VARCHAR(255),
        latitude DECIMAL(10, 8) NOT NULL,
        longitude  DECIMAL(11, 8) NOT NULL,
        location VARCHAR(30)
    )";

    $r = $db -> query_bool($table);
    echo $r==1?"OK":"FAILED";
}

function add_tweet($time, $username, $tID, $content, $latitude, $longitude, $location){
    global $db;
    //$db = check_db();
    $timestamp = strtotime($time);

    $insert = "INSERT INTO `" . DB_NAME . "`.`tweets` (`id`, `time`, `username`, `twitter_id`, `content`, `latitude`, `longitude`, `location`) VALUES (NULL, '$timestamp', '$username', '$tID', '$content', '$latitude', '$longitude', '$location');";

    $db -> query_bool($insert);
    //return $reult;
}

?>
