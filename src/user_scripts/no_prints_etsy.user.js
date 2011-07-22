// ==UserScript==
// @name          Etsy "Prints" Remover
// @description   Removes items which are suspected to be prints.
// @include       http://*.etsy.com*
// @author        Phil Harnish <philharnish@gmail.com>
// @version       1.1
//
// ==/UserScript==

// the guts of this userscript
function main() {
  // Remove any items with banned words.
  var banned = [
    "limited edition",
    "print"
  ];
  $('.listing-card').filter(function () {
    var title = $(this).find("a[title]:first").attr("title").toLowerCase();
    var bad = false;
    $.each(banned, function (_, v) {
      bad = title.indexOf(v) >= 0;
      return !bad;
    });
    return bad;
  }).hide();
  // Allow multiline titles.
  $('.listing-title a[title]').each(function () {
    $(this).text($(this).attr('title'));
  });
  $(".listing-card").css("height", "auto");
  $(".listing-title").css("height", "auto");
  $(".listing-detail").css("position", "relative");
}

var script = document.createElement("script");
script.textContent = "(" + main.toString() + ")();";
document.body.appendChild(script);
