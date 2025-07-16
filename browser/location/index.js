console.log('Location example');

const state = {};

state.initial_view_state = {
    longitude: 0,
    latitude: 0,
    zoom: 15,
    pitch: 0,
    bearing: 0,
};

state.locationHistory = [];

function getLayers(){
    const tileLayer = new deck.TileLayer({
        data: "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
        minZoom: 0,
        maxZoom: 19,
        tileSize: 256,
        renderSubLayers: props => {
            return [
            new deck.BitmapLayer(props, {
                data: null,
                image: props.data,
                bounds: [props.tile.bbox.west, props.tile.bbox.south, props.tile.bbox.east, props.tile.bbox.north]
            })
            ];
        },
    });

    const locationHistoryLayer = new deck.ScatterplotLayer({
        id: 'LocationHistoryLayer',
        data: state.locationHistory,
        getPosition: d => d.position,
        getRadius: d => d.accuracy,

        stroked: true,

        getFillColor: [255, 0, 0, 64],

        getLineColor: [0, 0, 0, 64],
        getLineWidth: 10,
    });
    return [tileLayer, locationHistoryLayer];
};

document.addEventListener("DOMContentLoaded", (event) => {
    console.log("Initialize");

    const button = document.getElementById('getLocation');
    button.addEventListener('click', getLocation);

    if ("geolocation" in navigator){
        state.geolocation = navigator.geolocation;
    } else {
        alert("GeoLocation is not supported by your browser.");
        return;
    }

    state.message = document.getElementById("message");
    state.location = {longitude: 0, latitude: 0};
    state.watchPositionId = null;

    state.deckgl = new deck.DeckGL({
        container: "map_container",
        initialViewState: state.initial_view_state,
        controller: true,
    });

    getLocation();
});

function getLocation(){
    if (state.watchPositionId != null){
        state.geolocation.clearWatch(state.watchPositionId);
        state.watchPositionId = null;
        console.log("watchposition cleared")
    }

    state.watchPositionId = state.geolocation.watchPosition(function(position){
        state.message.value += "\nCurrent time: " + new Date().toLocaleTimeString() + " Latitude: " + position.coords.latitude + " Longitude: " + position.coords.longitude + " Accuracy: " + position.coords.accuracy
        state.location.longitude = position.coords.longitude;
        state.location.latitude = position.coords.latitude;

        const curentPosition = {
            position: [position.coords.longitude, position.coords.latitude, position.coords.altitude],
            accuracy: position.coords.accuracy
        };
        state.locationHistory.push(curentPosition);

        state.deckgl.setProps({
            initialViewState: {
                ...state.initial_view_state,
                longitude: position.coords.longitude,
                latitude: position.coords.latitude,
            },
            layers: getLayers()
        });

    }, function(error){console.log(error)});
}
