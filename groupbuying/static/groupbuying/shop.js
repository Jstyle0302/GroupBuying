
/* Start for shop.html */
$('#list-tab a').on('click', function (e) {
    e.preventDefault()
    $(this).tab('show')
  })

// Get the modal
var modal = document.getElementById("myModal");

// Get the modal context
var modalContext = $("#myModal #context");

// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal
// $(".far.fa-edit.btn").click(function(e){
//     var target = $(e.target);
//     console.log(target)
//     $("#modal-name input").val('Shine')
//     $("#modal-price input").val(1)
//     $("#modal-description textarea").val('Very handsome')
//     // $("#modal-name")
//     // console.log(target)
//     // modalContext.append(getModal())
//     modal.style.display = "block";
// });

function showModal(id) {
  // var target = $(e.target);
    // console.log(target)
    console.log('success')
    var name = $("#product-name-".concat(id)).text();
    var price = $("#product-price-".concat(id)).text();
    var description = $("#product-description-".concat(id)).text();
    $("#modal-name input").val(name);
    $("#modal-price input").val(price);
    $("#modal-description textarea").val(description);
    $("#modal-id").val(id);
    modal.style.display = "block";
}


// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
  modalContext.empty();
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
    modalContext.empty();
  }
}

function getModal() {
    var contextForm = ``
  return contextForm;
}

// google.js
google.charts.load('current', {'packages':['bar']});
google.charts.setOnLoadCallback(drawBarChart);

function drawBarChart() {
  var data = google.visualization.arrayToDataTable([
    ['Year', 'Coffee', 'Tea', 'Cake'],
    ['2014', 1000, 400, 200],
    ['2015', 1170, 460, 250],
    ['2016', 660, 1120, 300],
    ['2017', 1030, 540, 350]
  ]);

  var options = {
    bars: 'horizontal' // Required for Material Bar Charts.
  };

  var chart = new google.charts.Bar(document.getElementById('statistics_bar'));

  chart.draw(data, google.charts.Bar.convertOptions(options));
}

google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawLineChart);

function drawLineChart() {
  var data = google.visualization.arrayToDataTable([
    ['Year', 'Sales', 'Expenses'],
    ['2004',  1000,      400],
    ['2005',  1170,      460],
    ['2006',  660,       1120],
    ['2007',  1030,      540]
  ]);

  var options = {
    curveType: 'function',
    legend: { position: 'bottom' }
  };

  var chart = new google.visualization.LineChart(document.getElementById('statistics_line'));

  chart.draw(data, options);
}

google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawPieChart);

function drawPieChart() {

  var data = google.visualization.arrayToDataTable([
    ['Customers', 'Number'],
    ['Under 20',     11],
    ['21 to 30',      2],
    ['31 to 40',  2],
    ['41 to 50', 2],
    ['Above 51',    7]
  ]);

  var options = {

  };

  var chart = new google.visualization.PieChart(document.getElementById('statistics_pie'));

  chart.draw(data, options);
}

/* End for shop.html */