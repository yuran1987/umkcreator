$(document).ready(function(){

$('.container').prepend("<div id='menu-icon'><b>Menu</b></div>");


$("#menu-icon").on("click", function(){
	$(".menu").slideToggle();
	$(this).toggleClass("active");
});


});
