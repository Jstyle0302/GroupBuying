$('#list-menu a').on('click', function (e) {
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
$("i").click(function(e){
    var target = $(e.target);
    // console.log(target)
    modalContext.append(getModal())
    modal.style.display = "block";
});

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
    var contextForm = `<form>
    <div class="form-row">
      <div class="form-group col-6">
        <label for="name">Name</label>
        <input type="text" class="form-control" id="name" placeholder="Name">
      </div>
      <div class="form-group col-6">
        <label for="price">Price</label>
        <input type="text" class="form-control" id="price" placeholder="Price">
      </div>
    </div>
    <div class="form-group">
      <label for="description">Description</label>
      <textarea class="form-control" id="description" rows="3"></textarea>
    </div>
    <div class="form-group">
      <label for="image">Image</label>
      <input type="file" class="form-control-file" id="image">
    </div>
    <button type="submit" class="btn btn-primary">Submit</button>
  </form>`
  return contextForm;
}

