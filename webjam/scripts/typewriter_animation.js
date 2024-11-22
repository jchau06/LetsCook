// Modified from https://codepen.io/haaswill/pen/VKzXve

const words = ["Spicy Ramen...", "Fish & Chips...", "Spicy Curry..."];
let i = 0;
let timer;

let TYPE_DELAY = 300
let DELETE_DELAY = 100
let TARGET_ELEMENT = 'typewriter_animation'

function typingEffect() {
	let word = words[i].split("");
	var loopTyping = function() {
		if (word.length > 0) {
			document.getElementById(TARGET_ELEMENT).innerHTML += (word.shift());
		} else {
			deletingEffect();
			return false;
		};
		timer = setTimeout(loopTyping, TYPE_DELAY);
	};
	loopTyping();
};

function deletingEffect() {
	let word = words[i].split("");
	var loopDeleting = function() {
		if (word.length > 0) {
			word.pop();
			document.getElementById(TARGET_ELEMENT).innerHTML = word.join("");
		} else {
			if (words.length > (i + 1)) {
				i++;
			} else {
				i = 0;
			};
			typingEffect();
			return false;
		};
		timer = setTimeout(loopDeleting, DELETE_DELAY);
	};
	loopDeleting();
};

// function blinkingCursor() {
//     let cursor = "|";

//     var loopBlinking = function() {
//         if (cursor === "|") {
//             cursor = "";
//         } else {
//             cursor = "|";
//         }
//         document.getElementById(TARGET_ELEMENT).innerHTML = cursor;
//         timer = setTimeout(loopBlinking, TYPE_DELAY);
//     };
//     loopBlinking();
// };
        
typingEffect();