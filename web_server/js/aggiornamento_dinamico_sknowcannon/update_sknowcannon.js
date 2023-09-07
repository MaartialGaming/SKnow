
function updateTitle(username){
    console.log("Username arrivato" + username)
    $("#nome_utente_tendina").html(username);
    $("#welcome_name").html("Hello!");
}



function get_list_localities() {
    console.log("FAccio la query");
    $.ajax(
        {
            url: '/edit/getLocalities', //QUI NON CI VA USER ID -> mettilo lato server gettando i cookies
            method: 'GET',
            contentType: "application/json",
            dataType: "json",
            success: function (risposta) {
                var dati = risposta.data;  // ho aggiunto . data perche il format è application.json quindi deve entrare un json per forza
                console.log("QUESTE SONO LE LOCALITA: "+ dati);
                updateTendinaLocalitiesNames(dati);
            },
        }
    );
}

function getSlopes(id_kit) {

    //METTI TUTTE LE REQUEST DELLE CARD
    //PER QUANTO RIGUARDA I GRAFICI PUOI PRENDERE ID DEL KIT DALL H3 -> #titolo_kit.innerHTML

    var section = document.getElementById("da_nascondere");
    section.classList.remove("nascondi");

    var section_sector = document.getElementById("da_nascondere2");
    section_sector.classList.add("nascondi");

    var dashboard_div = document.getElementById("dashboard_generale");
    dashboard_div.classList.add("nascondi");


    var titolo = document.getElementById(id_kit).innerText

    $("#locality_selected").html("Locality selected: " + titolo);
    $("#id_locality").html(titolo);
    $("#codice_locality").html(id_kit);
    $("#overall_id_to_vis").html("Select all the fields above to proceed");
    $("#slope_selected").html("No Slope selected");

    $.ajax(
        {
            url: '/edit/getSlopesByLocalityName', //QUI NON CI VA USER ID -> mettilo lato server gettando i cookies
            method: 'GET',
            contentType: "application/json",
            data: "loc="+titolo,
            dataType: "json",                           // qui si identifica il file che arriva come risposta alla query fatta
            success: function (risposta) {
                var dati = risposta.data; // ho aggiunto . data perche il format è application.json quindi deve entrare un json per forza
                updateTendinaSlopesNames(dati, titolo);
            },
        }
    );


}
function getSectors(slope, name_locality) {

    //METTI TUTTE LE REQUEST DELLE CARD
    //PER QUANTO RIGUARDA I GRAFICI PUOI PRENDERE ID DEL KIT DALL H3 -> #titolo_kit.innerHTML

    var section = document.getElementById("da_nascondere2");
    section.classList.remove("nascondi");

    var section_sector = document.getElementById("da_nascondere3");
    section_sector.classList.add("nascondi");

    var name_slope = document.getElementById("slopes"+slope).innerText

    $("#slope_selected").html("Slope selected:  " + name_slope);
    $("#id_slope").html(name_slope);
    $("#codice_slope").html(slope);
    $("#overall_id_to_vis").html("Select all the fields above to proceed");
    $("#titolo_sector_selected").html("No Sector selected: ");

    $.ajax(
        {
            url: '/edit/getSectorsBySlopeNameByLocalityName', //QUI NON CI VA USER ID -> mettilo lato server gettando i cookies
            method: 'GET',
            contentType: "application/json",
            data: "loc=" + name_locality + "&slo=" + name_slope,
            dataType: "json",                           // qui si identifica il file che arriva come risposta alla query fatta
            success: function (risposta) {
                var dati = risposta.data;
                updateTendinaSectorsNames(dati, name_locality, name_slope);
            },
        }
    );


}
function selectedSector(sector) {

    //METTI TUTTE LE REQUEST DELLE CARD
    //PER QUANTO RIGUARDA I GRAFICI PUOI PRENDERE ID DEL KIT DALL H3 -> #titolo_kit.innerHTML

    var section = document.getElementById("da_nascondere3");
    section.classList.remove("nascondi");

    var dashboard_div = document.getElementById("dashboard_generale");
    dashboard_div.classList.remove("nascondi");

    var titolo = document.getElementById("sector" + sector).innerText
    var slope = document.getElementById("id_slope").innerText;
    var loc = document.getElementById("id_locality").innerText;


    $("#titolo_sector_selected").html("Sector selected: "+titolo);
    $("#id_sector").html(titolo);
    $("#codice_sector").html(sector);

    $("#overall_id_to_vis").html(loc+ " - " + slope+ " - "+ titolo);



    /* CHIAMA QUI LE FUNZIONI PER I GRAFICI*/

    renderCards(loc, slope, titolo);

    renderSdHist(loc, slope, titolo, 12);
    renderTempHist(loc, slope, titolo, 12);
    renderHumHist(loc, slope, titolo, 12);

}

