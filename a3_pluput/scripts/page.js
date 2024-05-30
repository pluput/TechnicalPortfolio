// ===================== Fall 2022 EECS 493 Assignment 3 =====================
// This starter code provides a structure and helper functions for implementing
// the game functionality. It is a suggestion meant to help you, and you are not
// required to use all parts of it. You can (and should) add additional functions
// as needed or change existing functions.

// ==================================================
// ============ Page Scoped Globals Here ============
// ==================================================

// Div Handlers
let game_window;
let game_screen;
let onScreenAsteroid;
let landing_page;
let settings_page;
let tutorial;
let myRange;
let demo;

// Difficulty Helpers
let astProjectileSpeed = 3;          // easy: 1, norm: 3, hard: 5

// Game Object Helpers
let currentAsteroid = 1;
let AST_OBJECT_REFRESH_RATE = 15;
let maxPersonPosX = 1205;
let maxPersonPosY = 640;
let maxShieldedPersonPosX = 1176;
let maxShieldedPersonPosY = 606;
let PERSON_SPEED = 5;                // Speed of the person
let vaccineOccurrence = 20000;       // Vaccine spawns every 20 seconds
let vaccineGone = 5000;              // Vaccine disappears in 5 seconds
let maskOccurrence = 15000;          // Masks spawn every 15 seconds
let maskGone = 5000;                 // Mask disappears in 5 seconds

// Movement Helpers
var LEFT = false;
var RIGHT = false;
var UP = false;
var DOWN = false;
var touched = false;

// global variable
let firstTime = false;
let difficulty_level = 1;
let switchToShield = false;
let freezeGame = false;

//volume variable
let currentVol = 50;

//scoreboard helpers
let scoreNum = 0;
let dangerNum = 20;
let levelNum = 1;
let endingScoreNum = 0;

// ==============================================
// ============ Functional Code Here ============
// ==============================================

// Main
$(document).ready(function () {
  // ====== Startup ====== 
  game_window = $('.game-window');
  game_screen = $("#actual_game");
  onScreenAsteroid = $('.curAstroid');
  landing_page = $('#landing_page');
  settings_page = $('#settings_page');
  tutorial_page = $('#tutorial');
  player = $('#rocket');

  // TODO: ADD MORE
  game_screen.hide();
  settings_page.hide();
  tutorial_page.hide();
  $("#game_over").hide();

  set_difficulty();
  
  moveRocketInterval = setInterval(moveRocket, 10);
  moveShieldRocketInterval = setInterval(moveShieldRocket, 10);

});

// TODO: ADD YOUR FUNCTIONS HERE

//How To Page Displayed?
function how_to_page() {
  if (firstTime > 0) {
    play_game();
  }

  else {
    $('#actual_game').hide();
    $("#tutorial").show();
    $('#landing_page').hide();
    ++firstTime;
  }
}

//Play Game Button
function play_game() {
  game_splash();
  document.getElementById('score_num').innerHTML = scoreNum;
  document.getElementById('danger_num').innerHTML = dangerNum;
  document.getElementById('level_num').innerHTML = levelNum;

  setTimeout(function() {
    $('#game_splash_header').remove();
    $('#game_splash_image').remove();
    $('#game_splash_text').remove();

    game_screen.append("<img id='rocket' src='./src/player/player.gif'></img>");
    spawn_astroids();
    spawn_portals();
    spawn_shields();
    increaseScoreInterval = setInterval(increase_score, 500);
  }, 3000);

  $('#actual_game').show();
  $("#tutorial").hide();
  $('#landing_page').hide();
}

function game_splash() {
  game_screen.append("<div id='game_splash_header' class='game_splash_class'> <strong>Get Ready!</strong> </div>");
  game_screen.append("<div id='game_splash_image' class='game_splash_class'> <img src='src/arrowkeys.png'/></div>");
  game_screen.append("<div id='game_splash_text' class='game_splash_class'>Use arrow keys to move.</div>");
}

