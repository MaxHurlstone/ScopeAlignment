var needsToDo = true;
var output    = document.querySelector('.output');

const socket = io({secure:true});

socket.on("connect", () => {
      console.log("Connected!");
});
socket.on("disconnect", () => {
      console.log("Lost connection to the server.");
});

var a = 0;
var b = 0;
var x = 0;
var y = 0;
var z = 0;

async function handleOrientation(event) {

    a = event.alpha;  //z orientation
    b = event.beta;   //y orientation

    socket.emit("OrientationData", {"a":a, "b":b})

    output.innerHTML = "alpha: " + a + "\nbeta: " + b + "\nx: " + z + "\ny: " + y + "\nz: " + z
    // output.innerHTML += "gamma: " + x + "\n";
    //output.innerHTML += "\nbeta: " + b + "abs: " + abs

}

async function handleMotion(event) {

    x = event.acceleration.x;  //z orientation
    y = event.acceleration.y;
    z = event.acceleration.z;

    gx = event.accelerationIncludingGravity.x;  //z orientation
    gy = event.accelerationIncludingGravity.y;
    gz = event.accelerationIncludingGravity.z;   //y orientation

    socket.emit("MotionData", {"x":x, "y":y, "z":z, "gx":gx, "gy":gy, "gz":gz})

    //output.innerHTML += "\nx: " + z + "\ny: " + y + "\nz: " + z
    // output.innerHTML += "gamma: " + x + "\n";
    //utput.innerHTML += "\nbeta: " + b + "abs: " + abs

}



function onClick(event) {

  if(needsToDo){
      console.log("click occured");

      if (typeof DeviceOrientationEvent.requestPermission === 'function') {
          DeviceOrientationEvent.requestPermission()
          .then(permissionState => {
              if (permissionState === 'granted') {
                  console.log("Permission granted");
                  window.addEventListener('deviceorientation', handleOrientation);
              }
          })
          .catch(console.error);
          }
      else {
          console.log("on laptop");
          window.addEventListener('deviceorientation', handleOrientation);
          // handle regular non iOS 13+ devices

      }

      if (typeof DeviceMotionEvent.requestPermission === 'function') {
          DeviceMotionEvent.requestPermission()
          .then(permissionState => {
              if (permissionState === 'granted') {
                  console.log("Permission granted");
                  window.addEventListener('devicemotion', handleMotion);
              }
          })
          .catch(console.error);
          }
      else {
          console.log("on laptop");
          window.addEventListener('devicemotion', handleMotion);
          // handle regular non iOS 13+ devices

      }
    needsToDo=false;
    }
}


window.addEventListener("click", onClick);
