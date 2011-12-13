// ==UserScript==
// @name          Glitch Auction Calorie Cost Calculator
// @description   Calculates the calories ("energy") per currant.
// @include       http://www.glitch.com/auctions/cat-food/*
// @author        Phil Harnish <philharnish@gmail.com>
// @version       1.0
//
// ==/UserScript==

function main() {
  // Remove any items with banned words.
  var itemToEnergy = {
    'abbasid_ribs': 88,
    'all_spice': 1,
    'apple': 5,
    'applejack': 25,
    'awesome_stew': 200,
    'banana': 10,
    'banana_no_names': 32,
    'basic_omelet': 33,
    'bean_plain': 1,
    'berry_bowl': 37,
    'best_bean_dip': 38,
    'big_salad': 58,
    'birch_syrup': 4,
    'black_pepper': 1,
    'blue_bubble': 5,
    'bunch_of_grapes': 4,
    'sno_cone_blue': 0,
    'broccoli': 5,
    'bubble_and_squeak': 60,
    'bun': 9,
    'butterfly_butter': 6,
    'cabbage': 7,
    'camphor': 1,
    'cardamom': 1,
    'carrot': 6,
    'cedar_plank_salmon': 70,
    'cheese': 6,
    'cheese_plate': 36,
    'cheezy_sammich': 23,
    'cheezy_sauce': 26,
    'cherry': 1,
    'chillybusting_chili': 142,
    'choice_crudites': 38,
    'cinnamon': 1,
    'cloudberry': 2,
    'cloudberry_jam': 39,
    'cold_taco': 53,
    'common_crudites': 30,
    'corn': 6,
    'corn_off_the_cob': 40,
    'corny_fritter': 33,
    'creamy_catsup': 53,
    'cucumber': 4,
    'cumin': 1,
    'curry': 1,
    'deluxe_sammich': 37,
    'divine_crepes': 69,
    'egg_plain': 5,
    'eggy_scramble': 25,
    'exotic_fruit_salad': 30,
    'expensive_grilled_cheese': 173,
    'flour': 7,
    'flummery': 99,
    'fortifying_gruel': 191,
    'fried_egg': 8,
    'fried_noodles': 28,
    'fried_rice': 77,
    'frog_in_a_hole': 35,
    'fruit_salad': 25,
    'gammas_pancakes': 35,
    'garlic': 1,
    'ginger': 1,
    'grain': 1,
    'greasy_frybread': 37,
    'green_eggs': 12,
    'sno_cone_green': 0,
    'grilled_cheese': 53,
    'hard_bubble': 15,
    'hash': 57,
    'hearty_groddle_sammich': 93,
    'hearty_omelet': 102,
    'honey': 4,
    'hot_n_fizzy_sauce': 35,
    'hot_pepper': 1,
    'ice': 2,
    'ixstyle_braised_meat': 162,
    'juicy_carpaccio': 56,
    'lazy_salad': 22,
    'lemburger': 127,
    'lemon': 5,
    'licorice': -3,
    'lotsa_lox': 34,
    'mangosteen': 10,
    'meat': 10,
    'meat_gumbo': 93,
    'meat_tetrazzini': 192,
    'messy_fry_up': 52,
    'mexicali_eggs': 37,
    'mild_sauce': 26,
    'mushroom': 3,
    'mustard': 1,
    'nutmeg': 1,
    'oats': 8,
    'oaty_cake': 32,
    'obvious_panini': 92,
    'oily_dressing': 3,
    'older_spice': 1,
    'olive_oil': 5,
    'onion': 4,
    'orange': 5,
    'sno_cone_orange': 0,
    'parsnip': 6,
    'pickle': 21,
    'pinch_of_salt': 1,
    'pineapple': 7,
    'papl_upside_down_pizza': 22,
    'plain_bubble': 2,
    'plain_noodles': 13,
    'plank': 0,
    'plum': 3,
    'potato': 7,
    'potato_patty': 26,
    'proper_rice': 26,
    'sno_cone_purple': 0,
    'rice': 4,
    'rich_tagine': 101,
    'saffron': 1,
    'salmon': 15,
    'sammich': 29,
    'scrumptious_frittata': 39,
    'secret_sauce': 28,
    'sesame_oil': 4,
    'simple_bbq': 86,
    'simple_slaw': 24,
    'snack_pack': 49,
    'spicy_quesadilla': 68,
    'spinach': 3,
    'spinach_salad': 16,
    'cheese_stinky': 12,
    'strawberry': 4,
    'super_veggie_kebabs': 58,
    'sweet_n_sour_sauce': 29,
    'tangy_noodles': 45,
    'tangy_sauce': 10,
    'tasty_pasta': 134,
    'tiny_bubble': 10,
    'tomato': 5,
    'tortilla': 6,
    'turmeric': 1,
    'cheese_very_stinky': 18,
    'cheese_very_very_stinky': 24,
    'waffles': 49,
    'wavy_gravy': 75,
    'whortleberry': 5,
    'whortleberry_jelly': 75,
    'yummy_gruel': 134,
    'zucchini': 5
  };

  var maxCpc = 0;
  var maxName = '';
  $('#items').find('tr.class_item').each(function(i, elem) {
    var name = $(elem).attr('id').slice(0, -1);
    var price = $(elem).find('p.total').text().trim().slice(0, -1);
    var energy = itemToEnergy[name];
    var cpc = Math.round(100 * energy / price) / 100;
    if (cpc > maxCpc) {
      maxCpc = cpc;
      maxName = name;
    }
    $(this).append('<td>' + cpc + 'cpc<' + '/td>');
  });
  $('.auction_results_header').
      append('<strong>Winner: ' + maxName +
             ' @ ' + maxCpc + 'cpc<' + '/strong>');
}

var script = document.createElement("script");
script.textContent = "(" + main.toString() + ")();";
document.body.appendChild(script);