function renderCards(loc, slope, sec){

    var filter = 1;
    var uri_f1 = "/data_v2/getMeasureCard?loc="+loc+"&slo="+slope+"&sec="+sec+"&ns="+filter+"&measure=field1";

    var uri_f2 = "/data_v2/getMeasureCard?loc="+loc+"&slo="+slope+"&sec="+sec+"&ns="+filter+"&measure=field2"; //CAMBIARE IL FIELD
    
    var uri_f3= "/data_v2/getMeasureCard?loc="+loc+"&slo="+slope+"&sec="+sec+"&ns="+filter+"&measure=field3"; // CAMBIARE IL FIELD
  
    $.ajax(
        {
        url: uri_f1, 
        method: 'GET',
        contentType: "application/json",
        dataType: "json",
        success: function(risposta){
            console.log("field1 card data: " + risposta.data)
            if (risposta.data.length > 0) {
                $("#rt_snow_depth_val").html(risposta.data[0][0] + " mm");
            }
        },
        }
    );

    $.ajax(
        {
        url: uri_f2, 
        method: 'GET',
        contentType: "application/json",
        dataType: "json",
        success: function(risposta){
            console.log("field2 card data: " + risposta.data)
            if (risposta.data.length > 0) {
            $("#rt_temperature_val").html(risposta.data[0][0] + " °C");
            }
        },
        }
    );

    $.ajax(
        {
        url: uri_f3, 
        method: 'GET',
        contentType: "application/json",
        dataType: "json",
        success: function(risposta){
            console.log("field3 card data: " + risposta.data)
            if (risposta.data.length > 0) {
            $("#rt_humidity_val").html(risposta.data[0][0] + " %");
            }
        },
        }
    );
}

function updateCards() {
    var titolo = document.getElementById("id_sector").innerText;
    var slope = document.getElementById("id_slope").innerText;
    var loc = document.getElementById("id_locality").innerText;
    renderCards(loc, slope, titolo);
}

function renderGraphByFilter(filter){
    //retreive loc, slope, sector
    var titolo = document.getElementById("id_sector").innerText
    var slope = document.getElementById("id_slope").innerText;
    var loc = document.getElementById("id_locality").innerText;

    renderSdHist(loc, slope, titolo, filter);
    renderTempHist(loc, slope, titolo, filter);
    renderHumHist(loc, slope, titolo, filter);



}


/*
function show_add_locality() {
    var section = document.getElementById("nascondere_add_locality");
    section.classList.remove("nascondi");
}*/




function show_add_slope() {
    var section = document.getElementById("nascondere_add_slope");
    section.classList.remove("nascondi");
}

/*function add_slope() {
    locality_name = "ddddd";
    event.preventDefault();
    name_slope = document.getElementById('new_slope_name').value

    console.log(name_slope)

    $.ajax(
        {
            url: '/edit/addSlopeToLocality', //QUI NON CI VA USER ID -> mettilo lato server gettando i cookies
            method: 'POST',
            contentType: "application/json",
            data: JSON.stringify({
                name: name_slope,
                locality: locality_name

            }),
            dataType: "json",                           // qui si identifica il file che arriva come risposta alla query fatta
            success: function (risposta) {
                var dati = risposta;
            },
        }
    );

}*/

function showPopup_new_locality(locality_name) {
    locality_name = locality_name || "Add a locality to your network";
    
    console.log("popup aperto");
    var popup = document.getElementById("popup");
    popup.style.display = "block";


    $("#popup_title").html(locality_name);
}

