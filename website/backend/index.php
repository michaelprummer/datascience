<!DOCTYPE html>
<head>
    <script src="../js/jquery.js"></script>
</head>

<body>

<?php


//print_r($db->select('SELECT ID FROM objects WHERE ID = ?', array(0), array('%d')));
?>


<h3>Database Setup</h3>
<button onclick="SetupDB();">Setup Database</button>


<script type="text/javascript">
    function SetupDB() {
        $.ajax({
            url: 'api/Api.php',
            data: {action: 'setup'},
            type: 'post',
            success: function (output) {
                //alert(output);
            }
        });
    }
</script>


<h3>File Import</h3>


<form action="" method="post" enctype="multipart/form-data">
    Select Twitter CSV file:<br>
    <input type="file" name="fileToUpload" id="fileToUpload">
    <input type="submit" value="Import" name="submit">
</form>
<?php
function info($t)
{
    echo "<p>" . $t . "</p>";
}

function twitter_encode($s){
    return urlencode($s);
    ///utf8_encode
}

if (isset($_POST["submit"])) {
    if (isset($_FILES["fileToUpload"]["tmp_name"])) {
        echo "File: " . $_FILES["fileToUpload"]["name"] . ($_FILES["fileToUpload"]["size"] / 1024) . " Kb<br />";
        $filePath = $_FILES["fileToUpload"]["tmp_name"];
    } else {
        info("Can't read file.");
    }

}

if (file_exists($filePath)) {
    $handle = fopen($filePath, "r");

    if ($handle) {

        $max = 100;

        while (($line = fgets($handle)) !== false && $max > 0):
            $parts = preg_split("/[\t]/", $line);
            $max--; ?>
            <script type="text/javascript">
                $.ajax({
                    url: 'api/Api.php',
                    data: {
                        action: "addTweet",
                        time: "<?php echo ($parts[2]);?>",
                        username: "<?php echo ($parts[1]);?>",
                        content: "<?php echo ($parts[3]);?>",
                        lola: "<?php echo ($parts[4]);?>",
                        location: "<?php echo twitter_encode($parts[5]);?>"
                    },
                    type: 'post',
                    success: function (output) {
                        console.log(output);
                    }
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



?>




</body>


