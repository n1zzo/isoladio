var typingTimer;        
var doneTypingInterval = 250; 

//on keyup, start the countdown
$("#search-form").on('keyup', function () {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(startSearch, doneTypingInterval);
});

//on keydown, clear the countdown 
$("#search-form").on('keydown', function () {
    clearTimeout(typingTimer);
});

function startSearch() {
    var submitter_str = $("#name-form").val();
    var query_str = $("#search-form").val();
    console.log("Searching..."+query_str);
    $.ajax({
        type: "GET",
        url: "/search",
        data: {"submitter": submitter_str , "query":query_str},
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $.each( data, function( key, val ) {
                $("#results").append('<marquee behavior="scroll" direction="left">'+val+"</marquee>");
            });
        }
    });
}

function searchMode() {
    $("#queue").addClass("reduced-queue");
    $("#results").addClass("enlarged");
    event.stopPropagation();
}

function reduce() {
    $("#queue").removeClass("reduced-queue");
    $("#results").removeClass("enlarged");
}
