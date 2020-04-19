/* Start for shop.html */
$('#list-tab a').on('click', function (e) {
    e.preventDefault()
    $(this).tab('show')
  })

// Tag
function filterFunction() {
  var input, filter, ul, li, a, i;
  input = document.getElementById("myInput");
  filter = input.value.toUpperCase();
  div = document.getElementById("myDropdown");
  a = div.getElementsByTagName("a");
  for (i = 0; i < a.length; i++) {
    txtValue = a[i].textContent || a[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      a[i].style.display = "";
    } else {
      a[i].style.display = "none";
    }
  }
}


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
  var id = button.attr('id')
  var modal = $(this)
  modal.find('#modal-menu-name input').val(name);
  modal.find('#modal-menu-id').val(id);
})

$('#vendorModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget)
  var name = button.data('whatever')
  var id = button.attr('id')
  var modal = $(this)
  modal.find('#modal-vendor-name input').val(name);
  modal.find('#modal-vendor-id').val(id);
})

// Sends a new request to update the to-do list
function getStatistic() {
  $.ajax({
      url: "/groupbuying/get_statistic_json",
      dataType : "json",
      success: updateStatistic
  });
}

function updateStatistic(items) {
  // Removes the old to-do list items
  // console.log(items)
  // var json_data = items
  // var result = [];
  var lineChart = [
    ['Month', 'Sales', 'Expenses'],
    ['Jan',  200,      100],
    ['Feb',  300,      200],
    ['Mar',  400,      300],
    ['Apr',  0,      0],
    ['May',  0,      0],
    ['Jun',  0,      0],
    ['Jul',  0,      0],
    ['Aug',  0,      0],
    ['Sep',  0,      0],
    ['Oct',  0,      0],
    ['Nov',  0,      0],
    ['Dec',  0,      0]];

  for (var i in items) {
    var year = items[i].fields.year;
    var month = items[i].fields.month;
    var sales = items[i].fields.sales;
    var expense = items[i].fields.expense;
    lineChart[month][1] += sales;
    lineChart[month][2] += expense;
  }
  drawLineChart(lineChart);

}

// google.js
google.charts.load('current', {'packages':['corechart','bar']});
google.charts.setOnLoadCallback(drawLineChart);

function drawLineChart(arr) {
  // var data = google.visualization.arrayToDataTable([
  //   ['Month', 'Sales', 'Expenses'],
  //   ['Jan.',  1000,      400],
  //   ['Feb.',  1170,      460],
  //   ['Mar.',  660,       1120],
  //   ['Apr.',  1030,      540]
  // ]);
  var data = google.visualization.arrayToDataTable(arr)

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
    ['Month', 'Coffee', 'Tea', 'Cake'],
    ['Jan.', 1000, 400, 200],
    ['Feb.', 1170, 460, 250],
    ['Mar.', 660, 1120, 300],
    ['Apr.', 1030, 540, 350]
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
window.onload = getStatistic;