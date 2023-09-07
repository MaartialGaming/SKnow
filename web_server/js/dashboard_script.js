
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

// ------------- CHARTS ------------
var options = {
    series: [{
    data: [400, 430, 448, 470, 540],
    name: "Countries",
  }],
    chart: {
    type: 'bar',
    background: "transparent",
    height: 350
  },
  plotOptions: {
    bar: {
      borderRadius: 4,
      horizontal: false,
    }
  },
  dataLabels: {
    enabled: false
  },
  tooltip: {
    shared:true,
    intersect: false,
    theme:"dark",
  },
  xaxis: {
    categories: ['South Korea', 'Canada', 'United Kingdom', 'Netherlands', 'Italy'],
    title: {
        style: {
            color: "#000000",
        },
    },
    labels: {
        style: {
            colors: "#ffffff",
        }
    }
  },
  yaxis: {
    title: {
        style: {
            color: "#000000",
        },
    },
    labels: {
        style: {
            colors: "#ffffff",
        }
    }
  }
  };

  var barChart = new ApexCharts(document.querySelector("#bar-chart"), options);
  barChart.render();

  // AREA CHART 1

  var areaChartOptions = {
    series: [{
    name: 'TEAM A',
    type: 'area',
    data: [44, 55, 31, 47, 31, 43, 26, 41, 31, 47, 33]
  }, {
    name: 'TEAM B',
    type: 'line',
    data: [55, 69, 45, 61, 43, 54, 37, 52, 44, 61, 43]
  }],
    chart: {
    height: 350,
    type: 'line',
  },
  stroke: {
    curve: 'smooth'
  },
  fill: {
    type:'solid',
    opacity: [0.35, 1],
  },
  labels: ['Dec 01', 'Dec 02','Dec 03','Dec 04','Dec 05','Dec 06','Dec 07','Dec 08','Dec 09 ','Dec 10','Dec 11'],
  markers: {
    size: 0
  },
  yaxis: [
    {
      title: {
        text: 'Series A',
      },
    },
    {
      opposite: true,
      title: {
        text: 'Series B',
      },
    },
  ],
  tooltip: {
    shared:true,
    intersect: false,
    theme:"dark",
  },
  };

  var areaChart = new ApexCharts(document.querySelector("#area-chart"), areaChartOptions);
  areaChart.render();



 