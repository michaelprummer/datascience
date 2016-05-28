<?php
/**
 * Rest api
 */

if(isset($_POST['action'])) {
    $action = $_POST['action'];

    switch($action) {
        case 'setup':  test(); break;
    }

}

function test(){
    echo "Hi!";
}



?>