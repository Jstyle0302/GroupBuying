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
  var total_products = []
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
  // console.log(items)
  for (var i in items) {
    var year = items[i].fields.year;
    var month = items[i].fields.month;
    var sales = items[i].fields.sales;
    var expense = items[i].fields.expense;
    // for bar chart
    var product_sales = JSON.parse(items[i].fields.productSales)
    var product_names = Object.keys(product_sales)
    for (var i in product_names) {
      if (!total_products.includes(product_names[i])) {
        total_products.push(product_names[i])
      }
    }
    // for line chart
    lineChart[month][1] += sales;
    lineChart[month][2] += expense;
  }
  drawLineChart(lineChart);
  drawBarChart(total_products, items)
}

// google.js
google.charts.load('current', {'packages':['corechart','bar']});
// google.charts.setOnLoadCallback(drawLineChart);

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


google.charts.load('current', {'packages':['bar']});
google.charts.setOnLoadCallback(drawBarChart);

function drawBarChart(total_products, items) {
  var keys = Object.keys(total_products);
  var result = [[], [], [], []] // one quarter

  for (var i = 0; i < result.length; i ++) {
    for (var j = 0; j < keys.length + 1; j++) {
      result[i].push(0)
    }
  }  
  result[0].fill(100)
  result[1].fill(200)
  result[2].fill(300)
  result[3].fill(0)
  result[0][0] = "Jan"
  result[1][0] = "Feb"
  result[2][0] = "Mar"
  result[3][0] = "Apr"

  var product_idx_dict = {}
  var data = new google.visualization.DataTable();
  data.addColumn('string','Month');

  for (var i = 0; i < keys.length; i ++ ) {
    tmp_name = total_products[i]
    product_idx_dict[tmp_name] = parseInt(i + 1)
    data.addColumn('number', tmp_name);
  }
  // console.log(product_idx_dict)

  for (var i in items) {
    var month = parseInt(items[i].fields.month);
    var product_sales = JSON.parse(items[i].fields.productSales)
    var product_names = Object.keys(product_sales)
    for (var i = 0; i < product_names.length; i++) {
      var idx = parseInt(product_idx_dict[product_names[i]])
      result[month - 1][idx] += parseInt(product_sales[product_names[i]])
    }
  }
  // console.log(result)
  data.addRows(result)

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