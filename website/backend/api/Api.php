<?php
/**
 * Rest api
 */
require_once("DB.php");
define("DB_NAME", "datascience");
$db = check_db();



/*
 * Update CLuster queries for phpmyadmin
UPDATE t , (SELECT DISTINCT nmfID, tweetId FROM t WHERE nmfID > 0) b
SET t.nmfID = b.nmfID
WHERE t.tweetId = b.tweetId AND t.nmfID = -1

UPDATE t , (SELECT DISTINCT ldaID, tweetId FROM t WHERE ldaID > 0) b
SET t.ldaID = b.ldaID
WHERE t.tweetId = b.tweetId AND t.ldaID = -1

UPDATE t , (SELECT DISTINCT kmeansID, tweetId FROM t WHERE kmeansID > 0) b
SET t.kmeansID = b.kmeansID
WHERE t.tweetId = b.tweetId AND t.kmeansID = -1
*/


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
            add_tweet(
                $_POST['tweetID'],
                $_POST['nmfID'],
                $_POST['ldaID'],
                $_POST['kmeansID'],
                $_POST['longitude'],
                $_POST['latitude'],
                $_POST['tweettext']);
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
//596067684011397121	0	-1	-1	48.815616	 2.379703	"@SneakersAddict_: Nike Air Max 90 Hyperfuse â€˜Independence Dayâ€™ Red http://t.co/wFkPtOnTC3"
function add_tweet($tweetID, $nmfID, $ldaID, $kmeansID, $longitude, $latitude, $tweettext){
    global $db;

    // INSERT INTO `tweets`(`tweetID`, `nmfID`, `ldaID`, `kmeansID`, `latitude`, `longitude`, `text`) VALUES ([value-1],[value-2],[value-3],[value-4],[value-5],[value-6],[value-7])
    //die($tweetID . " | " .  $nmfID . " | " . $ldaID . " | " . $kmeansID . " | " . $longitude . " | " . $latitude . " | " . $tweettext);

    $insert = "INSERT INTO `tweets`(`tweetID`, `nmfID`, `ldaID`, `kmeansID`, `latitude`, `longitude`, `text`) VALUES ($tweetID, $nmfID, $ldaID, $kmeansID, $longitude, $latitude, '$tweettext')";
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
        $tweet_arr = [];
        $i = 0;

        foreach ($result as $row) {
            $tweet_arr[$i] = array(
                'type' => 'Feature',
                'geometry'=>array(
                    'type'=>'Point',
                    'coordinates' => array($row->longitude, $row->latitude)
                ),
                'properties'=> array(
                    'text'=> utf8_encode($row->text),
                    'id'=>$row->tweetID
                ),
            );

            $i++;
        }

        echo json_encode($tweet_arr);
    }
    else{
        echo "0 results";
    }
}

?>
