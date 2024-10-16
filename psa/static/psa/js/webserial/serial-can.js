let portOpen = false; // tracks whether a port is corrently open
let portPromise; // promise used to wait until port succesfully closed
let holdPort = null; // use this to park a SerialPort object when we change settings so that we don't need to ask the user to select it again
let port; // current SerialPort object
let reader; // current port reader object so we can call .cancel() on it to interrupt port reading
let openclosePort= document.getElementById("openclose_port");
const usbVendorId = 0x0D28;
let idCan = document.getElementById("idCan");
let dlcCan = document.getElementById("dlcCan");
let dataCan = document.getElementById("dataCan");
let sendBtn = document.getElementById("sendBtn");

async function sleep(ms) {
  return new Promise((resolve) =>setTimeout(resolve, ms));
}

// Do these things when the window is done loading
window.onload = function () {
  // Check to make sure we can actually do serial stuff
  if ("serial" in navigator) {
    // The Web Serial API is supported.
    // Connect event listeners to DOM elements
    openclosePort.addEventListener("click", openClose);
    sendBtn.addEventListener("click", sendDataCan);

  } else {
    // The Web Serial API is not supported.
    // Warn the user that their browser won't do stupid serial tricks
    alert("The Web Serial API is not supported by your browser");
  }
};

// This function is bound to the "Open" button, which also becomes the "Close" button
// and it detects which thing to do by checking the portOpen variable
async function openClose() {
  // Is there a port open already?
  if (portOpen) {
    // Port's open. Call reader.cancel() forces reader.read() to return done=true
    // so that the read loop will break and close the port
    reader.cancel();
    console.log("attempt to close");
  } else {
    // No port is open so we should open one.
    // We write a promise to the global portPromise var that resolves when the port is closed
    portPromise = new Promise((resolve) => {
      // Async anonymous function to open the port
      (async () => {
        // Check to see if we've stashed a SerialPort object
        if (holdPort == null) {
          // If we haven't stashed a SerialPort then ask the user to select one
          port = await navigator.serial.requestPort({ filters: [{ usbVendorId }] });
        } else {
          // If we have stashed a SerialPort then use it and clear the stash
          port = holdPort;
          holdPort = null;
        }
        // Open the serial port with the selected baud rate
        await port.open({ baudRate: 115200});

        // Create a textDecoder stream and get its reader, pipe the port reader to it
        const textDecoder = new TextDecoderStream();
        reader = textDecoder.readable.getReader();
        const readableStreamClosed = port.readable.pipeTo(textDecoder.writable);

        // If we've reached this point then we're connected to a serial port
        // Set a bunch of variables and enable the appropriate DOM elements
        portOpen = true;
        openclosePort.innerText = "Disconnect";
        openclosePort.classList.replace("btn-secondary", "btn-success");
        idCan.disabled = false;
        dlcCan.disabled = false;
        dataCan.disabled = false;
        sendBtn.disabled = false;

        // NOT SUPPORTED BY ALL ENVIRONMENTS
        // Get port info and display it to the user in the port_info span
        let portInfo = port.getInfo();
        console.log("Connected to device with VID " + portInfo.usbVendorId + " and PID " + portInfo.usbProductId);

        // Serial read loop. We'll stay here until the serial connection is ended externally or reader.cancel() is called
        // It's OK to sit in a while(true) loop because this is an async function and it will not block while it's await-ing
        // When reader.cancel() is called by another function, reader will be forced to return done=true and break the loop
        try {
          while (true) {
            const {value, done} = await reader.read();
            if (done) {
              // |reader| has been canceled.
              break;
            }
            // console.log(value);
          }
        } catch (error) {
          // TODO: Handle non-fatal read error.
          console.log(error);
        } finally {
          reader.releaseLock();
        }

        // If we've reached this point then we're closing the port
        // first step to closing the port was releasing the lock on the reader
        // we did this before exiting the read loop.
        // That should have broken the textDecoder pipe and propagated an error up the chain
        // which we catch when this promise resolves
        await readableStreamClosed.catch(() => {
          /* Ignore the error */
        });
        // Now that all of the locks are released and the decoder is shut down, we can close the port
        await port.close();

        // Set a bunch of variables and disable the appropriate DOM elements
        portOpen = false;
        openclosePort.innerText = "Connect";
        openclosePort.classList.replace("btn-success", "btn-secondary");
        idCan.disabled = true;
        dlcCan.disabled = true;
        dataCan.disabled = true;
        sendBtn.disabled = true;

        console.log("port closed");

        // Resolve the promise that we returned earlier. This helps other functions know the port status
        resolve();
      })();
    });
  }
}

async function sendString(value) {
  console.log(value);

  // Get a text encoder, pipe it to the SerialPort object, and get a writer
  const textEncoder = new TextEncoderStream();
  const writableStreamClosed = textEncoder.readable.pipeTo(port.writable);
  const writer = textEncoder.writable.getWriter();

  // write the outString to the writer
  await writer.write(value + "\r\n");

  // close the writer since we're done sending for now
  await writer.close();
  await writableStreamClosed;
  await sleep(10);
}


async function sendDataCan() {

  if (dataCan.value.match(/^B[0-7].\d{2}$/))
  {
    let data = dataCan.value.split('.');
    let data_list = [];
    for (let i = 0; i < dlcCan.value; i++) {
      if (i === parseInt(data[0][1])) {
        data_list.push("0x" + data[1]);
      } else if (i === 6) {
        data_list.push("0x" + VOL_NB.toString(16));
      } else data_list.push("0x00");
    }
    let outString = "WS+GETCAN=" + idCan.value + "," + data_list.join(',');
    console.log(outString);

    // Get a text encoder, pipe it to the SerialPort object, and get a writer
    const textEncoder = new TextEncoderStream();
    const writableStreamClosed = textEncoder.readable.pipeTo(port.writable);
    const writer = textEncoder.writable.getWriter();

    // write the outString to the writer
    await writer.write(outString + "\r\n");

    // close the writer since we're done sending for now
    await writer.close();
    await writableStreamClosed;
    await sleep(10);
  } else alert("Mauvais format de donnée !");
}
