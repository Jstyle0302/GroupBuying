function createqrcode() {
    var link = $("#myShareLink").val();
    var width = 100;
    var rectangle = width + "x" + width;
    var url = "https://chart.googleapis.com/chart?chs=" + rectangle + "&cht=qr&chl=" + link + "&choe=UTF-8&chld=M|2";
    var qr_code = "<img alt='Your QRcode' src='" + url + "' />";
    $('#qrcode').html(qr_code);
}
createqrcode();

function copyToClickboard() {
    /* Get the text field */
    var copyText = document.getElementById("myShareLink");
  
    /* Select the text field */
    copyText.select();
    copyText.setSelectionRange(0, 99999); /*For mobile devices*/
  
    /* Copy the text inside the text field */
    document.execCommand("copy");
  
    /* Alert the copied text */
  //   alert("Copied the text: " + copyText.value);
  }
