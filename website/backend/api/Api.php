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

            add_tweet($_POST['tweetID'], $_POST['kmeansID'], $_POST['nmfID'], $_POST['lda_tfidfID'], $_POST['latitude'], $_POST['longitude'], $_POST['text']);
            //add_tweet($_POST['time'], $_POST['username'], $_POST['tweetId'], $_POST['content'],$_POST['latitude'], $_POST['longitude'],$_POST['location']);
            break;

        case 'addCluster':
            //add_tweet($_POST['time'], $_POST['username'], $_POST['tweetId'], $_POST['content'],$_POST['latitude'], $_POST['longitude'],$_POST['location']);
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

    $tweetTable = "CREATE TABLE Tweets (
        id INT(8) PRIMARY KEY,
        tweetID INT(8),
        kmeansID VARCHAR(30),
        nmfID VARCHAR(30),
        lda_tfidfID VARCHAR(30),
        latitude DECIMAL(10, 8) NOT NULL,
        longitude  DECIMAL(11, 8) NOT NULL,
        text VARCHAR(140)
    )";

    $clusterTable = "CREATE TABLE Clusters (
        clusterID INT(8) PRIMARY KEY,
        type INT (4),
        terms VARCHAR(255) NOT NULL,
        date VARCHAR(63) NOT NULL,
        country VARCHAR(63) NOT NULL
    )";


    $r = $db -> query_bool($tweetTable);
    $r = $db -> query_bool($clusterTable);

    echo $r==1?"OK":"FAILED";
}

function add_cluster($clusterID, $type, $terms, $date, $country){
    global $db;
    $insert = "INSERT INTO `clusters`(`clusterID`, `type`, `terms`, `date`, `country`) VALUES ('$clusterID', '$type', '$terms', '$date', '$country')";
    $db -> query_bool($insert);
}

function add_tweet($tweetID, $kmeans, $nmf, $lda, $lat, $lng, $text){
    global $db;
    $insert = "INSERT INTO `tweets`(`tweetID`, `kmeansID`, `nmfID`, `lda_tfidfID`, `latitude`, `longitude`, `text`) VALUES ('$tweetID', '$kmeans','$nmf', '$lda', '$lat', '$lng', '$text')";
    $db -> query_bool($insert);
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
