function updateTendinaLocalitiesNames (data){
    if (data.length >0 ){
         var updatedTableBody = '<ul class="nav navbar-nav"><li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#">Localities Available<span class="caret"></span></a><ul class="dropdown-menu">';
         for (var i = 0; i < data.length; i++) {
            var localityName = data[i];
             console.log(localityName);
            
             //updatedTableBody += "<li><a id=" + localityName + " href='#titolo_kit' onClick='getData(" + localityName + "')'>";
             updatedTableBody += "<li><a id=" + i + " href='#titolo_kit' onClick='getSlopes(" + i +")'>";
             updatedTableBody += localityName;
            //updatedTableBody +=" - "+stato;
            updatedTableBody +='</a></li>';
         
         }
         updatedTableBody+="</ul></li></ul>"
        $("#localities_list_container").html(updatedTableBody);
    }
    else{
        $("#localities_list_container").html("<span>Sorry! NO LOCALITIES AVAILABLE</span>");
    }        

}


