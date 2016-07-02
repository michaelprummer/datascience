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

if(isset($_GET['action'])) {

    $action = $_GET['action'];

    switch($action) {
        case 'getTweets':
            get_tweets($_GET['type'], $_GET['cluster_id']);
            break;

        case 'getClusters':
            get_clusters($_GET['location'], $_GET['date'],  $_GET['type']);
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

    $tweetTable = "CREATE TABLE Tweets (
        tweetID BIGINT(20),
        nmfID VARCHAR(30),
        ldaID VARCHAR(30),
        kmeansID VARCHAR(30),
        latitude DECIMAL(10, 8) NOT NULL,
        longitude  DECIMAL(11, 8) NOT NULL,
        text VARCHAR(140)
    )";

    $clusterTable = "CREATE TABLE Clusters (
        clusterID INT(8) PRIMARY KEY,
        ctype VARCHAR(10),
        terms VARCHAR(255) NOT NULL,
        cdate VARCHAR(63) NOT NULL,
        country VARCHAR(63) NOT NULL
    )";


    $r = $db -> query_bool($tweetTable);
    $r = $db -> query_bool($clusterTable);

    echo $r==1?"OK":"FAILED";
}

function add_tweet($time, $username, $tID, $content, $latitude, $longitude, $location){

    global $db;
    //$db = check_db();
    $timestamp = strtotime($time);

    $insert = "INSERT INTO `" . DB_NAME . "`.`tweets` (`tweetId`, `time`, `username`, `twitter_id`, `content`, `latitude`, `longitude`, `location`) VALUES (NULL, '$timestamp', '$username', '$tID', '$content', '$latitude', '$longitude', '$location');";

    $db -> query_bool($insert);
}


function get_clusters($location, $date, $algo){

    global $db;

    $query = "SELECT clusterID, terms FROM clusters WHERE country='".$location."' AND cdate='".$date."' AND ctype='".$algo."'";
    $result = $db -> query($query);

    if (sizeof($result) > 0) {
        $arr = [];
        $inc = 0;

        foreach ($result as $row) {
            $jsonArrayObject = (array(
                'id' => $row->clusterID,
                'terms' => $row->terms
            ));
            $arr[$inc] = $jsonArrayObject;
            $inc++;
        }
        $json_array = json_encode($arr);
        echo $json_array;
    }
    else{
        echo "0 results";
    }
}

function get_tweets($algo, $clusterID){

    global $db;

    $query = "SELECT latitude, longitude, text, tweetID FROM tweets WHERE ".$algo."ID='".$clusterID."'";
    // $query = "SELECT latitude, longitude, twitter_id FROM tweets WHERE clusterID='".$clusterID."'";
    $result = $db -> query($query);

    if (sizeof($result) > 0) {
        $arr = [];
        $inc = 0;

        foreach ($result as $row) {
            $jsonArrayObject = (array(
            'type' => 'Feature',
            'geometry'=>array(
                'type'=>'Point',
                'coordinates' => array($row->longitude, $row->latitude)
                ),
            'properties'=> array(
                'text'=> $row->text,
                'id'=>$row->tweetID
                )
            ));
            $arr[$inc] = $jsonArrayObject;
            $inc++;
        }
        $json_array = json_encode($arr);
        echo $json_array;
    }
    else{
        echo "0 results";
    }
}

?>
