<?php

    $it = new filesystemiterator(dirname("./new_update_file/"));
    printf("{ \"NOF_file\" : %d, ", iterator_count($it));

    $i = 0;

    foreach ($it as $fileinfo) {
        echo "\"" .$i. "\" : \"";
        echo $fileinfo->getFilename() . "\" , ";
        $i++;
    }
    echo " \"SUM\" : ".$i." }";
?>