function moveRocket() {
  if (LEFT) {
    newPos = parseInt($("#rocket").css("left")) - PERSON_SPEED;
    if (newPos < 0) {
      newPos = 0;
    }
    $("#rocket").css("left", newPos);
    $("#rocket").attr("src", "src/player/player_left.gif");
  }

  if (RIGHT) {
    newPos = parseInt($("#rocket").css("left")) + PERSON_SPEED;
    if (newPos > maxPersonPosX) {
      newPos = maxPersonPosX;
    }
    $("#rocket").css("left", newPos);
    $("#rocket").attr("src", "src/player/player_right.gif");
  }

  if (UP) {
    newPos = parseInt($("#rocket").css("top")) - PERSON_SPEED;
    if (newPos < 0) {
      newPos = 0;
    }
    $("#rocket").css("top", newPos);
    $("#rocket").attr("src", "src/player/player_up.gif");
  }

  if (DOWN) {
    newPos = parseInt($("#rocket").css("top")) + PERSON_SPEED;
    if (newPos > maxPersonPosY) {
      newPos = maxPersonPosY;
    }
    $("#rocket").css("top", newPos);
    $("#rocket").attr("src", "src/player/player_down.gif");
  }
}

function moveShieldRocket() {
  if (LEFT) {
    newPos = parseInt($("#rocketInShield").css("left")) - PERSON_SPEED;
    if (newPos < 0) {
      newPos = 0;
    }
    $("#rocketInShield").css("left", newPos);
    $("#rocketInShield").attr("src", "src/player/player_shielded_left.gif");
  }

  if (RIGHT) {
    newPos = parseInt($("#rocketInShield").css("left")) + PERSON_SPEED;
    if (newPos > maxShieldedPersonPosX) {
      newPos = maxShieldedPersonPosX;
    }
    $("#rocketInShield").css("left", newPos);
    $("#rocketInShield").attr("src", "src/player/player_shielded_right.gif");
  }

  if (UP) {
    newPos = parseInt($("#rocketInShield").css("top")) - PERSON_SPEED;
    if (newPos < 0) {
      newPos = 0;
    }
    $("#rocketInShield").css("top", newPos);
    $("#rocketInShield").attr("src", "src/player/player_shielded_up.gif");
  }

  if (DOWN) {
    newPos = parseInt($("#rocketInShield").css("top")) + PERSON_SPEED;
    if (newPos > maxShieldedPersonPosY) {
      newPos = maxShieldedPersonPosY;
    }
    $("#rocketInShield").css("top", newPos);
    $("#rocketInShield").attr("src", "src/player/player_shielded_down.gif");
  }
}

function stabilizeRocket() {
  $("#rocket").attr("src", "src/player/player.gif");
}

function stabilizeShieldRocket() {
  $("#rocketInShield").attr("src", "src/player/player_shielded.gif");
}

function spawn_astroids() {
  if (difficulty_level == 0) {
    diffEasySpawn = setInterval(spawn, 1000);
    astProjectileSpeed = 1;
  }

  if (difficulty_level == 1) {
    diffNormalSpawn = setInterval(spawn, 800);
    astProjectileSpeed = 3;
  }

  if (difficulty_level == 2) {
    diffHardSpawn = setInterval(spawn, 600);
    astProjectileSpeed = 5;
  }
}

function spawn_shields() {
  shieldInterval = setInterval(function() {
    //make shield randomly appear
    game_screen.append("<img id='shields' src='src/shield.gif'></img>");
    $("#shields").css("top", getRandomNumber(0, 640));
    $("#shields").css("left", getRandomNumber(0, 1200));

    //check if rocket collides with shield
    takeShieldInterval = setInterval(function() {
      if (isColliding($('#rocket'), $('#shields'))) {
        //play sound
        let audio = new Audio('src/audio/collect.mp3');
        audio.volume = currentVol / 100;
        audio.play();

        currTop = document.getElementById("rocket").style.top;
        currLeft = document.getElementById("rocket").style.left;
        //delete shield and rocket images
        $('#shields').remove();
        $('#rocket').remove();
        //add rocket in shield image
        game_screen.append("<img id='rocketInShield' src='./src/player/player_shielded.gif'></img>");
        $("#rocketInShield").css("top", currTop);
        $("#rocketInShield").css("left", currLeft);
        //switch to moveShieldRocket
        switchToShield = true;
        //clear curr intervals
        clearInterval(takeShieldInterval);
        clearInterval(shieldInterval);
      }
    }, 10);

    setTimeout(function() {
      clearInterval(takeShieldInterval)
      }, 5000);

    setTimeout(function() {
      $('#shields').remove();
    }, 5000);
  }, 15000);
}

