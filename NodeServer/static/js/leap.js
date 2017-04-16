var cats = {};
var isStartGame = false;
var isSuperKill = false;
var superKillTIme = 3000;		// delay superKillTime then set isSuperKill to false;
var lostNum = 0; // when to active handLost event
var focusNum = 0;



var Controller = Leap.loop(function(frame) {
	focusNum = 0;
	//clear last attack event
	if(leapED) leapED.dispatchEvent(LeapEventDispatcher.EVENT_PLAYER_DISABLE_ATTACK);

	frame.hands.forEach(function(hand, index) {
		var cat = ( cats[index] || (cats[index] = new Cat()) );

		//attack control
		if(hand.type == "left") {
			cat.setTransform(hand.screenPosition(), -hand.roll(), "attack", null);
		}

		//move control
		if(hand.type == "right") {
			var radius;
			if(hand.sphereRadius >120) {
				radius = 120;
			} else {
				radius = hand.sphereRadius;
			}
			step = (120 - radius)/10;
			cat.setTransform(hand.screenPosition(), -hand.roll(), "move" , step);
		}

		//start and attack super kill controll
		if(hand.type == "right" && frame.valid && frame.gestures.length > 0){
		    frame.gestures.forEach(function(gesture){
		        switch (gesture.type){
		          case "circle":
		              console.log("Circle Gesture");
					  if(leapED && !isStartGame) leapED.dispatchEvent(LeapEventDispatcher.EVENT_START_GAME);
		              break;
		          case "keyTap":
		              console.log("Key Tap Gesture");
		              break;
		          case "screenTap":
		              console.log("Screen Tap Gesture");
		              break;
		          case "swipe":
		              console.log("Swipe Gesture");
					  if(frame.hands.length == 1 && hand.type == "right" && leapED && !isSuperKill) {
						  var eve = new LEvent(LeapEventDispatcher.EVENT_START_SKILL);
						  isSuperKill = true;
						  setTimeout("isSuperKill = false", superKillTIme);
						  eve.index = 0;
						  leapED.dispatchEvent(eve);
					  }
		              break;
		        }
	    	});
	  }
	});

	// a little sickness...  Detect if hands.len = 0 then active lost event
	if(leapED && frame.hands.length === 0 && gameLayer && !gameLayer.isPause && !isSuperKill) {
		if( lostNum++ == 100) {
			lostNum = 0;
			leapED.dispatchEvent(LeapEventDispatcher.EVENT_HAND_LOST);
		}
	}
})
.use('screenPosition', {scale: 0.25})
.use('handEntry')
.on('handFound', function(hand){
	if(leapED) {
		leapED.dispatchEvent(LeapEventDispatcher.EVENT_HAND_FOUND);
	}
})
.on('streamingStopped', function(){
	if(leapED) {
		leapED.dispatchEvent(LeapEventDispatcher.EVENT_HAND_LOST);
	}
})
.on('streamingStarted', function(){
	// seem fool but usefull.
	if(leapED) {
		if( isStartGame) {
			leapPlugIn = true;
			leapED.dispatchEvent(LeapEventDispatcher.EVENT_HAND_FOUND);
		} else {
			addBeginningText();
		}
	}
})
.on('focus', function(){
	if(leapED) {
		leapED.dispatchEvent(LeapEventDispatcher.EVENT_HAND_FOUND);
	}
});


var Cat = function() {
	var cat = this;
	cat.setTransform = function(position, rotation, type, step) {
		if (leapED) {
			var degree = rotation * (180/Math.PI);
			var rate = 1;
			if(type == "move"){
				var eve = new LEvent(LeapEventDispatcher.EVENT_HAND_MOVE);
				eve.angle = degree;
				eve.step = step;
				leapED.dispatchEvent(eve);
			}
			if(type == "attack"){
				var eve_attack = new LEvent(LeapEventDispatcher.EVENT_PLAYER_ATTACK);
				eve_attack.angle = degree;
				leapED.dispatchEvent(eve_attack);
			}
		}
	};
};

cats[0] = new Cat();

// This allows us to move the cat even whilst in an iFrame.
//Leap.loopController.setBackground(true)
