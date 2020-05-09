// const io = require('socket.io-client');

var aim    = document.querySelector('.aim');
var target = document.querySelector('.target');
var garden     = document.querySelector('.garden');
var output     = document.querySelector('.output');

var maxX = garden.clientWidth  - aim.clientWidth;
var maxY = garden.clientHeight - aim.clientHeight;

var initY = 0;
var initZ = 0;

var driftY = 0;
var driftX = 0;

var onRight = false
var Exposure = false;

var y = 0;
var x = 0;
var z = 0;

var deltaPos = 0

var fovy = 0.5; //180;
var fovx = 0.5; //360;

target.style.top = (maxY*90/180 - 15) + "px";
target.style.left = (maxX*180/360 - 15) + "px";

aim.style.top = (maxY*1/2 - 10) + "px";
aim.style.left = (maxX*1/2 - 10) + "px";

var needsToDo = true;


const socket = io({secure:true});

socket.on("connect", () => {
      console.log("Connected!");
});
socket.on("disconnect", () => {
      console.log("Lost connection to the server.");
});
socket.on("ExposureComplete", () => {
    console.log("Server telling us exposure is complete");
    Exposure = false;
    // initY = 0;
    // initZ = 0;
    y +=  driftY; //deltaPos["deltaAlt"];
    z -= driftX;
});
socket.on("DataUpdate", (data) => {
    console.log(data);

    handlePosDuringExposure(data);

    // deltaPos = data
    // console.log(data);
    //
    // driftY += deltaPos["deltaAlt"];
    // driftX += deltaPos["deltaAz"];
    //
    // y -=  driftY; //deltaPos["deltaAlt"];
    //
    // if (z > (fovx/2) & z < fovx){onRight = true;}
    // if (z+initZ > 0 & z < (fovx/2)){onRight = false;}
    //
    // if (onRight) {
    //     z = z-fovx;
    // }
    //
    // z += driftX; //deltaPos["deltaAz"];
    //
    // // console.log(y);
    // // console.log(z);
    //
    // aim.style.top  = (maxY*((fovy/2)-y)/(fovy) - 10) + "px"; //(maxY*0.5) - 10 + "px";
    // aim.style.left = (maxX*((fovx/2)-z)/fovx - 10) + "px"; // (maxX*0.5) - 10 + "px";
});

async function handlePosDuringExposure(data){
    deltaPos = data;
    driftY += deltaPos["deltaAlt"];
    driftX += deltaPos["deltaAz"];

    // if (z > (fovx/2) & z < fovx){onRight = true;}
    // if (z+initZ > 0 & z < (fovx/2)){onRight = false;}
    //
    // if (onRight) {
    //     z = z-fovx;
    // }

    y -=  driftY; //deltaPos["deltaAlt"];
    z += driftX; //deltaPos["deltaAz"];

    // console.log(y);
    // console.log(z);

    // aim.style.top  = (maxY*((fovy/2)-y)/(fovy) - 10) + "px"; //(maxY*0.5) - 10 + "px";
    // aim.style.left = (maxX*((fovx/2)-z)/fovx - 10) + "px"; // (maxX*0.5) - 10 + "px";
}


async function handleOrientation(event) {

    // if  (Exposure) {
    //     console.log("not runnning");
    //
    //     a = event.alpha;
    //     b = event.beta;
    //
    //     output.innerHTML = "alpha: " + a + "\nz: " + z + "\n";
    //     // output.innerHTML += "gamma: " + x + "\n";
    //     output.innerHTML += "beta: " + y + "\ny: " + y + "\n";
    //
    //     y = b-initY;
    //     // x = event.gamma;
    //     z = a-initZ;
    //
    //     if (z > (fovx/2) & z < fovx){onRight = true;}
    //     if (z+initZ > 0 & z < (fovx/2)){onRight = false;}
    //
    //     if (onRight) {
    //         z = z-fovx;
    //     }
    //
    //     aim.style.top  = (maxY*((fovy/2)-y)/(fovy) - 10) + "px"; //(maxY*0.5) - 10 + "px";
    //     aim.style.left = (maxX*((fovx/2)-z)/fovx - 10) + "px"; // (maxX*0.5) - 10 + "px";
    // }

    // else{
        a = event.alpha;
        b = event.beta;


        output.innerHTML = "alpha: " + a + "\nz: " + z + "\n";
        // output.innerHTML += "gamma: " + x + "\n";
        output.innerHTML += "beta: " + y + "\ny: " + y + "\n";

        y = b-initY;
        // x = event.gamma;
        z = a-initZ;

        // socket.emit('orientation', {zval:y, xval:x, yval:y});

        if (z > (fovx/2) & z < fovx){onRight = true;}
        if (z+initZ > 0 & z < (fovx/2)){onRight = false;}

        if (onRight) {
            z = z-fovx;
        }

        // y -= initY;
        // z -= initZ;


        aim.style.top  = (maxY*((fovy/2)-y)/(fovy) - 10) + "px"; //(maxY*0.5) - 10 + "px";
        aim.style.left = (maxX*((fovx/2)-z)/fovx - 10) + "px"; // (maxX*0.5) - 10 + "px";
    // }
}



function onClick(event) {

  if(needsToDo){console.log("click occured");

      if (typeof DeviceOrientationEvent.requestPermission === 'function') {
          DeviceOrientationEvent.requestPermission()
          .then(permissionState => {
              if (permissionState === 'granted') {
                  console.log("Permission granted");
                  window.addEventListener('deviceorientation', handleOrientation);
              }
          })
          .catch(console.error);
          } else {
              console.log("on laptop");
              window.addEventListener('deviceorientation', handleOrientation);
              // handle regular non iOS 13+ devices

      }
    needsToDo=false;}
}



function sendUserInput(){
    console.log($('form').serialize());
    socket.emit("userInput", {userInput:$('form').serialize()});
    return false;
}

function startExp(){
    Exposure = true;
    console.log("Exposure started");
    socket.emit("dataRequest", {});
    initY = b;
    initZ = a;

    // y = b-initY;
    // // x = event.gamma;
    // z = a-initZ;
    //
    // // socket.emit('orientation', {zval:y, xval:x, yval:y});
    //
    // if (z > (fovx/2) & z < fovx){onRight = true;}
    // if (z+initZ > 0 & z < (fovx/2)){onRight = false;}
    //
    // if (onRight) {
    //     z = z-fovx;
    // }
}

function reset(){
    console.log("Zeroed at target");
    // socket.emit("abort", {});
    initY = b;
    initZ = a;
}



window.addEventListener("click", onClick);
