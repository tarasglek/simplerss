/* on click, load the json for the particular feed
 * when clicking on stories render them inline
 * implement mark-as-read as 'mark all things older than XXX date as read'*/
function select_section(event) {
  var feed_num = $(event.target).data("feed")
  if (feed_num != '*') {
    $("#feeds li").hide()
    $("#feeds .feed"+feed_num).show()
    $("#display_all").show()
    $("#navlist").css("top", "90%")
    $("#navlist").css("height", "10%")
  } else {
    $("#display_all").hide()
    $("#feeds li").show()
    $("#navlist").css("top", "80%")
    $("#navlist").css("height", "20%")
  }
  window.scrollTo(0,0)
}

function get(url, handler) {
  var xhr = new XMLHttpRequest();
  xhr.onload = function (e) {
    if (e.target.status == 200) 
      handler.apply(this, [e])
    else 
      console.log("Code "+e.target.status+" while loading "+url)
  }

  // deal with caching issues
  var debug = ""
  //debug += new Date()
  xhr.open("get", url+"?" + debug, true);
  xhr.send(null);
}

function fill_li(li, json) {
  function fillmein() {
    var feed = JSON.parse(this.responseText)
    var title = $("a", li).text()
    for (var i in feed['entries']) {
      var e = feed['entries'][i]
      if (e['title'] == title) {
        var content = $("<summary/>")
        content.html('content' in e ? e['content'][0]['value'] : e['summary'])
        $(li).append(content)
        window.foo = li
        break;
      }
    }
  }
  get("out/feeds/"+json, fillmein);
}

function expand_story(event) {
  var li = event.target
  if (li.tagName != "LI")
    li = li.parentElement
  // only expand the LI once
  if ($("summary", li).length || li.tagName != "LI") {
    console.log("refusing to expand content twice")
    return
  }
  var feedNum = li.className.substring(4);
  $("#navlist button").each(function (i, o) {
                              if ($(o).data("feed") == feedNum) {
                                fill_li(li, $(o).data("json"))
                                return false;
                              }
                            })
}

$("button").click(select_section)
$("#feeds li").click(expand_story)