function spawn_portals() {
  portalInterval = setInterval(function() {
    //make portal randomly appear
    game_screen.append("<img id='portals' src='src/port.gif'></img>");
    $("#portals").css("top", getRandomNumber(0, 640));
    $("#portals").css("left", getRandomNumber(0, 1200));

    //check if rocket collides with portal
    takePortalInterval = setInterval(function() {
      if (switchToShield) {
        if (isColliding($('#rocketInShield'), $('#portals'))) {
          portal_collision();
        }
      }
      else {
        if (isColliding($('#rocket'), $('#portals'))) {
          portal_collision();
        }
      }
      
    }, 10);
    
    setTimeout(function() {
      clearInterval(takePortalInterval)
    }, 5000);
    
    setTimeout(function() {
      $('#portals').remove();
    }, 5000);
  }, 20000);
}

function portal_collision() {
  //play sound
  let audio = new Audio('src/audio/collect.mp3');
  audio.volume = currentVol / 100;
  audio.play();
  //delete portal
  $('#portals').remove();
  //increment level by 1
  levelNum = levelNum + 1;
  document.getElementById('level_num').innerHTML = levelNum;
  //increase rockets speed
  increase_speed();
  clearInterval(takePortalInterval);
  //increment danger by 2
  dangerNum = dangerNum + 2;
  document.getElementById('danger_num').innerHTML = dangerNum;
}

function increase_speed() {
  newSpeed = astProjectileSpeed * 0.2;
  astProjectileSpeed += newSpeed;
}

function increase_score() {
  scoreNum = scoreNum + 40;
  document.getElementById('score_num').innerHTML = scoreNum;
}

//Settings button
function settings() {
  $('#settings_page').show();
  slider = document.getElementById("myRange");
  output = document.getElementById("demo");
  output.innerHTML = slider.value; // Display the default slider value

  // Update the current slider value (each time you drag the slider handle)
  slider.oninput = function() {
    output.innerHTML = this.value;
    currentVol = this.value;
  }
}

//Close Settings Button
function close_settings() {
  $('#settings_page').hide();
}

//setting difficulty border
function set_difficulty() {
  //jquery
  $("#difficulty_easy").click( function() {
    //all other buttons have black border
    $("#difficulty_normal").css("border-color", "black");
    $("#difficulty_normal").css("border-width", "1px");
    $("#difficulty_hard").css("border-color", "black");
    $("#difficulty_hard").css("border-width", "1px");
    //highlight normal
    $("#difficulty_easy").css("border-color", "yellow");
    $("#difficulty_easy").css("border-width", "3px");
    difficulty_level = 0;
    dangerNum = 10;
  })

  $("#difficulty_normal").click( function() {
    //all other buttons have black border
    $("#difficulty_easy").css("border-color", "black");
    $("#difficulty_easy").css("border-width", "1px");
    $("#difficulty_hard").css("border-color", "black");
    $("#difficulty_hard").css("border-width", "1px");
    //highlight normal
    $("#difficulty_normal").css("border-color", "yellow");
    $("#difficulty_normal").css("border-width", "3px");
    difficulty_level = 1;
    dangerNum = 20;
  })

  $("#difficulty_hard").click( function() {
    //all other buttons have black border
    $("#difficulty_easy").css("border-color", "black");
    $("#difficulty_easy").css("border-width", "1px");
    $("#difficulty_normal").css("border-color", "black");
    $("#difficulty_normal").css("border-width", "1px");
    //highlight hard
    $("#difficulty_hard").css("border-color", "yellow");
    $("#difficulty_hard").css("border-width", "3px");
    difficulty_level = 2;
    dangerNum = 30;
  })
}

