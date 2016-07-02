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
    <h3>File Import</h3>
    <form action="" method="post" enctype="multipart/form-data">
        Number of Tweets:<br>
        <input type="number" value="30" name="numOfTweets">
        <input type="file" name="fileToUpload" id="fileToUpload">
        <input type="submit" value="Import" name="submit">
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
if (isset($_POST["submit"])) {
    if (isset($_FILES["fileToUpload"]["tmp_name"])) {
        echo "File: " . $_FILES["fileToUpload"]["name"] . ($_FILES["fileToUpload"]["size"] / 1024) . " Kb<br />";
        $filePath = $_FILES["fileToUpload"]["tmp_name"];

        if (file_exists($filePath)) {
            $handle = fopen($filePath, "r");

            if ($handle) {

                $algo = "kmeans";

                $max = isset($_POST['numOfTweets'])?($_POST['numOfTweets']+1):100;

                while (($line = fgets($handle)) !== false && $max > 0):
                    $parts = preg_split("/[\t]/", $line);
                    //die(print_r($parts));
                    $max--;

                    ?>

                    <script type="text/javascript">
                        $.ajax({
                            url: 'api/Api.php',
                            data: {
                                action: "addTweet",
                                id: "<?php echo ($parts[1]); ?>",
                                cluster_ID: "<?php echo ($parts[0]); ?>",
                                latitude: "<?php echo ($parts[2]); ?>",
                                longitude: "<?php echo ($parts[3]); ?>",
                                text: "<?php echo twitter_encode($parts[4]); ?>",
                                algo: "<?php echo $algo; ?>"
                            },
                            type: 'post'
                            /*,success: function (output) {
                                console.log(output);
                            }
                            */
                        });
                    </script>

                    <?php
                endwhile;

                fclose($handle);
            } else {
                info("Error opening the file.");
            }
        } else {
            info("Path wrong!");
        }

    } else {
        info("Can't read file.");
    }

}
?>
</body>


