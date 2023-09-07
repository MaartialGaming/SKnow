function updateTendinaSectorsNames (data, name_locality, name_slope){
    if (data.length >0 ){
         var updatedTableBody = '<ul class="nav navbar-nav"><li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#">Sectors Available<span class="caret"></span></a><ul class="dropdown-menu">';
         for (var i = 0; i < data.length; i++) {
            var sectorName = data[i];
             console.log(sectorName);
            
             //updatedTableBody += "<li><a id=" + localityName + " href='#titolo_kit' onClick='getData(" + localityName + "')'>";
             updatedTableBody += "<li><a id=sector" + i + " href='#dashboard' onClick='selectedSector(" + i + ",\"" + name_locality + "\",\"" + name_slope+"\")'>";
             updatedTableBody += sectorName;
            //updatedTableBody +=" - "+stato;
            updatedTableBody +='</a></li>';
         
         }
         updatedTableBody+="</ul></li></ul>"
        $("#sectors_list_container").html(updatedTableBody);
    }
    else{
        $("#sectors_list_container").html("<span>Sorry! NO Sectors AVAILABLE</span>");
    }        

}


