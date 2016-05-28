<html>
<head>
    <script src="../js/jquery.js"></script>
</head>

<body>

<?php
    require_once("api/DB.php");
    $db = new DB('root', '', 'test');


//print_r($db->select('SELECT ID FROM objects WHERE ID = ?', array(0), array('%d')));
?>



<button onclick="SetupDB();">Setup Database</button>

<script type="text/javascript">
    function SetupDB(){

        $.ajax({ url: 'api/Api.php',
            data: {action: 'setup'},
            type: 'post',
            success: function(output) {
                //alert(output);
            }
        });

    }
</script>

</body>
</html>