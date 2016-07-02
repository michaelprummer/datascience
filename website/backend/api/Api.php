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
        case 'addCluster':
            add_cluster($_POST['id'], $_POST['type'], $_POST['terms'],$_POST['day'], $_POST['country']);
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

    $table = "CREATE TABLE tweets (
        id BIGINT(20) UNSIGNED PRIMARY KEY,
        kmeans_ID int(6),
        nmf_ID int(6),
        latitude DECIMAL(10, 8) NOT NULL,
        longitude DECIMAL(10, 8) NOT NULL,
        text VARCHAR(255)
    )";

    $r = $db -> query_bool($table);
    echo $r==1?"OK":"FAILED";

    $table = "CREATE TABLE clusters (
        id INT(10) UNSIGNED PRIMARY KEY,
        type VARCHAR(10),
        terms VARCHAR(255),
        day int(10),
        country VARCHAR(255)
    )";

    $r = $db -> query_bool($table);
    echo $r==1?"OK":"FAILED";
}

function add_tweet($id, $cluster_ID, $latitude, $longitude, $text, $algo){

    global $db;
    //$db = check_db();

    $query = "SELECT id FROM tweets WHERE id='".$id."'";
    $result = $db -> query($query);

    if (sizeof($result) > 0) {
       $insert = "UPDATE `" . DB_NAME . "`.`tweets` SET `".$algo."_ID`='$cluster_ID' WHERE id='$id'";
    }
    else{
       $insert = "INSERT INTO `" . DB_NAME . "`.`tweets` (`id`, `".$algo."_ID`,`latitude`, `longitude`, `text`) VALUES ('$id', '$cluster_ID', '$latitude', '$longitude', '$text');";
    }

    $r = $db -> query_bool($insert);
    echo $r==1?"OK":"FAILED";
}

function add_cluster($id, $type, $terms, $day, $country){

    global $db;
    //$db = check_db();

    $insert = "INSERT INTO `" . DB_NAME . "`.`clusters` (`id`, `type`,`terms`, `day`, `country`) VALUES ('$id', '$type', '$terms', '$day', '$country');";

    $r = $db -> query_bool($insert);
    echo $r==1?"OK":"FAILED";
}


function get_clusters($location, $date, $algo){

    global $db;

    $query = "SELECT id, terms FROM clusters WHERE country='".$location."' AND day='".$date."' AND type='".$algo."'";
    $result = $db -> query($query);

    if (sizeof($result) > 0) {
        $arr = [];
        $inc = 0;

        foreach ($result as $row) {
            $jsonArrayObject = (array(
                'id' => $row->id,
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

    $query = "SELECT latitude, longitude, text, id FROM tweets WHERE ".$algo."_ID='".$clusterID."'";
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
                'id'=>$row->id
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
