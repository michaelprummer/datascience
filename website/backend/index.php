<?php
    require_once("db/DB.php");
    $db = new DB('root', '', 'test');


//print_r($db->select('SELECT ID FROM objects WHERE ID = ?', array(0), array('%d')));
?>


<script>

    $.ajax({ url: '/my/site',
        data: {action: 'test'},
        type: 'post',
        success: function(output) {
            alert(output);
        }
    });
</script>