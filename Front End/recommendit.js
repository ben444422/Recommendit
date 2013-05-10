//show a notification box on the page with text
function showNotif(text) {
	$('#notif-block').css('visibility', 'visible');
	$('#notif-content').empty();
	$('#notif-content').append(text);
}
$(document).ready(function() {
	var movedUp = false;
	
	$('#notif-button').click(function() {
		$('#notif-block').css('visibility', 'hidden');
	});
	
	$('#recBtn').on({
		click : function() {
			var username = $('#username').val();
			if (username == null)
				return;
			username = $.trim(username);
			if (username.length == 0)
				return;
			if (!movedUp) {
				$('.sect').animate({
					"top" : "-50%"
				}, "slow");
				movedUp = true;

				$('.loader').animate({
					"top" : "30%"
				}, "slow");
			}
			//send ajax request
			$.ajax({
				url : "http://localhost/cgi-bin/LoadRecommendation.py",
				type : "post",
				datatype : "json",
				data : {
					'username' : username,
				},
				success : function(response) {
					if (response.success == false) {
						movedUp = false;
						$('.sect').animate({
							"top" : "20%"
						}, "slow");
						$('.loader').animate({
							"top" : "-50%"
						}, "slow", function() {
							$(this).css({
								top : "150%"
							});
						});
						showNotif("Username not found!");
						return;
					}

					$('.output-content').empty();
					$('.output-title').empty();
					$('.output-title').append("<h3> Hi " + username + "! I recommend: </h3>");
					subreddits = response.message.split(" ");
					var initPx = 30;
					for (var i = 0; i < subreddits.length; i++) {
						$('.output-content').append($('<a></a>').attr('href', "http://www.reddit.com/r/" + subreddits[i]).attr('target', "_blank")
						.text(subreddits[i]).css({
							'font-size': '' + initPx.toString() + 'px',
							'line-height': '1',
							color : 'black'
						}));
						$('.output-content').append("<br>");
						initPx--;
					}
					console.log(document);

					$('.sect2').animate({
						"top" : "5%"
					}, "slow");
					$('.backBtn').animate({
						"top" : "0%"
					}, "slow");
					$('.loader').animate({
						"top" : "-50%"
					}, "slow", function() {
						$(this).css({
							top : "150%"
						});
					});
				}
			});
		}
	});
	$('.backBtn').click(function() {
		movedUp = false;
		$('.sect').animate({
			"top" : "20%"
		}, "slow");
		$('.sect2').animate({
			"top" : "150%"
		}, "slow");
		$('.backBtn').animate({
			"top" : "150%"
		}, "slow");
	});

});
