console.log('Location example');

const state = {};

state.initial_view_state = {
    longitude: 0,
    latitude: 0,
    zoom: 10,
    pitch: 0,
    bearing: 0,
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

    state.deckgl = new deck.DeckGL({
        container: "map_container",
        initialViewState: state.initial_view_state,
        controller: true,
        layers: [tileLayer,]
    });

});

function getLocation(){
    state.geolocation.watchPosition(function(position){
        state.message.value += "\nCurrent time: " + new Date().toLocaleTimeString() + " Latitude: " + position.coords.latitude + " Longitude: " + position.coords.longitude + " Accuracy: " + position.coords.accuracy
        state.location.longitude = position.coords.longitude;
        state.location.latitude = position.coords.latitude;
        state.deckgl.setProps({
            initialViewState: {
                ...state.initial_view_state,
                longitude: position.coords.longitude,
                latitude: position.coords.latitude,
            },
        });
        state.deckgl.redraw(true);
    }, function(error){console.log(error)});
}
