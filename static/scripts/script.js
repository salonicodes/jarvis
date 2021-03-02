/*By Saloni Tripathi*/
dict = { assistant: true, listening: false, icon: false, speaking: false };

function hide(obj) {
  var e1 = document.getElementsByClassName(obj)[0];
  e1.style.display = "none";
  dict[obj] = false;
}

function show(obj) {
  var e1 = document.getElementsByClassName(obj)[0];
  e1.style.display = "block";
  for (var key in dict) {
    if (dict[key]) {
      hide(key);
    }
  }
  dict[obj] = true
}

async function getAns(que) {
  var test = [que];
  var ans = "";
  ans = $.ajax({
    url: "/answer",
    data: { uque: JSON.stringify(test) },
    dataType: "json",
    type: "get",
    success: function (response) {
      //console.log(response)
    },
    error: function (error) {
      console.log(error);
    },
  });
  return ans;
}

async function userAsking() {
  await forSpeaking("Hey there, how may I help you today?");
  let query = await forListening();
  return query;
}

async function forSpeaking(whatToSpeak) {
  show("speaking");
  speak(whatToSpeak);
  return;
}

async function forLoading() {
  show("icon");
  return;
}

async function forListening() {
  show("listening");
  var listened = listen();
  return listened;
}

function forOrigin() {
  show("assistant");
  speak("Hey");
}

function speak(text) {
  if ("speechSynthesis" in window) {
    show("speaking")
    // Speech Synthesis supported
    var msg = new SpeechSynthesisUtterance();
    msg.text = text;
    msg.lang = "en";
    msg.volume = 1; // From 0 to 1
    msg.rate = 1; // From 0.1 to 10
    var texts = document.querySelector(".texts");
    texts.innerText = text;
    if(text.length>50) {
        text = text.slice(0, 50)
        text.concat("...")
    }
    window.speechSynthesis.speak(msg);  

  } else {
    // Speech Synthesis Not Supported
    alert("Sorry, your browser doesn't support text to speech!");
  }
}

function listen() {
  // new speech recognition object
  var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition;
  var recognition = new SpeechRecognition();

  recognition.interimResults = true;
  var texts = document.querySelector(".texts");
  texts.innerHTML = "";

  recognition.addEventListener("result", async (e) => {
    const text = Array.from(e.results)
      .map((result) => result[0])
      .map((result) => result.transcript)
      .join("");

      console.log("Texter = ", text)
    texts.innerText = text;
    if (e.results[0].isFinal) {
        console.log("Final text = ", text)
      texts.innerText = text;
      var answer = await getAns(text)
        speak(answer)
        show('assistant')
    }
    return texts.innerText;
  });

  // This runs when the speech recognition service starts
  recognition.onstart = function () {
    console.log("We are listening. Try speaking into the microphone.");
  };

  recognition.onspeechend = function () {
    // when user is done speaking
    console.log("Done speaking")
    recognition.stop();
  };

  // This runs when the speech recognition service returns result
  recognition.onresult = async function (event) {
    var transcript = event.results[0][0].transcript;
    console.log("Transcript = ", transcript)
    forLoading()
    console.log("Printed after speaking!")
  };

  // start recognition
  setTimeout(() => {
    recognition.start();
  }, 5000);
  /* const texts = document.querySelector(".texts");
    window.SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
    
    const recognition = new SpeechRecognition();
    recognition.interimResults = true;
    
    let p = document.createElement("p");
    
    recognition.addEventListener("result", (e) => {
    texts.appendChild(p);
    const text = Array.from(e.results)
        .map((result) => result[0])
        .map((result) => result.transcript)
        .join("");
    
    p.innerText = text;
    if (e.results[0].isFinal) {
        p = document.createElement("p");
    }
    });
    
    recognition.addEventListener("end", () => {
    recognition.start();
    });
    
    recognition.start();*/
}
