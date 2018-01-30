// // $(window).load(function(){
// // 	alert("vvv");
// // 	event.preventDefault();
// // });
// <script type="text/javascript">
// $( window ).on( "load", function() {
//   $('#loading').show();
//   // event.preventDefault();
// });
// $(window).bind("load", function() {
//   $('#loading').css( 'display', 'block', 'important' );
//   event.preventDefault();
// });
$(document).ready(function(){
  $("#user_form").submit(function(){
    $('#loading').css( 'display', 'block', 'important' );
  });
});