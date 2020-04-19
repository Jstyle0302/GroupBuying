function createqrcode() {
    var link = $("#shareLink").attr('href');
    var width = 100;
    var rectangle = width + "x" + width;
    var url = "https://chart.googleapis.com/chart?chs=" + rectangle + "&cht=qr&chl=" + link + "&choe=UTF-8&chld=M|2";
    var qr_code = "<img alt='Your QRcode' src='" + url + "' />";
    $('#qrcode').html(qr_code);
}
createqrcode();