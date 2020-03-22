var typingTimer;        
var doneTypingInterval = 250; 
var search_results = [];

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
    var base_url = window.location.origin+window.location.pathname;
    console.log("Searching..."+query_str);
    json_data = $.ajax({
        type: "GET",
        url: "search",
        data: {"submitter": submitter_str , "query":query_str},
        contentType: "application/json; charset=utf-8",
        dataType: "json",
	success: (data) => {
		res = data["data"].slice(0, 20);
    		$("#results").empty();
    		$("#results").append("<ul>");
        	res.forEach(el => {$("#results").append("<li>"+el["name"]+"</li>");});
    		$("#results").append("</ul>");
		search_results = res;
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
