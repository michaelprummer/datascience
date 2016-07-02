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
            add_tweet($_POST['id'], $_POST['cluster_ID'], $_POST['latitude'],$_POST['longitude'], $_POST['text'], $_POST['algo']);
            break;
    }

}

if(isset($_GET['action'])) {

    $action = $_GET['action'];

    switch($action) {
        case 'getTweets':
            get_tweets($_GET['location']);
            //get_tweets($_GET['clusterID']);
            break;

        case 'getClusters':
            get_clusters($_GET['location'], $_GET['date']);
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

    $table = "CREATE TABLE Tweets1 (
        id INT(6) UNSIGNED PRIMARY KEY,
        kmeans_ID int(6),
        nmf_ID int(6),
        latitude DECIMAL(10, 8) NOT NULL,
        longitude DECIMAL(10, 8) NOT NULL,
        text VARCHAR(255)
    )";

    $r = $db -> query_bool($table);
    echo $r==1?"OK":"FAILED";
}

function add_tweet($id, $cluster_ID, $latitude, $longitude, $text, $algo){

    global $db;
    //$db = check_db();
    //$timestamp = strtotime($time);

    $insert = "INSERT INTO `" . DB_NAME . "`.`tweets1` (`id`, `".$algo."_ID`,`latitude`, `longitude`, `text`) VALUES ('$id', '$cluster_ID', '$latitude', '$longitude', '$text');";
    echo $insert;
    $r = $db -> query_bool($insert);
    echo $r==1?"OK":"FAILED";
}


function get_clusters($location, $date){

    global $db;

    $query = "SELECT clusterID, terms FROM clusters WHERE country='".$location."' AND date='".$date."'";
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

function get_tweets($location){

    global $db;

    $query = "SELECT latitude, longitude, twitter_id FROM tweets WHERE location='".$location."'";
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
                'text'=> $row->twitter_id
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
