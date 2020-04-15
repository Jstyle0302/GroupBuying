
/* Start for shop.html */
$('#list-tab a').on('click', function (e) {
    e.preventDefault()
    $(this).tab('show')
  })

// Get the modal
$('#dishModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget)
  var id = button.data('whatever')
  var modal = $(this)

  var name = $("#product-name-".concat(id)).text();
  var price = $("#product-price-".concat(id)).text();
  var description = $("#product-description-".concat(id)).text();
  modal.find('#modal-name input').val(name);
  modal.find('#modal-price input').val(price);
  modal.find('#modal-description textarea').val(description);
  modal.find('#modal-id').val(id);
})

$('#menuModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget)
  var name = button.data('whatever')
  var id = button.data('id')
  var modal = $(this)
  modal.find('#modal-menu-name input').val(name);
  modal.find('#modal-menu-id').val(id);
})

$('#vendorModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget)
  var name = button.data('whatever')
  var id = button.data('id')
  var modal = $(this)
  modal.find('#modal-vendor-name input').val(name);
  modal.find('#modal-vendor-id').val(id);
})

// google.js
google.charts.load('current', {'packages':['corechart','bar']});
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
    height: 300,
    width: 800
  };

  var chart = new google.visualization.LineChart(document.getElementById('statistics_line'));

  chart.draw(data, options);
}


// google.charts.load('current', {'packages':['bar']});
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
    bars: 'vertical', // Required for Material Bar Charts.
    height: 300,
    width: 800
  };

  var chart = new google.visualization.ColumnChart(document.getElementById('statistics_bar'));

  chart.draw(data, google.charts.Bar.convertOptions(options));
}


// google.charts.load('current', {'packages':['corechart']});
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
    legend: {position:'labeled',alignment:'end'},
    height: 500,
    width: 800
  };

  var chart = new google.visualization.PieChart(document.getElementById('statistics_pie'));

  chart.draw(data, options);
}

/* End for shop.html */