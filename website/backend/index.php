<!DOCTYPE html>
<head>
    <script src="../js/jquery.js"></script>
    <script src="js/setup.js"></script>
    <link href="style.css" rel="stylesheet">
</head>
<body>

<div class="box">
    <h3>Database Setup</h3>
    <button onclick="SetupDB();">Create DB</button>
    <button onclick="ClearDB();">Clear Tables</button>
    <button onclick="RemoveDB();">Remove DB</button>
</div>
<div class="box">
    <h3>Cluster Import</h3>
    <form action="" method="post" enctype="multipart/form-data">
        Number of Tweets:<br>
        <input type="number" value="30" name="numOfTweets">
        <input type="file" name="fileToUpload" id="fileToUpload">
        <input type="submit" value="ImportCluster" name="ImportCluster">
    </form>
</div>
<div class="box">
    <h3>Tweet Import</h3>
    <form action="" method="post" enctype="multipart/form-data">
        Number of Tweets:<br>
        <input type="number" value="5" name="numOfTweets">
        <input type="file" name="fileToUpload" id="fileToUpload">
        <input type="submit" value="ImportTweet" name="ImportTweet">
    </form>
</div>

<?php

/**
 * Print with html
 */
function info($t){
    echo "<p>" . $t . "</p>";
}

/**
 * Clear data
 */
function twitter_encode($s){
    return trim(preg_replace('/ +/', ' ', preg_replace('/[^A-Za-z0-9 ]/', ' ', urldecode(html_entity_decode(strip_tags($s))))));
    //return addslashes($s);
    ///utf8_encode
}

/**
 * Import csv data
 */
if (isset($_POST["ImportTweet"])) {
    if (isset($_FILES["fileToUpload"]["tmp_name"])) {
        echo "File: " . $_FILES["fileToUpload"]["name"] . ($_FILES["fileToUpload"]["size"] / 1024) . " Kb<br />";
        $filePath = $_FILES["fileToUpload"]["tmp_name"];

        if (file_exists($filePath)) {
            $handle = fopen($filePath, "r");

            if ($handle) {

                //$max = isset($_POST['numOfTweets'])?($_POST['numOfTweets']+1):100;

                while (($line = fgets($handle)) !== false /*&& $max > 0*/):
                    $parts = preg_split("/[\t]/", $line);
                    //$max--;

                    ?>
                    <script type="text/javascript">
                        $.ajax({
                            url: 'api/Api.php',
                            data: {
                                action: "addTweet",
                                tweetID: "<?php echo $parts[1]; ?>",
                                kmeansID: "<?php echo $parts[0]; ?>",
                                nmfID: "",
                                lda_tfidfID: "",
                                latitude: "<?php echo $parts[2]; ?>",
                                longitude: "<?php echo $parts[3]; ?>",
                                //text: "<?php //echo twitter_encode($parts[4]); ?>"
                                text: ""
                            },
                            type: 'post'
                        });
                    </script>

                    <?php
                endwhile;

                fclose($handle);
            }
        }
    }

}
?>
</body>


