/* on click, load the json for the particular feed
 * when clicking on stories render them inline
 * implement mark-as-read as 'mark all things older than XXX date as read'*/
function select_section(event) {
  var feed_num = $(event.target).data("feed")
  if (feed_num != '*') {
    $("#feeds li").hide()
    $("#feeds .feed"+feed_num).show()
    $("#display_all").show()
    $("#feeds").css("height", "90%")
  } else {
    $("#display_all").hide()
    $("#feeds li").show()
    $("#feeds").css("height", "80%")
  }
  window.scrollTo(0,0)
}
$("button").click(select_section)