//game over page
function gameOver() {
  //save scoreNum to display on game over page
  endingScoreNum = scoreNum;
  //remove and restart curr elements on game page so we can start over
  $("#rocketTouched").remove();
  $('#shields').remove();
  $('#portals').remove();
  scoreNum = 0;
  dangerNum = 20;
  levelNum = 1;
  switchToShield = false;
  freezeGame = false;

  //hide all screens except landing page
  game_screen.hide();
  settings_page.hide();
  tutorial_page.hide();
  landing_page.show();
  $("#play_game_button").hide();
  $("#settings_button").hide();
  $("#game_over").show();

  document.getElementById('display_score').innerHTML = endingScoreNum;

  //took these from main function, resetting them
  moveRocketInterval = setInterval(moveRocket, 10);
  moveShieldRocketInterval = setInterval(moveShieldRocket, 10);

}

function startOver() {
  $("#game_over").hide();
  $("#play_game_button").show();
  $("#settings_button").show();
}

// Keydown event handler
document.onkeydown = function (e) {
  if (e.key == 'ArrowLeft') LEFT = true;
  if (e.key == 'ArrowRight') RIGHT = true;
  if (e.key == 'ArrowUp') UP = true;
  if (e.key == 'ArrowDown') DOWN = true;

  if (switchToShield) {
    moveShieldRocket();
  }
  else {
    moveRocket();
  }
}

// Keyup event handler
document.onkeyup = function (e) {
  if (e.key == 'ArrowLeft') LEFT = false;
  if (e.key == 'ArrowRight') RIGHT = false;
  if (e.key == 'ArrowUp') UP = false;
  if (e.key == 'ArrowDown') DOWN = false;

  if (switchToShield) {
    stabilizeShieldRocket();
  }
  else {
    stabilizeRocket();
  }
}

// Starter Code for randomly generating and moving an asteroid on screen
// Feel free to use and add additional methods to this class
class Asteroid {
  // constructs an Asteroid object
  constructor() {
      /*------------------------Public Member Variables------------------------*/
      // create a new Asteroid div and append it to DOM so it can be modified later
      let objectString = "<div id = 'a-" + currentAsteroid + "' class = 'curAstroid' > <img src = 'src/asteroid.png'/></div>";
      onScreenAsteroid.append(objectString);
      // select id of this Asteroid
      this.id = $('#a-' + currentAsteroid);
      currentAsteroid++; // ensure each Asteroid has its own id
      // current x, y position of this Asteroid
      this.cur_x = 0; // number of pixels from right
      this.cur_y = 0; // number of pixels from top

      /*------------------------Private Member Variables------------------------*/
      // member variables for how to move the Asteroid
      this.x_dest = 0;
      this.y_dest = 0;
      // member variables indicating when the Asteroid has reached the boarder
      this.hide_axis = 'x';
      this.hide_after = 0;
      this.sign_of_switch = 'neg';
      // spawn an Asteroid at a random location on a random side of the board
      this.#spawnAsteroid();
  }

  // Requires: called by the user
  // Modifies:
  // Effects: return true if current Asteroid has reached its destination, i.e., it should now disappear
  //          return false otherwise
  hasReachedEnd() {
      if(this.hide_axis == 'x'){
          if(this.sign_of_switch == 'pos'){
              if(this.cur_x > this.hide_after){
                  return true;
              }                    
          }
          else{
              if(this.cur_x < this.hide_after){
                  return true;
              }          
          }
      }
      else {
          if(this.sign_of_switch == 'pos'){
              if(this.cur_y > this.hide_after){
                  return true;
              }                    
          }
          else{
              if(this.cur_y < this.hide_after){
                  return true;
              }          
          }
      }
      return false;
  }

  // Requires: called by the user
  // Modifies: cur_y, cur_x
  // Effects: move this Asteroid 1 unit in its designated direction
  updatePosition() {
      // ensures all asteroids travel at current level's speed
      this.cur_y += this.y_dest * astProjectileSpeed;
      this.cur_x += this.x_dest * astProjectileSpeed;
      // update asteroid's css position
      this.id.css('top', this.cur_y);
      this.id.css('right', this.cur_x);

  }

