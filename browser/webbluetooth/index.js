console.log('Web Bluetooth example');

let bluetooth = null;
let state = null;

const service_uuid = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E";
const tx_charactaristics_uuid = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E";
const rx_charactaristics_uuid = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E";

document.addEventListener("DOMContentLoaded", (event) => {
    console.log("Initialize");

    if ("bluetooth" in navigator){
        bluetooth = navigator.bluetooth;
    } else {
        alert("Web Bluetooth is not supported by your browser.");
        return;
    }

    state = {
        target_device: null,
        device_name_element: document.getElementById("device_name"),
        service_uuid_element: document.getElementById("service_uuid"),
        tx_characteristics_element: document.getElementById("tx_characteristics"),
        rx_characteristics_element: document.getElementById("rx_characteristics"),
    }
    state.service_uuid_element.value = service_uuid;
    state.tx_characteristics_element.value = tx_charactaristics_uuid;
    state.rx_characteristics_element.value = rx_charactaristics_uuid;
});

async function choose_device() {
    console.log("choose_device");
    try{
        state.target_device = await bluetooth.requestDevice({acceptAllDevices: true});
        console.log(state.target_device);
    } catch (error){
        console.log(error);
        state.device_name_element.value = null;
        return;
    }
    state.device_name_element.value = state.target_device.name;
}

async function send_to_device(){
    console.log('send_to_device');
}