function delete_locality() {

    var locality_name = document.getElementById("id_locality").innerText;
    var uri_locality = 'delete/locality?loc='+locality_name;
    $.ajax(
        {
            url: uri_locality,
            method: 'DELETE',
            contentType: "application/json",
            dataType: "json",
            success: function (risposta) {
                console.log(risposta.esito);
                get_list_localities();
                $("#locality_selected").html("No Locality Selected")
                var slope_section = document.getElementById("da_nascondere");
                slope_section.classList.add("nascondi");
                var sector_section = document.getElementById("da_nascondere2");
                sector_section.classList.add("nascondi");
                var dashboard_section = document.getElementById("dashboard_generale");
                dashboard_section.classList.add("nascondi");
                $("#overall_id_to_vis").html("Select all the fields above to proceed");
                alert("Locality: " + locality_name + " deleted from the network");
            },
        }
    );
}

function hidePopup_new_locality() {
    console.log("popup chiuso");
    var popup = document.getElementById("popup");
    popup.style.display = "none";

    // capire come metterlo dentro il success per avere sempre l'aggiornamento corretto
    console.log("prima del metodo");
    get_list_localities();
    console.log("aggiunta la pista, aggiorno l'elenco");

    var section = document.getElementById("confirm_add_locality");
    section.classList.remove("nascondi");

    var section = document.getElementById("status_add_locality");
    section.classList.add("nascondi");

    var input_text = document.getElementById('new_locality_name')
    input_text.readOnly = false;
}

function add_locality() {

    event.preventDefault();
    name_locality = document.getElementById('new_locality_name').value

    console.log(name_locality);

    $.ajax(
        {
            url: '/edit/addLocality', //QUI NON CI VA USER ID -> mettilo lato server gettando i cookies
            method: 'POST',
            contentType: "application/json",
            data: JSON.stringify({
                name: name_locality
            }),
            dataType: "txt",                           // qui si identifica il file che arriva come risposta alla query fatta
            success: function (risposta) {
                console.log(risposta);

            },
        }
    );
    var section = document.getElementById("confirm_add_locality");
    section.classList.add("nascondi");

    var section = document.getElementById("status_add_locality");
    section.classList.remove("nascondi");

    var input_text = document.getElementById('new_locality_name')
    input_text.readOnly = true;

}


function add_slope() {

    event.preventDefault();
    var name_slope = document.getElementById('new_slope_name').value
    var name_locality= document.getElementById("id_locality").innerText;
    console.log("sono dentro add slope")
    console.log(name_locality);
    console.log(name_slope);

    $.ajax(
        {
            url: '/edit/addSlopeToLocality',
            method: 'POST',
            contentType: "application/json",
            data: JSON.stringify({
                name: name_slope,
                locality : name_locality
            }),
            dataType: "txt",                           // qui si identifica il file che arriva come risposta alla query fatta
            success: function (risposta) {
                console.log(risposta);

            },
        }
    );
    var section = document.getElementById("confirm_add_slope");
    section.classList.add("nascondi");

    var section = document.getElementById("status_add_slope");
    section.classList.remove("nascondi");

    var input_text = document.getElementById('new_slope_name')
    input_text.readOnly = true;

}


function showPopup_new_slope(locality_name) {
    locality_name = locality_name || "Add a new slope";
    
    console.log("popup aperto");
    var popup = document.getElementById("popup2");
    popup.style.display = "block";


    $("#popup_title2").html(locality_name);
}

function delete_slope() {

    var locality_name = document.getElementById("id_locality").innerText;
    var locality_code = document.getElementById("codice_locality").innerText;
    var name_slope = document.getElementById("id_slope").innerText;
    var uri_slope = 'delete/slope?loc='+locality_name+'&slo='+name_slope;
    $.ajax(
        {
            url: uri_slope,
            method: 'DELETE',
            contentType: "application/json",
            dataType: "json",
            success: function (risposta) {
                console.log(risposta.esito);
                getSlopes(locality_code);
                alert("Slope " + name_slope + " deleted from " + locality_name);
            },
        }
    );
}

function hidePopup_new_slope() {
    console.log("popup chiuso");
    var popup = document.getElementById("popup2");
    popup.style.display = "none";

    // capire come metterlo dentro il success per avere sempre l'aggiornamento corretto
    console.log("prima del metodo");
    var code_locality= document.getElementById("codice_locality").innerText;
    getSlopes(code_locality);
    console.log("aggiunta la pista, aggiorno l'elenco");

    var section = document.getElementById("confirm_add_slope");
    section.classList.remove("nascondi");

    var section = document.getElementById("status_add_slope");
    section.classList.add("nascondi");

    var input_text = document.getElementById('new_slope_name')
    input_text.readOnly = false;
}


