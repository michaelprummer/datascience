<?php
    require_once("db/DB.php");
    $db = new DB('root', '', 'test');


//print_r($db->select('SELECT ID FROM objects WHERE ID = ?', array(0), array('%d')));
?> 