  // Requires: this method should ONLY be called by the constructor
  // Modifies: cur_x, cur_y, x_dest, y_dest, num_ticks, hide_axis, hide_after, sign_of_switch
  // Effects: randomly determines an appropriate starting/ending location for this Asteroid
  //          all asteroids travel at the same speed
  #spawnAsteroid() {
      // REMARK: YOU DO NOT NEED TO KNOW HOW THIS METHOD'S SOURCE CODE WORKS
      let x = getRandomNumber(0, 1280);
      let y = getRandomNumber(0, 720);
      let floor = 784;
      let ceiling = -64;
      let left = 1344;
      let right = -64;
      let major_axis = Math.floor(getRandomNumber(0, 2));
      let minor_aix =  Math.floor(getRandomNumber(0, 2));
      let num_ticks;

      if(major_axis == 0 && minor_aix == 0){
          this.cur_y = floor;
          this.cur_x = x;
          let bottomOfScreen = game_screen.height();
          num_ticks = Math.floor((bottomOfScreen + 64) / astProjectileSpeed);

          this.x_dest = (game_screen.width() - x);
          this.x_dest = (this.x_dest - x)/num_ticks + getRandomNumber(-.5,.5);
          this.y_dest = -astProjectileSpeed - getRandomNumber(0, .5);
          this.hide_axis = 'y';
          this.hide_after = -64;
          this.sign_of_switch = 'neg';
      }
      if(major_axis == 0 && minor_aix == 1){
          this.cur_y = ceiling;
          this.cur_x = x;
          let bottomOfScreen = game_screen.height();
          num_ticks = Math.floor((bottomOfScreen + 64) / astProjectileSpeed);

          this.x_dest = (game_screen.width() - x);
          this.x_dest = (this.x_dest - x)/num_ticks + getRandomNumber(-.5,.5);
          this.y_dest = astProjectileSpeed + getRandomNumber(0, .5);
          this.hide_axis = 'y';
          this.hide_after = 784;
          this.sign_of_switch = 'pos';
      }
      if(major_axis == 1 && minor_aix == 0) {
          this.cur_y = y;
          this.cur_x = left;
          let bottomOfScreen = game_screen.width();
          num_ticks = Math.floor((bottomOfScreen + 64) / astProjectileSpeed);

          this.x_dest = -astProjectileSpeed - getRandomNumber(0, .5);
          this.y_dest = (game_screen.height() - y);
          this.y_dest = (this.y_dest - y)/num_ticks + getRandomNumber(-.5,.5);
          this.hide_axis = 'x';
          this.hide_after = -64;
          this.sign_of_switch = 'neg';
      }
      if(major_axis == 1 && minor_aix == 1){
          this.cur_y = y;
          this.cur_x = right;
          let bottomOfScreen = game_screen.width();
          num_ticks = Math.floor((bottomOfScreen + 64) / astProjectileSpeed);

          this.x_dest = astProjectileSpeed + getRandomNumber(0, .5);
          this.y_dest = (game_screen.height() - y);
          this.y_dest = (this.y_dest - y)/num_ticks + getRandomNumber(-.5,.5);
          this.hide_axis = 'x';
          this.hide_after = 1344;
          this.sign_of_switch = 'pos';
      }
      // show this Asteroid's initial position on screen
      this.id.css("top", this.cur_y);
      this.id.css("right", this.cur_x);
      // normalize the speed s.t. all Asteroids travel at the same speed
      let speed = Math.sqrt((this.x_dest)*(this.x_dest) + (this.y_dest)*(this.y_dest));
      this.x_dest = this.x_dest / speed;
      this.y_dest = this.y_dest / speed;
  }
}

// Spawns an asteroid travelling from one border to another
function spawn() {
  let asteroid = new Asteroid();
  setTimeout(spawn_helper(asteroid), 0);
}