function add_sector() {

    event.preventDefault();
    var name_sector = document.getElementById('new_sector_name').value
    var name_locality= document.getElementById("id_locality").innerText;
    var name_slope = document.getElementById("id_slope").innerText;

    console.log("sono dentro add sector")
    console.log(name_locality);
    console.log(name_slope);
    console.log(name_sector);

    $.ajax(
        {
            url: '/edit/addSectorToSlopeToLocality',
            method: 'POST',
            contentType: "application/json",
            data: JSON.stringify({
                name: name_sector,
                locality : name_locality,
                slope: name_slope
            }),
            dataType: "txt",                           // qui si identifica il file che arriva come risposta alla query fatta
            success: function (risposta) {
                console.log(risposta);

            },
        }
    );
    var section = document.getElementById("confirm_add_sector");
    section.classList.add("nascondi");

    var section = document.getElementById("status_add_sector");
    section.classList.remove("nascondi");

    var input_text = document.getElementById('new_sector_name')
    input_text.readOnly = true;
}


function showPopup_new_sector(locality_name) {
    locality_name = locality_name || "Add a new sector";
    
    console.log("popup aperto");
    var popup = document.getElementById("popup3");
    popup.style.display = "block";


    $("#popup_title3").html(locality_name);
}

function delete_sector() {

    var locality_name = document.getElementById("id_locality").innerText;
    var name_slope = document.getElementById("id_slope").innerText;
    var code_slope = document.getElementById("codice_slope").innerText;
    var name_sector = document.getElementById("id_sector").innerText;
    var uri_sector = 'delete/sector?loc='+locality_name+'&slo='+name_slope+'&sec='+name_sector;
    $.ajax(
        {
            url: uri_sector,
            method: 'DELETE',
            contentType: "application/json",
            dataType: "json",
            success: function (risposta) {
                console.log(risposta.esito);
                getSectors(code_slope, locality_name);
                var dashboard_section = document.getElementById("dashboard_generale");
                dashboard_section.classList.add("nascondi");
                alert("Sector " + name_sector + " deleted from " + name_slope);
            },
        }
    );
}

function hidePopup_new_sector() {
    console.log("popup chiuso");
    var popup = document.getElementById("popup3");
    popup.style.display = "none";

    // capire come metterlo dentro il success per avere sempre l'aggiornamento corretto
    console.log("prima del metodo");
    var name_locality= document.getElementById("id_locality").innerText;
    var code_slope = document.getElementById("codice_slope").innerText;

    getSectors(code_slope, name_locality);
    console.log("aggiunta il settore, aggiorno l'elenco");

    var section = document.getElementById("confirm_add_sector");
    section.classList.remove("nascondi");

    var section = document.getElementById("status_add_sector");
    section.classList.add("nascondi");

    var input_text = document.getElementById('new_sector_name')
    input_text.readOnly = false;
}




//sidebar TOGGLE
var sidebarOpen = false;
var sidebar = document.getElementById("sidebar");

function openSidebar() {
    if(!sidebarOpen){
        sidebar.classList.add("sidebar-responsive");
        sidebarOpen= true;
    }
}

function closeSidebar(){
    if(sidebarOpen){
        sidebar.classList.remove("sidebar-responsive");
        sidebarOpen= false;
    }
}

function openUserCard() {
  const userCard = document.querySelector('.user-card');
  userCard.style.display = userCard.style.display === 'block' ? 'none' : 'block';
}

function logout() {
  // Implementa qui il codice per il logout dell'utente
  const userCard = document.querySelector('.user-card');
  userCard.style.display = 'none';
  $.ajax(
    {
        url: "/logout" , //DEVI METTERE ID
        method: 'GET',
        contentType: "application/json",
        dataType: "json",
        success: function(risposta){	
        var dati = risposta.canceled;
        console.log(dati)
        if (dati =="true") {
            window.location.href= "/"
        }
        
        },
    }
);
}






