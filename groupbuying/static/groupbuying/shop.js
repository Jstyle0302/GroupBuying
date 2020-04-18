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