function spawn_helper(asteroid) {
  let astermovement = setInterval(function () {
    // update asteroid position on screen
    asteroid.updatePosition();

    //if rocket is not in shield and collides with asteroid
    if (!switchToShield) {
      if (freezeGame) {
        clearInterval(astermovement);

        //after 2 seconds, delete all asteroids
        setTimeout(function() {
          asteroid.id.remove();
        }, 2000);
      }

      else if (isColliding($("#rocket"), asteroid.id)) {
        //based on diff level, clear that spawnAsteroids interval
        if (difficulty_level == 0) {
          clearInterval(diffEasySpawn);
        }
        else if (difficulty_level == 1) {
          clearInterval(diffNormalSpawn);
        }
        else if (difficulty_level == 2) {
          clearInterval(diffHardSpawn);
        }

        //play sound
        let audio = new Audio('src/audio/die.mp3');
        audio.volume = currentVol / 100;
        audio.play();

        //remove curr rocket image and change to rocketTouched image
        currTop = document.getElementById("rocket").style.top;
        currLeft = document.getElementById("rocket").style.left;
        $("#rocket").remove();
        game_screen.append("<img id='rocketTouched' src='./src/player/player_touched.gif'></img>");
        $("#rocketTouched").css("top", currTop);
        $("#rocketTouched").css("left", currLeft);

        //freeze other asteroids
        freezeGame = true;

        //clear all other intervals
        clearInterval(moveRocketInterval);
        clearInterval(moveShieldRocketInterval);
        clearInterval(shieldInterval);
        clearInterval(portalInterval);
        clearInterval(increaseScoreInterval);

        //stop moving this asteroid
        clearInterval(astermovement);

        //switch to Game Over page
        setTimeout(function() {
          gameOver();
          asteroid.id.remove();
        }, 2000);
      }
    }

    //if rocket IS in shield and collides with asteroid
    else if (switchToShield) {
      if (isColliding($("#rocketInShield"), asteroid.id)) {
        currTop = document.getElementById("rocketInShield").style.top;
        currLeft = document.getElementById("rocketInShield").style.left;
        //delete shield and rocket images
        asteroid.id.remove();
        $('#rocketInShield').remove();
        //add rocket in shield image
        game_screen.append("<img id='rocket' src='./src/player/player.gif'></img>");
        $("#rocket").css("top", currTop);
        $("#rocket").css("left", currLeft);
        //switch to moveRocket
        switchToShield = false;
        //spawn shields again
        spawn_shields();
        //clear curr interval
        clearInterval(astermovement);
      }
    }

    // determine whether asteroid has reached its end position, i.e., outside the game border
    if (asteroid.hasReachedEnd()) {
      asteroid.id.remove();
      clearInterval(astermovement);
    }
  }, AST_OBJECT_REFRESH_RATE);
}

//===================================================

// ==============================================
// =========== Utility Functions Here ===========
// ==============================================

// Are two elements currently colliding?
function isColliding(o1, o2) {
  return isOrWillCollide(o1, o2, 0, 0);
}

// Will two elements collide soon?
// Input: Two elements, upcoming change in position for the moving element
function willCollide(o1, o2, o1_xChange, o1_yChange) {
  return isOrWillCollide(o1, o2, o1_xChange, o1_yChange);
}

// Are two elements colliding or will they collide soon?
// Input: Two elements, upcoming change in position for the moving element
// Use example: isOrWillCollide(paradeFloat2, person, FLOAT_SPEED, 0)
function isOrWillCollide(o1, o2, o1_xChange, o1_yChange) {
  const o1D = {
    'left': o1.offset().left + o1_xChange,
    'right': o1.offset().left + o1.width() + o1_xChange,
    'top': o1.offset().top + o1_yChange,
    'bottom': o1.offset().top + o1.height() + o1_yChange
  };
  const o2D = {
    'left': o2.offset().left,
    'right': o2.offset().left + o2.width(),
    'top': o2.offset().top,
    'bottom': o2.offset().top + o2.height()
  };
  // Adapted from https://developer.mozilla.org/en-US/docs/Games/Techniques/2D_collision_detection
  if (o1D.left < o2D.right &&
    o1D.right > o2D.left &&
    o1D.top < o2D.bottom &&
    o1D.bottom > o2D.top) {
    // collision detected!
    return true;
  }
  return false;
}

// Get random number between min and max integer
function getRandomNumber(min, max) {
  return (Math.random() * (max - min)) + min;
}
