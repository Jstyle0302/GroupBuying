// Active tab via url
$(function(){
  var url = window.location.href;
  var activeTab = url.substring(url.indexOf("#") + 1);
  var target = $("#" + activeTab);
  if (target.length == 1) {
    $(".tab-pane").removeClass("active in");
    target.addClass("active in");
    $('a[href="#'+ activeTab +'"]').tab('show');
  }
});

// Buttons for add or minus product.
function addProduct(id) {
  var target = $("#"+id.toString())
  var currentValue = parseInt(target.val())
  target.val(currentValue+1)
}

function minusProduct(id) {
  var target = $("#"+id.toString())
  var currentValue = parseInt(target.val())
  if (currentValue - 1 > 1) {
    target.val(currentValue-1)
  } else {
    target.val(1)
  }
}